import torch.nn as nn

import torch
# 检查MPS是否可用
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
# 定义一个简单的模型
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.linear = nn.Linear(3, 1)

    def forward(self, x):
        return self.linear(x)

# 创建模型并将其移动到MPS设备
model = SimpleModel().to(device)

# 创建输入数据并将其移动到MPS设备
input_data = torch.randn(5, 3).to(device)

# 执行前向传播
output = model(input_data)
print(output)