import configparser
import mysql.connector
from mysql.connector import Error
import sys
import pymysql

if len(sys.argv) < 3:
    print("Usage: python script.py <config_file> tenant_id task_id")
    sys.exit(1)

config_file = sys.argv[1]
specific_tenant_id = sys.argv[2]
specific_task_id = sys.argv[3]
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

# 连接到 open 数据库
try:
    open_connection = pymysql.connect(**db_config_open)
    print("成功连接到 open 数据库")
except pymysql.MySQLError as e:
    print(f"连接到 open 数据库时出错: {e}")

# 更新 open 数据库中的记录
try:
    with open_connection.cursor() as cursor:
        print("force update ",specific_tenant_id,specific_task_id)
        update_query = """
        UPDATE lb_task_run
        SET state = 8
        WHERE exec_engine = 'unified_scheduler' and state NOT IN (2, 8) and tenant_id=%s and task_id = %s
        """
        cursor.execute(update_query, (specific_tenant_id,specific_task_id))
        open_connection.commit()
except pymysql.MySQLError as e:
    print(f"更新 open 数据库时出错: {e}")

# 关闭连接
finally:
    if open_connection:
        open_connection.close()
        print("已关闭 open 数据库连接")
