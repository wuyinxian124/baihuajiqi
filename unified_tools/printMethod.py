import os
import re
from collections import defaultdict


def read_method_names(file_path):
    """
    从文件中读取方法名，每行一个。

    :param file_path: 文件路径
    :return: 方法名列表
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        method_names = [line.strip() for line in file if line.strip()]
    return method_names


def find_methods_in_file(file_path, method_names):
    """
    在指定的文件中查找匹配的方法。

    :param file_path: 文件路径
    :param method_names: 方法名列表
    :return: 匹配的方法信息字典，键为方法名，值为匹配的信息列表
    """
    methods_info = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 匹配类名的正则表达式
        class_pattern = re.compile(r'public\s+interface\s+(\w+)')
        class_match = class_pattern.search(content)
        class_name = class_match.group(1) if class_match else 'UnknownClass'

        # 匹配方法定义的正则表达式
        method_pattern = re.compile(r'@(PostMapping|GetMapping)\("([^"]+)"\)\s+.*?\s+(\w+)\s*\(')
        matches = method_pattern.findall(content)
        for match in matches:
            annotation, url, method_name = match
            if method_name in method_names:
                methods_info[method_name].append((url, f'{class_name}#{method_name}'))
    return methods_info


def find_methods_in_directory(directory, method_names):
    """
    在指定的目录中查找匹配的方法。

    :param directory: 目录路径
    :param method_names: 方法名列表
    :return: 匹配的方法信息字典，键为方法名，值为匹配的信息列表
    """
    result = defaultdict(list)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('Api.java'):
                file_path = os.path.join(root, file)
                methods_info = find_methods_in_file(file_path, method_names)
                for method_name, infos in methods_info.items():
                    result[method_name].extend(infos)
    return result


# if __name__ == '__main__':
#     method_names_file = 'path/to/method_names.txt'  # 替换为你的方法名文件路径
#     directory = 'path/to/your/directory'  # 替换为你的目录路径
#
#     method_names = read_method_names(method_names_file)
#     matching_methods = find_methods_in_directory(directory, method_names)
#
#     for method_name, infos in matching_methods.items():
#         print(f'Method: {method_name}')
#         for url, method_info in infos:
#             print(f'  URL: {url}, Method: {method_info}')

if __name__ == '__main__':
    method_names_file = 'function.txt'  # 替换为你的方法名文件路径
    directory = '/Users/runzhouwu/project/cloud/tbds-common-api/tbds-guldan-api/src/main/java/com/tencent/tbds/guldan/api'  # 替换为你的目录路径
    print("begin")
    method_names = read_method_names(method_names_file)
    matching_methods = find_methods_in_directory(directory, method_names)

    for file_path, methods_info in matching_methods.items():
        print(f'In file: {file_path}')
        for url, method_info in methods_info:
            print(f'  URL: {url}, Method: {method_info}')