# 直接使用huggingface 官网 使用指南,构建例子
# 加载需要认证的模型
from transformers import AutoModelForSequenceClassification,AutoTokenizer,pipeline
model_name = 'maidalun1020/bce-reranker-base_v1'
access_token='token_id'
model = AutoModelForSequenceClassification.from_pretrained(model_name,token=access_token)
tokenizer = AutoTokenizer.from_pretrained(model_name,token=access_token)
text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
results = text_classification("深圳的小学生都开始放假了，爸爸妈妈有的忙了")
for result in results:
    # print(result)
    print(f"label: {result['label']}, with score: {round(result['score'], 4)}")