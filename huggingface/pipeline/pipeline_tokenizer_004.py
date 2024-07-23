# tokenizer根据一组规则将文本拆分为tokens。然后将这些tokens转换为数字，然后转换为张量，成为模型的输入
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-cased")
# encoded_input = tokenizer("Do not meddle in the affairs of wizards, for they are subtle and quick to anger.")
# print(encoded_input)

batch_sentences = [
    "But what about second breakfast?",
    "Don't think he knows about second breakfast, Pip.",
    "What about elevensies?",
]
# encoded_inputs = tokenizer(batch_sentences)
'''
句子的长度并不总是相同，这可能会成为一个问题，因为模型输入的张量需要具有统一的形状。填充是一种策略，通过在较短的句子中添加一个特殊的padding token，以确保张量是矩形的。
将 padding 参数设置为 True，以使批次中较短的序列填充到与最长序列相匹配的长度

另一方面，有时候一个序列可能对模型来说太长了。在这种情况下，您需要将序列截断为更短的长度。
将 truncation 参数设置为 True，以将序列截断为模型接受的最大长度.
'''
encoded_inputs = tokenizer(batch_sentences,padding=True,truncation=True)
print(encoded_inputs)

'''
tokenizer返回一个包含三个重要对象的字典：

input_ids 是与句子中每个token对应的索引。
attention_mask 指示是否应该关注一个token。
token_type_ids 在存在多个序列时标识一个token属于哪个序列。
'''