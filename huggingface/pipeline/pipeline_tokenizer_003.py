# tokenizer根据一组规则将文本拆分为tokens。然后将这些tokens转换为数字，然后转换为张量，成为模型的输入
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-cased")
encoded_input = tokenizer("Do not meddle in the affairs of wizards, for they are subtle and quick to anger.")
print(encoded_input)


'''
tokenizer返回一个包含三个重要对象的字典：

input_ids 是与句子中每个token对应的索引。
attention_mask 指示是否应该关注一个token。
token_type_ids 在存在多个序列时标识一个token属于哪个序列。
'''