import os
import re


def find_java_files(directories):
    """扫描指定目录下所有 .java 结尾的文件"""
    java_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.java') and not file.endswith('Test.java'):
                    java_files.append(os.path.join(root, file))
    return java_files


def extract_methods(file_path, keywords):
    """从文件中提取包含特定关键字的方法调用，并打印整行以便调试"""
    methods = set()
    patterns = [re.compile(rf'\b{keyword}\.\w+\(') for keyword in keywords]  # 匹配 keyword.methodName(

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            for pattern, keyword in zip(patterns, keywords):
                if keyword in line:
                    print(f"Debug: {line.strip()}")  # 打印整行以便调试
                    matches = pattern.findall(line)
                    for match in matches:
                        method = match[:-1]  # 去掉最后的 '('
                        methods.add(method)

    return methods


def main(directories, keywords):
    java_files = find_java_files(directories)
    all_methods = set()

    for java_file in java_files:
        methods = extract_methods(java_file, keywords)
        all_methods.update(methods)

    sorted_methods = sorted(all_methods)

    for method in sorted_methods:
        print(method)


if __name__ == "__main__":
    # 指定目录和关键字
    # ds
    # directories = ['/Users/runzhouwu/project/cloud/tbds-datastudio/datastudio-common/src/main/java/com/tencent/tbds/datastudio',
    #                '/Users/runzhouwu/project/cloud/tbds-datastudio/datastudio-mvc/datastudio-service/src/main/java/com/tencent/tbds/datastudio/service']  # 替换为你的目录路径列表
    # keywords = ['tbdsGuldanApi','taskExecutionServApi']  # 替换为你的关键字列表

    # 集成
    # directories = ['/Users/runzhouwu/project/runzhou/wedata-dis-service/src/main/java/com/tencent/cloud/wedata/di']  # 替换为你的目录路径列表
    # keywords = ['tbdsGuldanApi', 'guldanInnerServApi','taskExecutionServApi','taskOperationServApi','dataIntegrationServApi','scheduleOpsApi']  # 替换为你的关键字列表

    # 元数据
    # directories = ['/Users/runzhouwu/project/cloud/hybris/hybris-scheduler/hybris-scheduler-biz/src/main/java/com/tencent/hybris/scheduler/biz']  # 替换为你的目录路径列表
    # keywords = ['instanceServiceApi', 'guldanInnerServApi','taskExecutionServApi','taskOperationServApi','dataIntegrationServApi','scheduleOpsApi','tbdsGuldanApi','makePlanOperateApi']  # 替换为你的关键字列表

    # dq
    # directories = ['/Users/runzhouwu/project/cloud/wedata-dq/dq-service/src/main/java/com/tencent/cloud/wedata/dq/service']  # 替换为你的目录路径列表
    # keywords = ['tbdsGuldanApi', 'openPlatformServApi','schedulerGuldanApiV3','taskExecutionServApi','scheduleOpsApi']  # 替换为你的关键字列表

    # 运维
    directories = ['/Users/runzhouwu/project/cloud/wedata-ai-ops/wedata-ai-ops-api/src/main/java/com/tencent/wedata/ai/ops'
                   ,'/Users/runzhouwu/project/cloud/wedata-ai-ops/wedata-ai-ops-common/src/main/java/com/tencent/wedata/ai/ops/commons'
        ,'/Users/runzhouwu/project/cloud/wedata-ai-ops/wedata-ai-ops-core/src/main/java/com/tencent/wedata/ai/ops/core']  # 替换为你的目录路径列表
    keywords = ['tbdsGuldanApi', 'openPlatformServApi','schedulerGuldanApiV3','taskExecutionServApi','guldanScheduleOpsApi','makePlanOperateApi','instanceServiceApi']  # 替换为你的关键字列表



    main(directories, keywords)