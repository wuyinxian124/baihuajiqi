# -*- coding: utf-8 -*-
# 打印指定任务的 上下游，广度遍历 ,传入一个任务id
import sys
import mysql.connector
import pandas as pd
import networkx as nx
import configparser
import pymysql
import os
from datetime import datetime

if len(sys.argv) < 3:
    print("Usage: python script.py <config_file> tenantId outName")
    sys.exit(1)

config_file = sys.argv[1]
specific_tenant_id = sys.argv[2]
outputName = sys.argv[3]

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

# 连接数据库
try:
    # 连接到数据库实例1
    connection_unified = pymysql.connect(**db_config_unified)
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# 查询 lb_task 和 lb_task_link 表
query_task = "SELECT task_id, tenant_id, status, exec_engine,cycle_unit FROM lb_task WHERE status IN ('F', 'Y', 'O','INVALID')"
query_task_link = "SELECT task_from, task_to FROM lb_task_link"

try:
    df_task = pd.read_sql(query_task, connection_unified)
    df_task_link = pd.read_sql(query_task_link, connection_unified)
except Exception as e:
    print(f"Error querying database: {e}")
    connection_unified.close()
    exit(1)

connection_unified.close()

# 过滤 lb_task_link 中无效的依赖关系
valid_task_ids = set(df_task['task_id'])
df_task_link = df_task_link[
    df_task_link['task_from'].isin(valid_task_ids) &
    df_task_link['task_to'].isin(valid_task_ids)
    ]

# 创建有向图
G = nx.DiGraph()

# 添加节点
for _, row in df_task.iterrows():
    G.add_node(row['task_id'], tenant_id=row['tenant_id'], exec_engine=row['exec_engine'])

# 添加边
for _, row in df_task_link.iterrows():
    G.add_edge(row['task_from'], row['task_to'])

# 按 tenant_id 分类
tenant_groups = df_task.groupby('tenant_id')

# 获取当前时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 创建输出目录
output_dir = f"{outputName}_output_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# 输出结果
for tenant_id, group in tenant_groups:
    tenant_dir = os.path.join(output_dir, str(tenant_id))
    os.makedirs(tenant_dir, exist_ok=True)

    # 获取该 tenant_id 的子图
    subgraph = G.subgraph(group['task_id'])

    # 查找所有的连通分量（DAG）
    dag_index = 0
    no_dependency_tasks = []
    for component in nx.weakly_connected_components(subgraph):
        dag = subgraph.subgraph(component)

        # 检查是否是有向无环图
        if not nx.is_directed_acyclic_graph(dag):
            print(f"Error: Found a cycle in tenant {tenant_id} for tasks {list(component)}")
            continue

        # 获取节点列表和 exec_engine
        task_ids = list(dag.nodes)
        exec_engines = [dag.nodes[task_id]['exec_engine'] for task_id in task_ids]

        # 检查是否所有的 exec_engine 都是 'unified_scheduler'
        # all_unified_scheduler = all(engine == 'unified_scheduler' for engine in exec_engines)
        # exec_engine_label = "all_unified_scheduler" if all_unified_scheduler else "mixed_exec_engines"
        # 检查 exec_engine 类型
        if all(engine == 'unified_scheduler' for engine in exec_engines):
            exec_engine_label = "all_unified"
        elif all(engine != 'unified_scheduler' for engine in exec_engines):
            exec_engine_label = "all_guldan"
        else:
            exec_engine_label = "mixed"

        # 输出结果到文件
        if len(task_ids) > 1:
            dag_file = os.path.join(tenant_dir, f"dag_{dag_index}_tasks_{len(task_ids)}_{exec_engine_label}.txt")
            with open(dag_file, 'w') as f:
                for task_id, exec_engine in zip(task_ids, exec_engines):
                    f.write(f"{task_id} [{exec_engine}]\n")
            dag_index += 1
        else:
            # 将单个任务ID添加到无依赖任务列表
            no_dependency_tasks.append((task_ids[0], exec_engines[0]))

    # 查找没有依赖关系的任务
    all_task_ids = set(df_task['task_id'])
    linked_task_ids = set(df_task_link['task_from']).union(set(df_task_link['task_to']))
    no_dependency_task_ids = all_task_ids - linked_task_ids

    # 将无依赖任务写入文件
    no_dependency_file = os.path.join(tenant_dir, f"no_dependency_tasks_{len(no_dependency_task_ids)}.txt")
    with open(no_dependency_file, 'w') as f:
        for task_id in no_dependency_task_ids:
            # 取相等的第一行
            task_info = df_task[df_task['task_id'] == task_id].iloc[0]
            if task_info['tenant_id'] == tenant_id:
                f.write(f"{task_id} [{task_info['exec_engine']}] {task_info['status']} {task_info['cycle_unit']}\n")
        for task_id, exec_engine in no_dependency_tasks:
            # 取相等的第一行
            task_info = df_task[df_task['task_id'] == task_id].iloc[0]
            if task_info['tenant_id'] == tenant_id:
                f.write(f"{task_id} [{task_info['exec_engine']}] {task_info['status']} {task_info['cycle_unit']}\n")