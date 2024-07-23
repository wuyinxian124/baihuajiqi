# 模拟分词器的使用
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("google-bert/bert-base-uncased")
results = tokenizer.tokenize("I have a new GPU!")
for result in results:
    print(result)