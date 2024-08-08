# -*- coding: utf-8 -*-
# 融合任务回切第一阶段
# 无依赖，且任务为失效，停止，冻结 或一次性任务

import requests
import mysql.connector
import sys
import json
from datetime import datetime, timedelta
import configparser
import pymysql


# 读取文件 结构为 20230921143247466 [unified_scheduler] F D
def read_file(file_path):
    print("---------begin----------")
    print("read file ",file_path)
    task_ids = set()  # 使用 set 来自动去重
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == '[unified_scheduler]':
                task_ids.add(parts[0])  # 添加到 set 中
    return sorted(list(task_ids))  # 返回去重后的列表


def get_unified_connection(config_file):
    # 读取配置文件
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
    return connection_unified


def get_open_connection(config_file):
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

    # 连接数据库
    try:
        # 连接到数据库实例1
        connection_open = pymysql.connect(**db_config_open)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
    return connection_open


def get_unified_write_connection(config_file):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_file)

    db_config_unified = {
        'host': config['unified-write']['host'],
        'user': config['unified-write']['user'],
        'password': config['unified-write']['password'],
        'db': config['unified-write']['db'],
        'charset': config['unified-write']['charset'],
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 连接数据库
    try:
        # 连接到数据库实例1
        connection_unified = pymysql.connect(**db_config_unified)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
    return connection_unified


def get_open_write_connection(config_file):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_file)

    # 从配置文件获取数据库配置
    db_config_open = {
        'host': config['open-write']['host'],
        'user': config['open-write']['user'],
        'password': config['open-write']['password'],
        'db': config['open-write']['db'],
        'charset': config['open-write']['charset'],
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 连接数据库
    try:
        # 连接到数据库实例1
        connection_open = pymysql.connect(**db_config_open)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
    return connection_open


# 任务实例满足要求，实例十分钟之前全部结束
def check_all_instance_had_done(task_id, db_connection):
    cursor = db_connection.cursor()
    now_minus_10 = datetime.now() - timedelta(minutes=10)
    query = """
    SELECT COUNT(*) as un_count
    FROM lb_task_run
    WHERE task_id = %s
    AND (state NOT IN (2, 8) OR end_time >= %s OR last_update >= %s)
    """
    cursor.execute(query, (task_id, now_minus_10, now_minus_10))
    result = cursor.fetchone()
    # 打印 result 的类型和内容
    # print(type(result))
    # print(result)

    # 检查 result 是否为 None 或者是一个空元组
    if result is None:
        return True
    count = result.get('un_count', 0)  # 假设字典中有 'count' 键

    # 检查 count 是否为 None
    return count is None or count == 0


def multi_check_all_instance_had_done(task_ids, db_connection):
    cursor = db_connection.cursor()
    now_minus_10 = datetime.now() - timedelta(minutes=10)
    if not task_ids:
        print("The task_ids list is empty.")
        return True
    task_ids_str = ','.join(['%s'] * len(task_ids))
    query = f"""
    SELECT COUNT(*) as un_count
    FROM lb_task_run
    WHERE task_id IN ({task_ids_str})
    AND exec_engine='unified_scheduler' and (state NOT IN (2, 8) OR end_time >= %s OR last_update >= %s)
    """

    # 将 task_ids 和 now_minus_10 作为参数传递
    params = task_ids + [now_minus_10, now_minus_10]
    cursor.execute(query, params)
    result = cursor.fetchone()
    print(" return ", result)
    # 检查 result 是否为 None 或者是一个空元组
    if result is None:
        return True
    count = result.get('un_count', 0)  # 假设字典中有 'count' 键

    # 检查 count 是否为 None
    return count is None or count == 0


# def call_rollback_api(task_ids, ip, port):
#     url = f"http://{ip}:{port}/rollbackTaskToWedata?tasks=" + ','.join(task_ids)
#     response = requests.get(url)
#     return response.json()

def call_rollback_api(task_ids, ip, port):
    # 确保 task_ids 中的每个元素都是字符串
    flat_task_ids = []
    for task in task_ids:
        if isinstance(task, list):
            flat_task_ids.extend(task)  # 如果是列表，展平
        else:
            flat_task_ids.append(task)  # 否则直接添加

    # 将 task_ids 列表中的元素转换为字符串并用逗号连接
    tasks = ','.join(map(str, flat_task_ids))

    # 构造请求的 URL
    url = f"http://{ip}:{port}/rollbackTaskToWedata?tasks={tasks}"
    print(f"Request URL: {url}")  # 打印请求的 URL
    try:
        response = requests.get(url)
        # 检查响应状态码
        if response.status_code == 200:
            return response.json()  # 请求成功，返回 JSON 数据
        else:
            print("request ", url)
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")  # 打印错误信息
            return None  # 或者根据需要返回其他值
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None  # 或者根据需要返回其他值


def get_task_details(task_ids, db_connection):
    cursor = db_connection.cursor()
    query = """
    SELECT task_id, status, cycle_unit 
    FROM lb_task 
    WHERE task_id IN (%s)
    """ % ','.join(['%s'] * len(task_ids))
    cursor.execute(query, task_ids)
    return cursor.fetchall()


def backup_and_delete_unified_task_run(task_ids, db_connection):
    cursor = db_connection.cursor()
    task_ids_str = ','.join(['%s'] * len(task_ids))

    try:
        # Backup records to lb_task_run_backup
        backup_query = f"""
        INSERT INTO lb_task_run_back
        SELECT * FROM lb_task_run WHERE exec_engine='unified_scheduler' and task_id IN ({task_ids_str})
        """
        cursor.execute(backup_query, task_ids)

        # Delete records from lb_task_run
        delete_query = f"""
        DELETE FROM lb_task_run WHERE exec_engine='unified_scheduler' and task_id IN ({task_ids_str})
        """
        cursor.execute(delete_query, task_ids)

        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Error during backup and delete: {e}")
        sys.exit(1)


def update_open_task_run(task_ids, db_connection):
    cursor = db_connection.cursor()
    task_ids_str = ','.join(['%s'] * len(task_ids))

    try:
        # Update exec_engine in open.lb_task_run
        update_query = f"""
        UPDATE lb_task_run
        SET exec_engine = 'wedata_scheduler'
        WHERE exec_engine='unified_scheduler' and task_id IN ({task_ids_str})
        """
        cursor.execute(update_query, task_ids)

        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Error during update: {e}")
        sys.exit(1)


import os


def read_files_with_prefix(directory, prefix,fileKey):
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在。")
        return None
    listFile = []
    # 遍历目录中的文件
    for filename in os.listdir(directory):
        # 检查文件名是否以指定前缀开头
        if filename.startswith(prefix) and fileKey in filename:
            file_path = os.path.join(directory, filename)
            # 读取文件内容
            listFile.append(file_path)
    return listFile


def reback_task(file_path, ignore_str, db_config_path, ip, port):
    f_task_ids = read_file(file_path)
    ignore_list = ignore_str.split(',')  # 使用逗号分隔并转换为集合

    # 从集合 B 中移除集合 A 的元素，得到集合 C
    # task_ids = f_task_ids - ignore_list  # 使用集合的差集操作
    task_ids = [item for item in f_task_ids if item not in ignore_list]  # 使用列表推导式

    unified_connection = get_unified_connection(db_config_path)
    open_connection = get_open_connection(db_config_path)
    unified_write_connection = get_unified_write_connection(db_config_path)
    open_write_connection = get_open_write_connection(db_config_path)

    valid_task_ids = []
    invalid_task_ids = []

    if not task_ids:
        # 有不满足的条件的任务  退出
        print("Had not any task")
        return True
    print("need deal task", len(task_ids))

    for i in range(0, len(task_ids), 30):
        batch = task_ids[i:i + 30]
        if multi_check_all_instance_had_done(batch, unified_connection) and multi_check_all_instance_had_done(batch,
                                                                                                              open_connection):
            print("item ", i, " ", len(batch), " had done")
            valid_task_ids.extend(batch)
        else:
            invalid_task_ids.extend(batch)
            print("item ", i, "Invalid task IDs:", invalid_task_ids, sep=',')
            return True

    if invalid_task_ids:
        # 有不满足的条件的任务  退出
        print("Has invalid task", len(invalid_task_ids))
        return True

    success_task_ids = []
    for j in range(0, len(valid_task_ids), 20):
        batchIds = valid_task_ids[j:j + 20]
        print(j, " api task size", len(batchIds))
        response_data = call_rollback_api(batchIds, ip, port)

        if response_data is None:
            print("API call failed for batch:", batchIds)
            return True

        if response_data['data']['errorRows'] == 0 and not response_data['data']['failTask']:
            success_task_ids.extend(response_data['data']['successTask'])
            print("API call suc for return error ", response_data['data']['errorRows'], " all ",
                  response_data['data']['totalRows'])
            # Backup and delete from unified.lb_task_run
            backup_and_delete_unified_task_run(batchIds, unified_write_connection)

            # Update open.lb_task_run
            update_open_task_run(batchIds, open_write_connection)
            print("API call suc for batch:", batchIds)

        else:
            print("API call failed for batch:", batchIds)
            print("Response data:", response_data['data'])
            return False

    print("Total successful task IDs:", len(success_task_ids))

    if success_task_ids:
        task_details = get_task_details(success_task_ids, unified_connection)
        status_count = {}
        cycle_unit_count = {}

        for task_id, status, cycle_unit in task_details:
            if status not in status_count:
                status_count[status] = 0
            status_count[status] += 1

            if cycle_unit not in cycle_unit_count:
                cycle_unit_count[cycle_unit] = 0
            cycle_unit_count[cycle_unit] += 1

        print("Status count:", status_count)
        print("Cycle unit count:", cycle_unit_count)
        print("-------end-------")
        return True
    else:
        return False


def main():
    if len(sys.argv) != 7:
        print("Usage: python script.py <file_path> <db_config_path> <ip> <port> ignoreIdStr fileKey")
        sys.exit(1)

    file_path = sys.argv[1]
    db_config_path = sys.argv[2]
    ip = sys.argv[3]
    port = sys.argv[4]
    ignore_str = sys.argv[5]
    fileKey = sys.argv[6]

    current_directory = os.getcwd()
    absolute_path = os.path.join(current_directory, file_path)
    if os.path.isfile(absolute_path):
        print(f"{absolute_path} 是一个文件。")
        reback_task(absolute_path, ignore_str, db_config_path, ip, port)
    elif os.path.isdir(absolute_path):
        print(f"{absolute_path} 是一个目录。")
        fileList = read_files_with_prefix(absolute_path, prefix='dag' ,fileKey=fileKey)
        print("find files ",len(fileList))
        for file in fileList:
            result = reback_task(file, ignore_str, db_config_path, ip, port)
            if not result:
                print("failed and exit")
                sys.exit(1)
    else:
        print(f"{absolute_path} 不存在。")
if __name__ == "__main__":
    main()