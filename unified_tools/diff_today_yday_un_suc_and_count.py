# -*- coding: utf-8 -*-
"""
脚本功能：
该脚本用于连接MySQL数据库，执行一个特定的SQL查询，该查询旨在获取昨天成功运行且今天未成功或未运行的任务的详细信息。脚本将统计每个任务的记录数，并按租户ID和工作流ID进行排序。同时，脚本还会统计每个租户的任务数和实例数。

脚本输出：

任务详细信息：包括租户ID、工作流ID、任务ID以及对应的记录数。这些信息将被写入一个名为task_details_YYYYMMDDHHMMSS.txt的文件中，其中YYYYMMDDHHMMSS是脚本运行时的时间戳。
租户任务和实例计数：包括每个租户的任务数和实例数。这些信息将被写入一个名为tenant_task_instance_counts_YYYYMMDDHHMMSS.txt的文件中。
脚本操作步骤：

配置数据库连接：在脚本中填写数据库的主机地址、用户名、密码和数据库名。
执行SQL查询：脚本将执行预定义的SQL查询，获取所需的数据。
数据处理：脚本将处理查询结果，计算每个任务的记录数以及每个租户的任务数和实例数。
写入文件：脚本将统计结果写入两个不同的文件中，并在文件名中包含时间戳。
注意事项：

确保在运行脚本之前已经安装了pymysql库。如果未安装，可以使用pip install pymysql命令进行安装。
在脚本中填写正确的数据库配置信息，包括主机地址、用户名、密码和数据库名。
脚本文件应以UTF-8编码保存，以支持中文字符的正确输出。
在写入文件时，脚本使用了UTF-8编码，以确保中文说明能够正确写入。
运行脚本后，您将在脚本所在的目录中找到两个新文件，包含了任务详细信息和租户任务及实例计数的统计结果。

use command
 python3 thisfile.py /path/db_config.txt
"""
import sys
import pymysql
import pymysql.cursors
import configparser
from datetime import datetime, timedelta

# 检查是否提供了配置文件名称作为命令行参数
if len(sys.argv) < 2:
    print("Usage: python script.py <config_file>")
    sys.exit(1)

config_file = sys.argv[1]

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

# 连接到数据库实例1
connection_open = pymysql.connect(**db_config_open)

try:
    with connection_open.cursor() as cursor:
        # 获取当前时间的小时和分钟
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute

        # 执行SQL查询
        sql = """
        SELECT
            y.task_id,
            y.tenant_id,
            y.project_id,
            y.task_type,
            y.cur_run_date AS yesterday_run_date,
            y.state AS yesterday_state,
            y.end_time AS yesterday_end_time,
            t.cur_run_date AS today_run_date,
            t.state AS today_state
        FROM
            lb_task_run AS y
        LEFT JOIN
            lb_task_run AS t ON y.task_id = t.task_id
            AND t.cur_run_date = DATE_ADD(y.cur_run_date, INTERVAL 1 DAY)
        WHERE
            DATE(y.cur_run_date) = DATE(NOW()) - INTERVAL 1 DAY
            AND y.state = 2 -- 昨天成功的状态
            AND HOUR(y.end_time) < %s -- 昨天的结束时间小于今天的当前小时
            AND (MINUTE(y.end_time) < %s OR HOUR(y.end_time) < %s) -- 昨天的结束时间小于今天的当前分钟或小时
            AND t.cur_run_date IS NOT NULL -- 今天的实例已经生成
            AND (t.state IS NULL OR t.state != 2) -- 今天的状态不是成功或没有状态
        ORDER BY
            y.tenant_id,
            y.task_type,
            y.project_id,
            y.task_id;
        """
        cursor.execute(sql, (current_hour, current_minute, current_hour))
        results = cursor.fetchall()

        # Initialize dictionaries to store statistics
        task_details = {}
        tenant_task_counts = {}

        # Process the results to calculate statistics
        for row in results:
            task_id = row['task_id']
            tenant_id = row['tenant_id']
            project_id = row['project_id']
            task_type = row['task_type']
            task_key = (tenant_id, project_id, task_id,task_type)

            # Count records for each task ID and store additional details
            if task_key not in task_details:
                task_details[task_key] = {
                    'tenant_id': tenant_id,
                    'project_id': project_id,
                    'task_type': task_type,
                    'task_id': task_id,
                    'count': 0
                }
            task_details[task_key]['count'] += 1

            # Count tasks and instances for each tenant
            if tenant_id not in tenant_task_counts:
                tenant_task_counts[tenant_id] = {'tasks': set(), 'instances': 0}
            tenant_task_counts[tenant_id]['tasks'].add(task_id)
            tenant_task_counts[tenant_id]['instances'] += 1

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Output the task details to a file
        task_details_filename = f"task_details_{timestamp}.txt"
        with open(task_details_filename, 'w') as f:
            for key in sorted(task_details.keys()):
                details = task_details[key]
                f.write(f"Tenant ID {details['tenant_id']}, Project ID {details['project_id']},task_type ID {details['task_type']}, Task ID {details['task_id']}: {details['count']} records\n")
        print(f"Task details written to {task_details_filename}")

        # Output the tenant task and instance counts to a file
        tenant_counts_filename = f"tenant_task_instance_counts_{timestamp}.txt"
        with open(tenant_counts_filename, 'w') as f:
            for tenant_id, counts in tenant_task_counts.items():
                task_count = len(counts['tasks'])
                instance_count = counts['instances']
                f.write(f"Tenant ID {tenant_id}: {task_count} tasks, {instance_count} instances\n")
        print(f"Tenant task and instance counts written to {tenant_counts_filename}")

finally:
    connection_open.close()
