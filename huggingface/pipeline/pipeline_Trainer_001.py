from datasets import load_dataset

# 准备数据集
# 加载Yelp评论数据集：
dataset = load_dataset("yelp_review_full")
print(dataset["train"][100])

from transformers import AutoTokenizer
# tokenizer来处理文本，包括填充和截断操作以处理可变的序列长度
tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-cased")
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)
# Datasets 的 map 方法，将预处理函数应用于整个数据集
tokenized_datasets = dataset.map(tokenize_function, batched=True)
# tokenized_datasets = small_train_dataset.map(tokenize_function, batched=True)

# 完整数据集提取一个较小子集来进行微调，以减少训练所需的时间：
small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(100))
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(100))

# 开始训练
'''
 Transformers 提供了一个专为训练 Transformers 模型而优化的 Trainer 类，使您无需手动编写自己的训练循环步骤而更轻松地开始训练模型
 1.指定模型
 2.指定训练超参数
 3.指定评估函数
 4.创建训练器
 5.微调模型
'''
from transformers import AutoModelForSequenceClassification
# 1.指定模型
# 加载您的模型并指定期望的标签数量,已知数据集有五个标签
model = AutoModelForSequenceClassification.from_pretrained("google-bert/bert-base-cased", num_labels=5)

# 2.指定训练超参数
# 创建一个 TrainingArguments 类，其中包含您可以调整的所有超参数以及用于激活不同训练选项的标志。对于本教程，您可以从默认的训练超参数开始，但随时可以尝试不同的设置以找到最佳设置。
from transformers import TrainingArguments
training_args = TrainingArguments(output_dir="test_trainer")

# 3.指定评估函数
# Trainer 在训练过程中不会自动评估模型性能。您需要向 Trainer 传递一个函数来计算和展示指标。🤗 Evaluate 库提供了一个简单的 accuracy 函数，您可以使用 evaluate.load 函数加载它
import numpy as np
import evaluate
metric = evaluate.load("accuracy")

# 在 metric 上调用 compute 来计算您的预测的准确性。在将预测传递给 compute 之前，您需要将预测转换为logits（请记住，所有 🤗 Transformers 模型都返回对logits）
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 在微调过程中监视评估指标，请在您的训练参数中指定 eval_strategy 参数，以在每个epoch结束时展示评估指标：
from transformers import TrainingArguments, Trainer
training_args = TrainingArguments(output_dir="test_trainer", eval_strategy="epoch")

# 4.创建训练器
# 创建一个包含您的模型、训练参数、训练和测试数据集以及评估函数的 Trainer 对象
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)
# 5.微调模型
# 调用train()以微调模型
trainer.train()