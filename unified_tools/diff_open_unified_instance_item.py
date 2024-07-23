import pymysql
from datetime import datetime
import configparser
import sys

if len(sys.argv) < 3:
    print("Usage: python3 script.py <config_file> tenantId startTime endTime")
    sys.exit(1)

config_file = sys.argv[1]
specific_tenant_id = sys.argv[2]
specific_from = sys.argv[3]
specific_to = sys.argv[4]

# 读取配置文件
config = configparser.ConfigParser()
config.read(config_file)

# 从配置文件获取数据库配置
db_config_open = {
    'host': config['open']['host'],
    'user': config['open']['user'],
    'password': config['open']['password'],
    'db': config['open']['db'],
    'charset': config['open']['charset'],
    'cursorclass': pymysql.cursors.DictCursor
}

db_config_unified = {
    'host': config['unified']['host'],
    'user': config['unified']['user'],
    'password': config['unified']['password'],
    'db': config['unified']['db'],
    'charset': config['unified']['charset'],
    'cursorclass': pymysql.cursors.DictCursor
}

# 查询数据库
def query_database(connection, tenant_id, start_time, end_time):
    query = """
    SELECT 
        task_id, cur_run_date, next_run_date, state, exec_engine, do_flag, redo_flag, tries, try_limit, execution_space, resource_group, product_name, tenant_id
    FROM 
        lb_task_run
    WHERE 
        tenant_id = %s AND exec_engine='unified_scheduler' AND cur_run_date BETWEEN %s AND %s
    """
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, (tenant_id, start_time, end_time))
        results = cursor.fetchall()
    return results


# 检查记录是否在 lb_task_run 中不存在但在 lb_task_run_bak 中存在
def check_record_in_open_bak(connection, task_id, cur_run_date):
    query_lb_task_run = """
    SELECT 1 FROM lb_task_run WHERE task_id = %s AND cur_run_date = %s
    """
    query_lb_task_run_bak = """
    SELECT 1 FROM lb_task_run_bak WHERE task_id = %s AND cur_run_date = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_lb_task_run, (task_id, cur_run_date))
        result_lb_task_run = cursor.fetchone()

        if result_lb_task_run is None:
            cursor.execute(query_lb_task_run_bak, (task_id, cur_run_date))
            result_lb_task_run_bak = cursor.fetchone()
            return result_lb_task_run_bak is not None
    return False

# 统计差异个数
def count_differences(extra_records):
    count_dict = {}
    for record in extra_records:
        task_id = record['task_id']
        if task_id in count_dict:
            count_dict[task_id] += 1
        else:
            count_dict[task_id] = 1
    return count_dict

# 比较两个数据库中的记录
def compare_records(open_records, unified_records):
    open_dict = {(record['task_id'], record['cur_run_date']): record for record in open_records}
    unified_dict = {(record['task_id'], record['cur_run_date']): record for record in unified_records}

    open_extra = []
    unified_extra = []

    for key in open_dict:
        if key not in unified_dict:
            open_extra.append(open_dict[key])

    for key in unified_dict:
        if key not in open_dict:
            unified_extra.append(unified_dict[key])

    return open_extra, unified_extra

# 保存结果到文件
def save_results(open_extra, unified_extra,connection_open):
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # 统计差异个数
    open_count = count_differences(open_extra)
    unified_count = count_differences(unified_extra)

    task_id_statistics = f"task_id_statistics_{timestamp}.txt"
    # 保存统计结果
    with open(task_id_statistics, 'w') as file:
        file.write('Task ID, Open Extra Count, Unified Extra Count\n')
        all_task_ids = sorted(set(open_count.keys()).union(set(unified_count.keys())), reverse=True)
        for task_id in all_task_ids:
            open_count_value = open_count.get(task_id, 0)
            unified_count_value = unified_count.get(task_id, 0)
            file.write(f'{task_id}, {open_count_value}, {unified_count_value}\n')
    print(f"Tenant task id diff statistics {task_id_statistics}")

    # 保存 open 缺失记录详情
    open_extra_details = f"open_extra_details_{timestamp}.txt"
    with open(open_extra_details, 'w') as file:
        for record in sorted(open_extra, key=lambda x: x['task_id'], reverse=True):
            file.write(f"{record['task_id']},{record['cur_run_date']},{record['next_run_date']},{record['next_run_date']}\n")

    print(f"Tenant open extra details {open_extra_details}")

    # 保存 unified 缺失记录详情
    unified_extra_details = f"unified_extra_details_{timestamp}.txt"
    with open(unified_extra_details, 'w') as file:
        for record in sorted(unified_extra, key=lambda x: x['task_id'], reverse=True):
            file.write(f"{record['task_id']},{record['cur_run_date']},{record['product_name']}\n")

    print(f"Tenant unified extra details {unified_extra_details}")

    delete_unified_extra_details = f"delete_unified_extra_details_{timestamp}.txt"
    # 检查 unified 多余记录是否在 open 数据库中存在
    with open(delete_unified_extra_details, 'w') as file:
        for record in unified_extra:
            if check_record_in_open_bak(connection_open, record['task_id'], record['cur_run_date']):
                file.write(f"{record['task_id']},{record['cur_run_date']},{record['product_name']}\n")
    print(f"Tenant delete unified extra details {delete_unified_extra_details}")
# 主函数
def main(tenant_id, start_time, end_time):
    # 连接数据库
    connection_open = pymysql.connect(**db_config_open)
    connection_unified = pymysql.connect(**db_config_unified)

    try:
        # 查询数据库
        open_records = query_database(connection_open, tenant_id, start_time, end_time)
        unified_records = query_database(connection_unified, tenant_id, start_time, end_time)

        # 比较记录
        open_extra, unified_extra = compare_records(open_records, unified_records)

        # 保存结果到文件
        save_results(open_extra, unified_extra,connection_open)
    finally:
        connection_open.close()
        connection_unified.close()

if __name__ == '__main__':
    print(f"check tenant {specific_tenant_id} from {specific_from} to {specific_to} ")
    main(specific_tenant_id, specific_from, specific_to)