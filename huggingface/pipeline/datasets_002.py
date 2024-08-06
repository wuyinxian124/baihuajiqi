# from datasets import load_dataset_builder
# ds_builder = load_dataset_builder("m-a-p/COIG-CQIA")
from datasets import load_dataset

dataset = load_dataset("m-a-p/COIG-CQIA",'zhihu',split='train')

print(dataset.info.description)
print("-----")
print(dataset.info.features)
# 遍历数据集
iterable_dataset = dataset.to_iterable_dataset()

# 取一行
print(dataset[0])
print("----")
# 取一行中的一个字段
print(dataset[0]['instruction'])