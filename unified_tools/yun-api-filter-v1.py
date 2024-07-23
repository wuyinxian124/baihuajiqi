import pandas as pd
import re
'''
它可以从 Excel 文件中读取 A、B、C、D 列的数据，去除内容中的前后空格，忽略内容为空的记录，并根据你的要求处理内容。最后，它会将去重和排序后的结果输出到控制台
'''


def process_string(s):
    # 去除前后空格
    s = s.strip()

    # 忽略内容为空的记录
    if not s:
        return None

    # 查找并处理 URL
    url_match = re.search(r'(?i)URL:\s*([^,]+)', s)
    if url_match:
        s = url_match.group(1).strip()

    # 查找并处理 Method
    method_match = re.search(r'(?i)Method:', s)
    if method_match:
        s = s[:method_match.start()].strip()

    return s


def read_and_process_excel(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path, usecols="A:D")

    # 合并A、B、C、D列
    all_values = pd.concat([df[col].dropna().apply(str).apply(process_string) for col in df.columns])

    # 去除None值
    all_values = all_values.dropna()

    # 去重
    unique_values = all_values.drop_duplicates()

    # 按字典顺序排序
    sorted_values = unique_values.sort_values()

    return sorted_values


def main():
    # 文件路径
    file_path = '~/Downloads/调用接口统计全模块.xlsx'  # 替换为你的Excel文件路径

    # 读取并处理Excel文件
    sorted_values = read_and_process_excel(file_path)

    # 输出到控制台
    for value in sorted_values:
        print(value)


if __name__ == "__main__":
    main()