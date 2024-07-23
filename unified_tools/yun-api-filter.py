import pandas as pd
import re
'''
将包含多余五个数字或 yyyy-MM-dd 格式日期的部分替换为 xxx
我们可以从多个文件中读取内容，处理每个文件的内容，去重之后将结果输出到控制台。
'''

def process_string(s):
    # 替换包含多余五个数字的部分为 'xxx'
    s = re.sub(r'/[^/]*\d{5,}[^/]*', '/xxx', s)
    # 替换包含 yyyy-MM-dd 格式日期的部分为 'xxx'
    s = re.sub(r'/[^/]*\d{4}-\d{2}-\d{2}[^/]*', '/xxx', s)
    return s


def read_and_process_file(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 假设第一列的列名为 'Column1'
    column_name = df.columns[0]

    # 处理第一列的每个字符串
    df[column_name] = df[column_name].apply(process_string)

    return df[column_name]


def main():
    # 文件路径列表
    file_paths = ['~/Downloads/new-panel_2024-07-17 19_24_16-北京.csv', '~/Downloads/new-panel_2024-07-17 19_24_10-广州.csv',
                  '~/Downloads/new-panel_2024-07-17 19_24_04-上海.csv']  # 替换为你的CSV文件路径

    # 读取并处理每个文件
    all_values = []
    for file_path in file_paths:
        processed_values = read_and_process_file(file_path)
        all_values.append(processed_values)

    # 合并所有处理后的值
    all_values = pd.concat(all_values, ignore_index=True)

    # 去重
    unique_values = all_values.drop_duplicates()

    # 按字典顺序排序
    sorted_values = unique_values.sort_values()

    # 输出到控制台
    for value in sorted_values:
        print(value)


if __name__ == "__main__":
    main()