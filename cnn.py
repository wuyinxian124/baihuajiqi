import numpy as np
import math
import os.path
import urllib.request
import gzip
import matplotlib.pyplot as plt

# 下载 MNIST 数据集
def download_mnist_dataset(url):
    filename = './' + os.path.basename(url)
    if os.path.isfile(filename):
        return

    buf = urllib.request.urlopen(url).read()
    with open(filename, mode='wb') as f:
        f.write(buf)

BASE_URL = 'http://yann.lecun.com/exdb/mnist/'
filenames = [
    'train-images-idx3-ubyte.gz',
    'train-labels-idx1-ubyte.gz',
    't10k-images-idx3-ubyte.gz',
    't10k-labels-idx1-ubyte.gz'
]
[download_mnist_dataset(BASE_URL + filename) for filename in filenames]

# 读取 MNIST 数据集
def load_file(filename, offset):
    with gzip.open('./' + filename + '.gz', 'rb') as f:
        return np.frombuffer(f.read(), np.uint8, offset=offset)

# 读取训练数据
TX = load_file('train-images-idx3-ubyte', offset=16)
TY = load_file('train-labels-idx1-ubyte', offset=8)

def convertX(X):
    return X.reshape(-1, 1, 28, 28).astype(np.float32) / 255.0

TX = convertX(TX)

def convertY(Y):
    return np.eye(10)[Y]

TY = convertY(TY)

# 图像展示
def show_images(X):
    COLUMN = 5
    ROW = (len(X) - 1) // COLUMN + 1

    fig = plt.figure()

    for i in range(len(X)):
        sub = fig.add_subplot(ROW, COLUMN, i + 1)
        sub.axis('off')
        sub.set_title('X[{}]'.format(i))
        plt.imshow(X[i][0], cmap='gray')

    plt.show()

# 展示前10张
show_images(TX[0:10])

# （为了使训练结果可以复现，固定种子的值。本来是不需要这么做的）
np.random.seed(0)

W1 = np.random.randn( 32,  1, 5, 5)   * math.sqrt(2 / ( 1 * 5 * 5))
W2 = np.random.randn( 64, 32, 5, 5)   * math.sqrt(2 / (32 * 5 * 5))
W3 = np.random.randn(200, 64 * 7 * 7) * math.sqrt(2 / (64 * 7 * 7))
W4 = np.random.randn( 10, 200)        * math.sqrt(2 / 200)
b1 = np.zeros(32)
b2 = np.zeros(64)
b3 = np.zeros(200)
b4 = np.zeros(10)

# 计算卷积后的特征图的大小
def output_size(input_size, filter_size, stride_size=1, padding_size=0):
    return (input_size - filter_size + 2 * padding_size) // stride_size + 1

# 从 im 形式变换为 col 形式
# -----------------------
#
# im：变换前的图像，形式为“图像数 × 通道数 × 高 × 宽”
# fh：过滤器的高
# fw：过滤器的宽
# s：步进
# p：填充
#
# 返回值：形式为“个数为图像数的特征图的高和宽的大小 × 过滤器的大小”的矩阵
def im2col(im, fh, fw, s=1, p=0):
    # 计算卷积后的特征图的大小
    N, IC, IH, IW = im.shape
    OH, OW = output_size(IH, fh, s, p), output_size(IW, fw, s, p)

    # 填充为 0
    if p > 0:
        im = np.pad(im, [(0,0), (0,0), (p,p), (p,p)], mode='constant')

    # 从 im 形式复制为 col 形式
    col = np.zeros([N, fh * fw, IC, OH, OW])
    for h in range(fh):
        for w in range(fw):
            col[:, h*fw+w] = im[:, :, h:h+(OH*s):s, w:w+(OW*s):s]

    return col.transpose(0, 3, 4, 2, 1).reshape(N * OH * OW, IC * fh * fw)

# 卷积
def convolve(X, W, b, s=1, p=0):
    # 计算卷积后的特征图的大小
    N, IC, IH, IW = X.shape
    K, KC, FH, FW = W.shape
    OH, OW = output_size(IH, FH, s, p), output_size(IW, FW, s, p)

    # 为了能进行矩阵的乘法的计算，对X和W变形
    X = im2col(X, FH, FW, s, p)
    W = W.reshape(K, KC * FH * FW).T

    # 计算卷积
    Z = np.dot(X, W) + b

    # 恢复为“图像数 × 通道数 × 高 × 宽”的排列
    return Z.reshape(N, OH, OW, K).transpose(0, 3, 1, 2)

# ReLU函数
def relu(X):
    return np.maximum(0, X)

# Max Pooling
def max_pooling(X, fh, fw, s):
    # 计算卷积后的特征图的大小
    N, IC, IH, IW = X.shape
    OH, OW = output_size(IH, fh, s), output_size(IW, fw, s)

    # 为了更容易选择最大值，变更数据的形式
    X = im2col(X, fh, fw, s).reshape(N * OH * OW * IC, fh * fw)

    # 计算最大值及其索引
    P  = X.max(axis=1)
    PI = X.argmax(axis=1)

    return P.reshape(N, OH, OW, IC).transpose(0, 3, 1, 2), PI

# softmax函数
def softmax(X):
    # 从各元素减去最大值，以防止溢出
    N = X.shape[0]
    X = X - X.max(axis=1).reshape(N, -1)

    # softmax函数的计算
    return np.exp(X) / np.exp(X).sum(axis=1).reshape(N, -1)

# 正向传播
def forward(X0):
    # 卷积层1
    Z1 = convolve(X0, W1, b1, s=1, p=2)
    A1 = relu(Z1)
    X1, PI1 = max_pooling(A1, fh=2, fw=2, s=2)

    # 卷积层2
    Z2 = convolve(X1, W2, b2, s=1, p=2)
    A2 = relu(Z2)
    X2, PI2 = max_pooling(A2, fh=2, fw=2, s=2)

    # 展开为 1列
    N = X2.shape[0]
    X2 = X2.reshape(N, -1)

    # 全连接层
    Z3 = np.dot(X2, W3.T) + b3
    X3 = relu(Z3)

    # 输出层
    Z4 = np.dot(X3, W4.T) + b4
    X4 = softmax(Z4)

    return Z1, X1, PI1, Z2, X2, PI2, Z3, X3, X4

# ReLU的微分
def drelu(x):
    return np.where(x > 0, 1, 0)

# 输出层的德尔塔
def delta_output(T, Y):
    return -T + Y

# 隐藏层的德尔塔
def delta_hidden(Z, D, W):
    return drelu(Z) * np.dot(D, W)

# 从 col 形式变换为 im 形式
# -----------------------
#
# col：col形式的数据
# im_shape：指定恢复为im形式时的“图像数 × 通道数 × 高 × 宽”的大小
# fh：过滤器的高
# fw：过滤器的宽
# s：步进
# p：填充
#
# 返回值：指定的大小为im_shape的矩阵
def col2im(col, im_shape, fh, fw, s=1, p=0):
    # 卷积后的特征图的纵向和横向的大小
    N, IC, IH, IW = im_shape
    OH, OW = output_size(IH, fh, s, p), output_size(IW, fw, s, p)

    # 为im形式分配内存，这是包含步进和填充的情况
    im = np.zeros([N, IC, IH + 2 * p + s - 1, IW + 2 * p + s - 1])

    # 从 col 形式恢复为 im 形式。重复的元素相加
    col = col.reshape(N, OH, OW, IC, fh * fw).transpose(0, 4, 3, 1, 2)
    for h in range(fh):
        for w in range(fw):
            im[:, :, h:h+(OH*s):s, w:w+(OW*s):s] += col[:, h*fw+w]

    # 由于不需要填充的部分，所以先去除再返回
    return im[:, :, p:IH+p, p:IW+p]

# 卷积层的德尔塔
def delta_conv(P, D, W, s, p):
    N, DC, DH, DW = D.shape
    K, KC, FH, FW = W.shape

    # 适当地将矩阵变形为 col 形式
    D = D.transpose(0, 2, 3, 1).reshape(N * DH * DW, DC)
    W = W.reshape(K, KC * FH * FW)
    col_D = np.dot(D, W)

    # 将 col 形式恢复为 im 形式，计算德尔塔
    return drelu(P) * col2im(col_D, P.shape, FH, FW, s, p)

# 最大池化的反向传播
def backward_max_pooling(im_shape, PI, D, fh, fw, s):
    # 按过滤器的高 × 宽纵向排列单元，并填充为 0
    N, C, H, W = im_shape
    col_D = np.zeros(N * C * H * W).reshape(-1, fh * fw)
    # 在池化选择的索引的位置放回德尔塔
    col_D[np.arange(PI.size), PI] = D.flatten()
    # 进行 col2im 变换，恢复为 im 形式
    return col2im(col_D, im_shape, fh, fw, s)

# 反向传播
def backward(Y, X4, Z3, X2, PI2, Z2, X1, PI1, Z1):
    D4 = delta_output(Y, X4)
    D3 = delta_hidden(Z3, D4, W4)

    D2 = delta_hidden(X2, D3, W3)
    D2 = backward_max_pooling(Z2.shape, PI2, D2, fh=2, fw=2, s=2)

    D1 = delta_conv(X1, D2, W2, s=1, p=2)
    D1 = backward_max_pooling(Z1.shape, PI1, D1, fh=2, fw=2, s=2)

    return D4, D3, D2, D1

# 对目标函数的权重进行微分
def dweight(D, X):
    return np.dot(D.T, X)

# 对目标函数的偏置进行微分
def dbias(D):
    return D.sum(axis=0)

# 目标函数对过滤器权重的微分
def dfilter_weight(X, D, weight_shape):
    K, KC, FH, FW = weight_shape
    N, DC, DH, DW = D.shape

    D = D.transpose(1, 0, 2, 3).reshape(DC, N * DH * DW)
    col_X = im2col(X, FH, FW, 1, 2)
    return np.dot(D, col_X).reshape(K, KC, FH, FW)

# 目标函数对过滤器偏置的微分
def dfilter_bias(D):
    N, C, H, W = D.shape
    return D.transpose(1, 0, 2, 3).reshape(C, N * H * W).sum(axis=1)

# 学习率
ETA = 1e-4

# 参数的更新
def update_parameters(D4, X3, D3, X2, D2, X1, D1, X0):
    global W4, W3, W2, W1, b4, b3, b2, b1

    W4 = W4 - ETA * dweight(D4, X3)
    W3 = W3 - ETA * dweight(D3, X2)
    W2 = W2 - ETA * dfilter_weight(X1, D2, W2.shape)
    W1 = W1 - ETA * dfilter_weight(X0, D1, W1.shape)

    b4 = b4 - ETA * dbias(D4)
    b3 = b3 - ETA * dbias(D3)
    b2 = b2 - ETA * dfilter_bias(D2)
    b1 = b1 - ETA * dfilter_bias(D1)

# 训练
def train(X0, Y):
    Z1, X1, PI1, Z2, X2, PI2, Z3, X3, X4 = forward(X0)

    D4, D3, D2, D1 = backward(Y, X4, Z3, X2, PI2, Z2, X1, PI1, Z1)

    update_parameters(D4, X3, D3, X2, D2, X1, D1, X0)

# 轮数
EPOCH = 5

# 预测
def predict(X):
    return forward(X)[-1]

# 交叉熵函数
def E(T, X):
    return -(T * np.log(predict(X) + 1e-5)).sum()

# 小批量的大小
BATCH = 100

for epoch in range(1, EPOCH + 1):
    # 获取用于小批量训练的随机索引
    p = np.random.permutation(len(TX))

    # 取出数量为小批量大小的数据，进行训练
    for i in range(math.ceil(len(TX) / BATCH)):
        indice = p[i*BATCH:(i+1)*BATCH]
        X0 = TX[indice]
        Y  = TY[indice]

        train(X0, Y)

        # 输出日志
        if i % 10 == 0:
            error = E(Y, X0)
            log = '误差: {:8.4f} (第{:2d}轮 第{:3d}个小批量)'
            print(log.format(error, epoch, i))

testX = load_file('t10k-images-idx3-ubyte', offset=16)
testX = convertX(testX)

# 显示测试数据集的前 10 个数据
show_images(testX[0:10])

# 分类
def classify(X):
    return np.argmax(predict(X), axis=1)

classify(testX[0:10])
