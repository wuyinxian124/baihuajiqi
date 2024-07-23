# -*- coding: utf-8 -*-
# 打印指定任务的 上下游，广度遍历
import pymysql
import collections
import configparser
import sys
from collections import deque, defaultdict
from datetime import datetime

if len(sys.argv) < 3:
    print("Usage: python script.py <config_file>")
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

import graphviz

# 获取任务及其exec_engine
cursor.execute("SELECT task_id,exec_engine FROM task_version_info WHERE used_version =1")
tasks = cursor.fetchall()
valid_tasks = {task['task_id']: task['exec_engine'] for task in tasks}
print(f'The size of tasks: {len(valid_tasks)}')

# 从lb_task_link表中获取这些任务的单向关系
cursor.execute("SELECT task_from, task_to FROM task_version_link_info ")
links = cursor.fetchall()
print(f'The size of links: {len(links)}')

# 构建一个图
graph = collections.defaultdict(list)
graph1 = collections.defaultdict(list)
for link in links:
    task_from, task_to = link['task_from'], link['task_to']  # 修正此行
    if task_from in valid_tasks and task_to in valid_tasks:
        graph[task_from].append(task_to)  # 添加 父到子 下游节点
        graph1[task_to].append(task_from)  # 添加 子到父 上游节点

def create_graphviz_graph(graph, root, valid_tasks):
    dot = graphviz.Digraph(comment='DAG')
    visited = set()
    queue = deque([(root, 0, None)])  # 队列中的元素是一个元组，包含节点、层级和父节点

    while queue:
        node, level, parent = queue.popleft()

        if node not in visited:
            exec_engine_initial = valid_tasks[node][0] if valid_tasks[node] else ''
            dot.node(node, f"{node}[{exec_engine_initial}]")

            if parent is not None:
                parent_exec_engine_initial = valid_tasks[parent][0] if valid_tasks[parent] else ''
                dot.edge(parent, node)

            visited.add(node)

            for child in graph[node]:
                queue.append((child, level + 1, node))

    return dot

# 找出特定任务的所有上下游任务
# 获取当前时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("------------------ALL SON-------------")
dot_son = create_graphviz_graph(graph, specific_task_id, valid_tasks)
print(dot_son.source)  # 打印Graphviz源代码
dot_son.render(f'output_son_{timestamp}', format='png')  # 生成并保存图像文件

print("------------------ALL parent----------")
dot_parent = create_graphviz_graph(graph1, specific_task_id, valid_tasks)
print(dot_parent.source)  # 打印Graphviz源代码
dot_parent.render(f'output_parent_{timestamp}', format='png')  # 生成并保存图像文件

# 关闭游标和连接
cursor.close()
connection_open.close()