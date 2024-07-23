import pymysql
import configparser
import sys
import json

if len(sys.argv) < 3:
    print("Usage: python script.py <config_file> any")
    sys.exit(1)

config_file = sys.argv[1]
# specific_task_id = sys.argv[2]

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

# 读取link.txt文件
def read_link_file(file_path):
    links = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')
            if len(parts) == 2:
                task_from = parts[0]
                task_to_list = parts[1].split(',')
                links.append((task_from, task_to_list))
    return links

# 查询数据库
def query_database(task_from, task_to_list, connection):
    placeholders = ', '.join(['%s'] * len(task_to_list))
    query = f"""
    SELECT 
        t1.task_id AS task_from,
        t1.status AS task_from_status,
        t1.tenant_id AS task_from_tenant_id,
        t1.cycle_unit AS task_from_cycle_unit,
        t2.task_id AS task_to,
        t2.status AS task_to_status,
        t2.tenant_id AS task_to_tenant_id,
        t2.cycle_unit AS task_to_cycle_unit
    FROM 
        lb_task_latest_version t1
    JOIN 
        task_version_link_info link ON t1.task_id = link.task_from
    JOIN 
        lb_task_latest_version t2 ON link.task_to = t2.task_id
    WHERE 
        link.task_from = %s AND link.task_to IN ({placeholders})
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [task_from] + task_to_list)
        results = cursor.fetchall()
    return results

# 查询 pre_dependence_config
def query_pre_dependence_config(task_id, connection):
    query = """
    SELECT 
        JSON_UNQUOTE(JSON_EXTRACT(task_info, '$.taskExt.properties.pre_dependence_config')) AS pre_dependence_config
    FROM 
        task_version_info
    WHERE 
        task_id = %s
        AND used_version = 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
    return result['pre_dependence_config'] if result else None
from datetime import datetime
# 主函数
def main():
    file_path = 'link.txt'
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file_path = f"link_args_output_{timestamp}.txt"

    # 连接数据库
    connection = pymysql.connect(**db_config_open)

    try:
        with open(output_file_path, 'w') as output_file:
            # 读取link.txt文件中的记录并查询数据库
            for task_from, task_to_list in read_link_file(file_path):
                # 打印link.txt文件中的记录
                output_file.write(f"Task From: {task_from}, Task To List: {', '.join(task_to_list)}\n")

                # 查询数据库并打印结果
                results = query_database(task_from, task_to_list, connection)
                for result in results:
                    output_file.write(
                        f"--Task From: {result['task_from']}, "
                        f"( {result['task_from_status']} "
                        f", {result['task_from_cycle_unit']} )"
                        f" To: {result['task_to']}, "
                        f"( {result['task_to_status']} "
                        f", {result['task_to_cycle_unit']} )"
                        f"Tenant Id: {result['task_to_tenant_id']}\n"
                    )
                    # 检查 Task From 和 Task To 的状态
                    if result['task_from_status'] != 'Y' or result['task_to_status'] != 'Y':
                        output_file.write(f"error: Task From {result['task_from']} or Task To {result['task_to']} status is not 'Y'\n")
                    # 查询 pre_dependence_config
                    pre_dependence_config = query_pre_dependence_config(result['task_to'], connection)
                    if pre_dependence_config:
                        try:
                            config_list = json.loads(pre_dependence_config).get('configList', [])
                            matched = False
                            for config in config_list:
                                # 打印config的内容以调试
                                if isinstance(config, dict) and config.get('taskId') == result['task_from']:
                                    # 检查 cycle_unit 和 value
                                    if result['task_from_cycle_unit'] == 'D' and result['task_to_cycle_unit'] == 'D' and config.get('value') == 'CD':
                                        output_file.write(f"--Matched Config: {config}\n")
                                    elif result['task_from_cycle_unit'] == 'H' and result['task_to_cycle_unit'] == 'H' and config.get('value') == 'CH':
                                        output_file.write(f"--Matched Config: {config}\n")
                                    elif result['task_from_cycle_unit'] == 'M' and result['task_to_cycle_unit'] == 'M' and config.get('value') == 'CM':
                                        output_file.write(f"--Matched Config: {config}\n")
                                    elif result['task_from_cycle_unit'] == 'C' and result['task_to_cycle_unit'] == 'C' and config.get('value') == 'CT':
                                        output_file.write(f"--Matched Config: {config}\n")
                                    else:
                                        output_file.write(f"WARN: Task From {result['task_from']} and Task To {result['task_to']} cycle units or config value do not Matched Config: {config}\n")
                                    matched = True
                                    break  # 只输出第一个匹配的结果
                            if not matched:
                                output_file.write(
                                    f"error: No matching config found for Task From {result['task_from']} in Task To {result['task_to']}\n")
                        except json.JSONDecodeError:
                            output_file.write(f"--Error decoding JSON for task_to: {result['task_to']}\n")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
