# B站关键词相关视频数据分析
## 项目简介
本项目主要对B站关键词相关视频进行数据分析，包括视频播放量、点赞量、评论量、投币量、分享量、收藏量等指标，并使用Python进行数据可视化。

## 数据来源
数据来源于<a href='https://github.com/Nemo2011/bilibili-api'>bilibili-api</a>，通过关键词搜索获取相关视频的播放量、点赞量、评论量、投币量、分享量、收藏量等指标。

## 数据处理
使用Python对数据进行处理

## 数据可视化
ipynb笔记：<a href='analysis_dataset.ipynb'>卡拉彼丘视频数据分析</a><br>
分析报告示例：
<img src='others/pics/report.png'></a>

## 运行须知
配置文件为<a href='config.yaml'>config.yaml</a>，请根据实际情况修改配置文件中的参数。
<pre><code>
dataset_dir: 'datasets'  # 数据集保存的目录
fig_dir: 'figures'  # 图表保存的目录

keyword: '卡拉彼丘'  # 搜索词
if_set_day_limit: False  # 是否设置截止日期
day_limit: '2025-09-02'  # 年-月-日：获取一直获取数据，直到这一天为止
num_limit: 7  # 无截止日期时，一直获取数据，直到连续{num_limit}天没有数据为止
day_distance: 0  # 0:从今天开始，1:从昨天开始，2:从前天开始，以此类推

sleep_time: 0.5  # 每次请求之间的延迟（秒）
</code></pre>
双击run.bat运行程序。