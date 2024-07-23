import numpy as np
import math

# 训练数据的数量
N = 1000

#（为了使训练结果可以复现，固定种子的值。本来是不需要这么做的）
np.random.seed(1)

# 随机生成训练数据和正确答案的标签
TX = (np.random.rand(N, 2) * 1000).astype(np.int32) + 1
TY = (TX.min(axis=1) / TX.max(axis=1) <= 0.2).astype(np.int)[np.newaxis].T

# 计算平均值和标准差
MU = TX.mean(axis=0)
SIGMA = TX.std(axis=0)

# 标准化
def standardize(X):
    return (X - MU) / SIGMA

TX = standardize(TX)

# 权重和偏置
W1 = np.random.randn(2, 2) # 第1层的权重
W2 = np.random.randn(2, 2) # 第2层的权重
W3 = np.random.randn(1, 2) # 第3层的权重
b1 = np.random.randn(2)    # 第1层的偏置
b2 = np.random.randn(2)    # 第2层的偏置
b3 = np.random.randn(1)    # 第3层的偏置

# sigmoid 函数
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

# 正向传播
def forward(X0):
    Z1 = np.dot(X0, W1.T) + b1
    X1 = sigmoid(Z1)
    Z2 = np.dot(X1, W2.T) + b2
    X2 = sigmoid(Z2)
    Z3 = np.dot(X2, W3.T) + b3
    X3 = sigmoid(Z3)

    return Z1, X1, Z2, X2, Z3, X3

# sigmoid 函数的微分
def dsigmoid(x):
    return (1.0 - sigmoid(x)) * sigmoid(x)

# 输出层的德尔塔
def delta_output(Z, Y):
    return (sigmoid(Z) - Y) * dsigmoid(Z)

# 隐藏层的德尔塔
def delta_hidden(Z, D, W):
    return dsigmoid(Z) * np.dot(D, W)

# 反向传播
def backward(Y, Z3, Z2, Z1):
    D3 = delta_output(Z3, Y)
    D2 = delta_hidden(Z2, D3, W3)
    D1 = delta_hidden(Z1, D2, W2)

    return D3, D2, D1

# 学习率
ETA = 0.001

# 对目标函数的权重进行微分
def dweight(D, X):
    return np.dot(D.T, X)

# 对目标函数的偏置进行微分
def dbias(D):
    return D.sum(axis=0)

# 更新参数
def update_parameters(D3, X2, D2, X1, D1, X0):
    global W3, W2, W1, b3, b2, b1

    W3 = W3 - ETA * dweight(D3, X2)
    W2 = W2 - ETA * dweight(D2, X1)
    W1 = W1 - ETA * dweight(D1, X0)

    b3 = b3 - ETA * dbias(D3)
    b2 = b2 - ETA * dbias(D2)
    b1 = b1 - ETA * dbias(D1)

# 训练
def train(X, Y):
    # 正向传播
    Z1, X1, Z2, X2, Z3, X3 = forward(X)

    # 反向传播
    D3, D2, D1 = backward(Y, Z3, Z2, Z1)

    # 参数的更新（神经网络的训练）
    update_parameters(D3, X2, D2, X1, D1, X)

# 重复次数
EPOCH = 30000

# 预测
def predict(X):
    return forward(X)[-1]

# 目标函数
def E(Y, X):
    return 0.5 * ((Y - predict(X)) ** 2).sum()

# 小批量的大小
BATCH = 100

for epoch in range(1, EPOCH + 1):
    # 获得用于小批量训练的随机索引
    p = np.random.permutation(len(TX))

    # 取出数量为小批量大小的数据并训练
    for i in range(math.ceil(len(TX) / BATCH)):
        indice = p[i*BATCH:(i+1)*BATCH]
        X0 = TX[indice]
        Y  = TY[indice]

        train(X0, Y)

    # 输出日志
    if epoch % 1000 == 0:
        log = '误差 = {:8.4f}(第{:5d}轮)'
        print(log.format(E(TY, TX), epoch))

# 分类器
def classify(X):
    return (predict(X) > 0.8).astype(np.int)

# 生成测试数据
TEST_N = 1000
testX = (np.random.rand(TEST_N, 2) * 1000).astype(np.int32) + 1
testY = (testX.min(axis=1) / testX.max(axis=1) <= 0.2).astype(np.int)[np.newaxis].T

# 计算精度
accuracy = (classify(standardize(testX)) == testY).sum() / TEST_N
print('精度: {}%'.format(accuracy * 100))
