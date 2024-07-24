from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# 下载文件
tokenizer = AutoTokenizer.from_pretrained("bigscience/T0_3B")
model = AutoModelForSeq2SeqLM.from_pretrained("bigscience/T0_3B")
# 将文件保存至指定目录
tokenizer.save_pretrained("./downs_tmp/bigscience_t0")
model.save_pretrained("./downs_tmp/bigscience_t0")