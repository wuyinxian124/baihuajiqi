model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# 模型和分词器必须一样
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
results = classifier("Nous sommes très heureux de vous présenter la bibliothèque 🤗 Transformers.")
for result in results:
    # print(result)
    print(f"label: {result['label']}, with score: {round(result['score'], 4)}")