# 模拟分词器的使用
# 先安装 pip install sentencepiece
from transformers import XLNetTokenizer

tokenizer = XLNetTokenizer.from_pretrained("xlnet/xlnet-base-cased")
results = tokenizer.tokenize("Don't you love 🤗 Transformers? We sure do.")
for result in results:
    print(result)