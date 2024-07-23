import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimSong']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 初始条件
total_shares = 93210  # 腾讯总股本（百万股）
prosus_shares = 22798  # Prosus持股数量（百万股）
reduce_amount = 10  # 每次减持数量（百万股）
iterations = 1000  # 减持次数
repurchase_ratio = 1.1  # 腾讯回购比例（假设每次减持的110%）

# 存储持股比例变化
share_ratios = []
zero_crossing_iteration = None  # 记录持股比例降至0的迭代次数

# 计算每次减持和回购后的持股比例
for i in range(iterations):
    if prosus_shares <= 0:
        break
    prosus_shares -= reduce_amount
    if prosus_shares < 0:
        prosus_shares = 0
    repurchase_amount = reduce_amount * repurchase_ratio
    total_shares -= repurchase_amount
    share_ratio = prosus_shares / total_shares * 100
    share_ratios.append(share_ratio)

    # 检查持股比例是否降至0
    if share_ratio <= 0 and zero_crossing_iteration is None:
        zero_crossing_iteration = i

# 计算一阶差分和二阶差分
first_diff = np.diff(share_ratios)
second_diff = np.diff(share_ratios, n=2)

# 判断变化趋势函数的凹凸性
is_linear = np.all(second_diff == 0)

if not is_linear:
    # 找到局部极值点（顶点）
    local_minima = (np.diff(np.sign(first_diff)) > 0).nonzero()[0] + 1
    local_maxima = (np.diff(np.sign(first_diff)) < 0).nonzero()[0] + 1

# 生成增减表
data = {
    '减持次数': range(len(share_ratios)),
    '持股比例 (%)': share_ratios,
    '变化量': [0] + list(first_diff)
}
df = pd.DataFrame(data)
df['变化趋势'] = df['变化量'].apply(lambda x: '增加' if x > 0 else '减少' if x < 0 else '不变')

# 绘制持股比例变化趋势图
plt.figure(figsize=(10, 6))
plt.plot(range(len(share_ratios)), share_ratios, marker='o', linestyle='-', color='b')
plt.title('Prosus 持股比例变化趋势')
plt.xlabel('减持次数')
plt.ylabel('持股比例 (%)')
plt.grid(True)

# 标注零界点
if zero_crossing_iteration is not None:
    plt.axvline(x=zero_crossing_iteration, color='r', linestyle='--')
    plt.text(zero_crossing_iteration, 0, f'零界点: {zero_crossing_iteration}', color='r', ha='right')

if not is_linear:
    # 标注局部极值点
    for idx in local_minima:
        plt.scatter(idx, share_ratios[idx], color='g', zorder=5)
        plt.text(idx, share_ratios[idx], f'局部最小值: ({idx}, {share_ratios[idx]:.2f}%)', color='g', ha='right')

    for idx in local_maxima:
        plt.scatter(idx, share_ratios[idx], color='r', zorder=5)
        plt.text(idx, share_ratios[idx], f'局部最大值: ({idx}, {share_ratios[idx]:.2f}%)', color='r', ha='right')

plt.show()

# 输出零界点和局部极值点
if zero_crossing_iteration is not None:
    print(f'持股比例降至0的零界点在第 {zero_crossing_iteration} 次减持时。')
else:
    print('持股比例未降至0。')

if is_linear:
    print(f'持股比例变化趋势函数是线性的。')
else:
    print(f'持股比例变化趋势函数的凹凸性: 既不凹也不凸')
    print(f'局部最小值点: {[(idx, share_ratios[idx]) for idx in local_minima]}')
    print(f'局部最大值点: {[(idx, share_ratios[idx]) for idx in local_maxima]}')

# 输出增减表
print("\n增减表:")
print(df)