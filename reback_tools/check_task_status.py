import pandas as pd
import mysql.connector
from mysql.connector import Error
import configparser
import pymysql

def fetch_data_from_db(connection):
    try:
        query = """
        SELECT tenant_id, task_id, status 
        FROM lb_task 
        WHERE status IN ('Y', 'F', 'O', 'INVALID')
        """
        return pd.read_sql(query, connection)
    except Error as e:
        print(f"Error: {e}")


def compare_data(unified_df, open_df):
    # Merge dataframes on tenant_id and task_id
    merged_df = pd.merge(unified_df, open_df, on=['tenant_id', 'task_id'], how='outer', suffixes=('_unified', '_open'))

    # Find records that are in unified but not in open
    only_in_unified = merged_df[merged_df['status_open'].isnull()][['tenant_id', 'task_id', 'status_unified']]
    only_in_unified['status_open'] = None

    # Find records that are in open but not in unified
    only_in_open = merged_df[merged_df['status_unified'].isnull()][['tenant_id', 'task_id', 'status_open']]
    only_in_open['status_unified'] = None

    # Find records that are in both but have different statuses
    different_status = merged_df[merged_df['status_unified'] != merged_df['status_open']][['tenant_id', 'task_id', 'status_unified', 'status_open']]

    return only_in_unified, only_in_open, different_status

def write_to_file(df, filename):
    # 将 DataFrame 写入文本文件
    with open(filename, 'w') as f:
        f.write(df.to_string(index=False))

import sys
def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <config_file> tenantId outName")
        sys.exit(1)

    config_file = sys.argv[1]
    outputName = sys.argv[2]

    # Database connection details
    config = configparser.ConfigParser()
    config.read(config_file)

    db_config_unified = {
        'host': config['unified']['host'],
        'user': config['unified']['user'],
        'password': config['unified']['password'],
        'db': config['unified']['db'],
        'charset': config['unified']['charset'],
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 连接数据库
    try:
        # 连接到数据库实例1
        connection_unified = pymysql.connect(**db_config_unified)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

    unified_data = fetch_data_from_db(connection_unified)
    # 从配置文件获取数据库配置
    db_config_open = {
        'host': config['open']['host'],
        'user': config['open']['user'],
        'password': config['open']['password'],
        'db': config['open']['db'],
        'charset': config['open']['charset'],
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 连接数据库
    try:
        # 连接到数据库实例1
        connection_open = pymysql.connect(**db_config_open)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
    # Fetch data from both databases

    open_data = fetch_data_from_db(connection_open)

    import os
    # Compare data
    only_in_unified, only_in_open, different_status = compare_data(unified_data, open_data)
    # no_dependency_file = os.path.join(outputName, f"no_dependency_tasks_{len(no_dependency_task_ids)}.txt")
    os.makedirs(outputName, exist_ok=True)
    # Write results to files
    write_to_file(only_in_unified.sort_values(by='tenant_id'), os.path.join(outputName,f"only_in_unified.txt"))
    write_to_file(only_in_open.sort_values(by='tenant_id'), os.path.join(outputName,f"only_in_open.txt"))
    write_to_file(different_status.sort_values(by='tenant_id'), os.path.join(outputName,f"different_status.txt"))

    print("Data comparison completed. Results written to files.")

if __name__ == "__main__":
    main()