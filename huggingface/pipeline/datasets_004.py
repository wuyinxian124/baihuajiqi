# from datasets import load_dataset_builder
# ds_builder = load_dataset_builder("m-a-p/COIG-CQIA")
from datasets import load_dataset

ds_builder = load_dataset("MushanW/GLOBE",split='test')

print(ds_builder.info.description)
print("-----")
print(ds_builder.info.features)
# 取其中几行，前三行
ds_builder = ds_builder[:3]
# Get rows between three and six
# ds_builder = ds_builder[3:6]
# 取一行
print(ds_builder[0])
print("----")
# 取一行中的一个字段
print(ds_builder[0]['audio'])