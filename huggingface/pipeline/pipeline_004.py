# 直接使用huggingface 官网 使用指南,构建例子
from transformers import AutoModelForSequenceClassification,AutoTokenizer,pipeline
model = AutoModelForSequenceClassification.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
tokenizer = AutoTokenizer.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
results = text_classification("深圳的小学生都开始放假了，爸爸妈妈有的忙了",function_to_apply = 'softmax',top_kxx='xxx')
for result in results:
    # print(result)
    print(f"label: {result['label']}, with score: {round(result['score'], 4)}")