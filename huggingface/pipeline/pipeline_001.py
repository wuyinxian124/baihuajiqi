from transformers import pipeline

# 情感分析
classifier = pipeline("sentiment-analysis")
results = classifier("We are very happy to show you the 🤗 Transformers library.")
for result in results:
    # print(result)
    print(f"label: {result['label']}, with score: {round(result['score'], 4)}")