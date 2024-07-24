import torch
# 检查MPS是否可用
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

# 创建两个张量并将其移动到MPS设备
a = torch.randn(5, 3).to(device)
b = torch.randn(5, 3).to(device)

# 执行计算
c = a + b
print(c)