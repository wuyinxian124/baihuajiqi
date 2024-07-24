from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel

# 使用

tokenizer = AutoTokenizer.from_pretrained("./downs_tmp/bigscience_t0")
model = AutoModel.from_pretrained("./downs_tmp/bigscience_t0")


# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
#
# tokenizer = AutoTokenizer.from_pretrained("bigscience/T0pp")
# model = AutoModelForSeq2SeqLM.from_pretrained("bigscience/T0pp")

inputs = tokenizer.encode("Is this review positive or negative? Review: this is the best cast iron skillet you will ever buy", return_tensors="pt")
outputs = model.generation(inputs)
print(tokenizer.decode(outputs[0]))
