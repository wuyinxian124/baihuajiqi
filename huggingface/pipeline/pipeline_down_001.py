# 下载指定文件
# downloading files from the Hub
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id="lysandre/arxiv-nlp", filename="config.json",local_dir="./downs")

hf_hub_download(repo_id="google/fleurs", filename="fleurs.py", repo_type="dataset",local_dir="./downs")
# hf_hub_download(repo_id="google/fleurs", filename="fleurs.py", repo_type="dataset")


# downloads an entire repository at a given revision
from huggingface_hub import snapshot_download
snapshot_download(repo_id="lysandre/arxiv-nlp", allow_patterns="*.json",local_dir="./downs")