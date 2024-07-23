import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimSong']

# 总股本和大股东持股
total_shares = 9321e6  # 总股本，单位为百万股
prosus_shares = 22798e4  # Prosus持股，单位为百万股

# 减持比例变化
reduction_steps = np.arange(0, prosus_shares + 1, 1000e4)  # 每次减持100万股
holding_ratios = []

for reduction in reduction_steps:
    # Prosus减持后持股
    new_prosus_shares = prosus_shares - reduction
    # 腾讯回购相应股票
    tencent_shares = total_shares - new_prosus_shares
    # 计算持股比例
    holding_ratio = tencent_shares / total_shares
    holding_ratios.append(holding_ratio)

# 转换为百分比
holding_ratios = np.array(holding_ratios) * 100

# 绘制趋势图
plt.figure(figsize=(10, 6))
plt.plot(reduction_steps / 1e6, holding_ratios, label='持股比例变化', color='blue')
plt.title('腾讯持股比例变化趋势图')
plt.xlabel('Prosus减持股票数量（百万股）')
plt.ylabel('腾讯持股比例（%）')
plt.grid()
plt.legend()
plt.axhline(y=holding_ratios[0], color='r', linestyle='--', label='初始持股比例')
plt.axhline(y=holding_ratios[-1], color='g', linestyle='--', label='最终持股比例')
plt.legend()
plt.show()

# 找到局部顶点
local_maxima = []
for i in range(1, len(holding_ratios) - 1):
    if holding_ratios[i] > holding_ratios[i - 1] and holding_ratios[i] > holding_ratios[i + 1]:
        local_maxima.append((reduction_steps[i] / 1e6, holding_ratios[i]))

print("局部顶点：")
for point in local_maxima:
    print(f"减持股票数量: {point[0]:.2f}百万股, 持股比例: {point[1]:.2f}%")