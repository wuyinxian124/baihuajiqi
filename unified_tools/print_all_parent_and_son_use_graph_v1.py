# -*- coding: utf-8 -*-
# 打印指定任务的 上下游，广度遍历
import pymysql
import collections
import configparser
import sys
from collections import deque, defaultdict

if len(sys.argv) < 3:
    print("Usage: python script.py <config_file> tasId")
    sys.exit(1)

config_file = sys.argv[1]
specific_task_id = sys.argv[2]

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

# 创建游标
cursor = connection_open.cursor()

# 从lb_task表中获取所有状态为'Y'的任务
cursor.execute("SELECT task_id,exec_engine FROM task_version_info WHERE used_version =1")
tasks = cursor.fetchall()
valid_tasks = {task['task_id'] for task in tasks}
print(f'The size of tasks: {len(valid_tasks)}')

# 从lb_task_link表中获取这些任务的单向关系
cursor.execute("SELECT task_from, task_to FROM task_version_link_info ")
links = cursor.fetchall()
print(f'The size of links: {len(links)}')

# 构建一个图
graph = collections.defaultdict(list)
graph1 = collections.defaultdict(list)
for link in links:
    task_from, task_to = link['task_from'], link['task_to']
    if task_from in valid_tasks and task_to in valid_tasks:
        graph[task_from].append(task_to) # 添加 父到子 下游节点
        graph1[task_to].append(task_from)  # 添加 子到父 上游节点


def print_bfs(graph, root):
    visited = set()
    queue = deque([(root, 0)])  # 队列中的元素是一个元组，包含节点和它的层级
    current_level = 0
    while queue:
        node, level = queue.popleft()

        if level > current_level:
            print()
            print(f"no.: {level}")  # 打印换行符
            current_level = level

        if node not in visited:
            print(node, end=' ')
            visited.add(node)

            for child in graph[node]:
                queue.append((child, level + 1))

# 找出特定任务的所有上下游任务

print("------------------ALL SON-------------")
print_bfs(graph, specific_task_id)
print()
print("------------------ALL parent----------")
print_bfs(graph1, specific_task_id)


# 关闭游标和连接
cursor.close()
connection_open.close()