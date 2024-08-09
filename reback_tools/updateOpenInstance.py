import configparser
import mysql.connector
from mysql.connector import Error
import sys
import pymysql

if len(sys.argv) < 2:
    print("Usage: python script.py <config_file> tenant_id")
    sys.exit(1)

config_file = sys.argv[1]
specific_tenant_id = sys.argv[2]
# 读取配置文件
config = configparser.ConfigParser()
config.read(config_file)

# 从配置文件获取数据库配置
# 从配置文件获取数据库配置
db_config_open = {
    'host': config['open-write']['host'],
    'user': config['open-write']['user'],
    'password': config['open-write']['password'],
    'db': config['open-write']['db'],
    'charset': config['open-write']['charset'],
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


# 连接到 unified 数据库
try:
    unified_connection = pymysql.connect(**db_config_unified)
    print("成功连接到 unified 数据库")
except pymysql.MySQLError as e:
    print(f"连接到 unified 数据库时出错: {e}")

# 连接到 open 数据库
try:
    open_connection = pymysql.connect(**db_config_open)
    print("成功连接到 open 数据库")
except pymysql.MySQLError as e:
    print(f"连接到 open 数据库时出错: {e}")

# 查询 unified 数据库中的符合条件的记录
unified_tasks = []
try:
    with unified_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        query = """
        SELECT task_id, cur_run_date, exec_engine, state
        FROM lb_task_run
        WHERE exec_engine = 'unified_scheduler' AND state IN (2, 8) and tenant_id=%s
        """
        cursor.execute(query,(specific_tenant_id))
        unified_tasks = cursor.fetchall()
except pymysql.MySQLError as e:
    print(f"查询 unified 数据库时出错: {e}")

# 更新 open 数据库中的记录
try:
    with open_connection.cursor() as cursor:
        for task in unified_tasks:
            query = """
            SELECT task_id, cur_run_date, exec_engine, state
            FROM lb_task_run
            WHERE task_id = %s AND cur_run_date = %s AND exec_engine = 'unified_scheduler' AND state NOT IN (2, 8) and tenant_id=%s
            """
            cursor.execute(query, (task['task_id'], task['cur_run_date'],specific_tenant_id))
            open_task = cursor.fetchone()

            if open_task:
                print("update ",task['task_id'], "_", task['cur_run_date'])
                update_query = """
                UPDATE lb_task_run
                SET state = 8
                WHERE tenant_id=%s and task_id = %s AND cur_run_date = %s
                """
                cursor.execute(update_query, (task['task_id'], task['cur_run_date'],specific_tenant_id))

        open_connection.commit()
except pymysql.MySQLError as e:
    print(f"更新 open 数据库时出错: {e}")

# 关闭连接
finally:
    if unified_connection:
        unified_connection.close()
        print("已关闭 unified 数据库连接")

    if open_connection:
        open_connection.close()
        print("已关闭 open 数据库连接")
