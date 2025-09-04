#!/usr/bin/env python
# coding: utf-8

# ## 1. 基础配置

# In[102]:


import pandas as pd
import matplotlib.pyplot as plt
import ast
import yaml
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# In[103]:


# 设置显示选项以显示所有列
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', 1000)        # 设置显示宽度
pd.set_option('display.max_colwidth', None) # 显示完整的列内容

plt.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']  # 使用微软雅黑作为首选
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

def format_large_numbers(value, _):
    if value >= 100000:
        return f'{value/10000:.0f}万'
    else:
        return f'{value:.0f}'


# In[104]:


# 读取配置文件
config = {}
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
dataset_dir = config['dataset_dir']
fig_dir = config['fig_dir']
keyword = config['keyword']


# In[105]:


try:
    os.makedirs(fig_dir)
except:
    pass


# ## 2. 数据清洗与预处理

# In[106]:


df = pd.read_csv(f'{dataset_dir}/{keyword}.csv')
print(df.shape)
print(df.describe(include='all'))


# 很多列没有数据

# In[107]:


# 删除无数据的列
df = df.dropna(axis=1, how='all')
print(df.isna().sum().sort_values(ascending=False).head())


# In[108]:


# 处理空值
df['tag'] = df['tag'].fillna('')# 对于tag列，填充为空字符串
df = df.dropna(subset=['title'])# 对于title列，删除唯一一个空值行
df['description'] = df['description'].fillna('')# 对于description列，填充为空字符串
print("处理后空值统计:", df.isna().sum().sum(), '; 形状:', df.shape)# 确认处理结果


# In[109]:


print(df.head(1).T)


# In[110]:


# 保留这些列
columns_list = ['bvid','title','tag','description','arcurl','pic',# bv号 标题 标签 描述 链接 封面
                'pubdate','senddate','duration','hit_columns',# 发布时间 发送时间 时长 命中搜索的列
                'typename','typeid','author','mid','upic',# 分区类型 分区类型ID 作者 作者id 作者头像
                'is_pay','is_union_video','is_charge_video',# 是否付费 是否联合投稿 是否是充电视频
                'play','like','favorites','danmaku','review',# 播放数 点赞数 收藏数 弹幕数 评论数
                ]
df = df[columns_list]
print(df.shape)
print(df.describe(include='all'))


# 处理异常数据

# bv号有相同的

# In[111]:


# 相同bvid只保留一个
df = df.drop_duplicates(subset=['bvid'], keep='first')
print(df.shape)
print(df['bvid'].describe())


# In[112]:


#删除title列的<em class="keyword">和</em>
df['title'] = df['title'].str.replace('<em class="keyword">', '').str.replace('</em>', '')


# In[113]:


# 显示'hit_columns'列不同值的数量
print(df['hit_columns'].value_counts().sort_values(ascending=False))


# hit_columns中只有'author'的明显是无效数据

# In[114]:


# 删除'hit_columns'列中数据为['author']的行
df = df[df['hit_columns'] != '[\'author\']']
print('\'hit_columns\'列为[\'author\']的形状：',df[df['hit_columns'] == '[\'author\']'].shape)
print(df.shape)


# In[115]:


# 1. 处理日期字段（将时间戳转换为可读日期）
df['pubdate_dt'] = pd.to_datetime(df['pubdate'], unit='s')
df['senddate_dt'] = pd.to_datetime(df['senddate'], unit='s')

# 2. 处理视频时长（将"0:51"格式转换为秒数）
def duration_to_seconds(duration_str):
    try:
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except:
        return 0

df['duration'] = df['duration'].apply(duration_to_seconds)    

# 3. 创建新特征 - 视频年龄（从发布到数据表中最晚的时间）
latest_date = df['pubdate_dt'].max()
df['video_age_days'] = (latest_date - df['pubdate_dt']).dt.days

print(df[['pubdate_dt', 'senddate_dt', 'duration','video_age_days']].head(3))
print(df[['pubdate_dt', 'senddate_dt', 'duration','video_age_days']].describe())


# ## 3. 探索性数据分析

# ### 3.1 命中分析

# In[116]:


# 将 hit_columns 转换为列表
df['hit_columns'] = df['hit_columns'].apply(ast.literal_eval)

# 使用 explode 展开列表，然后统计每个字段的出现次数
hit_counts = df['hit_columns'].explode().value_counts()

# 创建柱状图
plt.figure(figsize=(10, 6))
hit_counts.plot(kind='bar')
plt.title('各字段作为搜索命中原因的出现次数')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{fig_dir}/各字段作为搜索命中原因的出现次数.png')



# ### 3.2 发布时间分析

# In[ ]:


# 统计每天的发布数量，并绘制折线图
daily_counts = df['pubdate_dt'].dt.date.value_counts().sort_index()

plt.figure(figsize=(12, 6))
daily_counts.plot(kind='line')
plt.title('每天的视频发布数量')
plt.xlabel('日期')
plt.ylabel('数量')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{fig_dir}/每天的视频发布数量.png')



# In[ ]:


# 统计每月的发布数量，并绘制柱状图
monthly_counts = df['pubdate_dt'].dt.to_period('M').value_counts().sort_index()

plt.figure(figsize=(12, 6))
monthly_counts.plot(kind='bar')
plt.title('每月的视频发布数量')
plt.xlabel('月份')
plt.ylabel('数量')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f'{fig_dir}/每月的视频发布数量.png')



# In[ ]:


# 统计每年的发布数量，并绘制柱状图
yearly_counts = df['pubdate_dt'].dt.to_period('Y').value_counts().sort_index()

plt.figure(figsize=(12, 6))
yearly_counts.plot(kind='bar')
plt.title('每年的视频发布数量')
plt.xlabel('年份')
plt.ylabel('数量')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{fig_dir}/每年的视频发布数量.png')



# ### 3.3 视频时长分析

# In[ ]:


# 将视频时长分为几个区间
bins = [0, 60, 300, 600, 1800, 3600, float('inf')]
labels = ['<1分钟', '1-5分钟', '5-10分钟', '10-30分钟', '30-60分钟', '>60分钟']


# 统计每个区间的视频数量，并绘制柱状图
df['duration'] = pd.cut(df['duration'], bins=bins, labels=labels, right=False)
duration_counts = df['duration'].value_counts().sort_index()

plt.figure(figsize=(10, 6))
duration_counts.plot(kind='bar')
plt.title('视频时长分布')
plt.xlabel('时长区间')
plt.ylabel('数量')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{fig_dir}/视频时长分布.png')



# ### 3.4 视频分析

# In[121]:


def plt_video_top10(by:str, title:str):
    '''
    by:排序的值
    title:图表标题
    '''
    # 获取by量前十的视频
    top10 = df.sort_values(by=by, ascending=False).head(10)

    # 创建图表
    plt.figure(figsize=(12, 8))
    # 创建垂直柱状图
    bars = plt.bar(range(len(top10)), top10[by])
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_large_numbers))
    plt.title(title)
    plt.xticks(range(len(top10)), range(1, len(top10)+1))

    # 在图表下方添加详细信息
    table_data = []
    for i, (index, row) in enumerate(top10.iterrows(), 1):
        short_title = row['title'][:40] + '...' if len(row['title']) > 40 else row['title']
        table_data.append([i, row['bvid'], row['author'], short_title])

    # 创建表格
    table = plt.table(cellText=table_data,
                    colLabels=['排名', 'BV号', '作者', '标题'],
                    cellLoc='left',
                    loc='bottom',
                    bbox=[0, -0.5, 1, 0.4])

    table.auto_set_column_width([0, 1, 2, 3])  # 根据内容自动调整列宽
    #设置导出的大小
    plt.tight_layout()
    plt.savefig(f'{fig_dir}/{title}.png')
    


# In[122]:


# 获取播放量前十的视频
plt_video_top10('like', 'B站视频播放量前十')


# In[123]:


# 获取点赞量前十的视频
plt_video_top10('like', 'B站视频点赞量前十')


# In[124]:


# 获取收藏量前十的视频
plt_video_top10('favorites', 'B站视频收藏量前十')


# In[125]:


# 获取弹幕量前十的视频
plt_video_top10('danmaku', 'B站视频弹幕量前十')


# In[126]:


# 获取评论量前十的视频
plt_video_top10('review', 'B站视频评论量前十')


# ### 3.5 up主分析

# In[127]:


#根据mid确定有多少up变成了'账号已注销'，在总up中的占比
up_counts = df['mid'].value_counts()
print('up主数量:', up_counts.shape[0])
outup_counts = df[df['author'] == '账号已注销']['mid'].value_counts()
print('注销up主数量:', outup_counts.shape[0])
print('注销up主占比:', outup_counts.shape[0] / up_counts.shape[0]*100,'%')


# In[ ]:


# 统计每个up主发布的视频数量，并绘制前十的柱状图（不包括'账号已注销')
up_pub_counts = df[df['author'] != '账号已注销']['author'].value_counts().head(10)

plt.figure(figsize=(14, 6))
up_pub_counts.plot(kind='bar')
plt.title('发布视频数量前十的up主')
plt.xlabel('up主')
plt.ylabel('数量')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{fig_dir}/发布视频数量前十的up主.png')



# In[129]:


def plt_up_top10(by:str, title:str):
    '''
    by:排序的值
    title:图表标题
    '''
    up_play_counts = df[df['author'] != '账号已注销'].groupby('author')[by].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(14, 6))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_large_numbers))
    up_play_counts.plot(kind='bar')
    plt.title(title)
    plt.xlabel('up主')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{fig_dir}/{title}.png')
    


# In[130]:


# 统计每个up主发布的视频总观看数量，并绘制前十的柱状图（不包括'账号已注销')
plt_up_top10('play', '视频总观看数量前十的up主')


# In[131]:


# 统计每个up主发布的视频总点赞数量，并绘制前十的柱状图（不包括'账号已注销')
plt_up_top10('like', '视频总点赞数量前十的up主')


# In[132]:


# 统计每个up主发布的视频总收藏数量，并绘制前十的柱状图（不包括'账号已注销')
plt_up_top10('favorites','视频总收藏数量前十的up主')


# In[133]:


# 统计每个up主发布的视频总弹幕数量，并绘制前十的柱状图（不包括'账号已注销')
plt_up_top10('danmaku', '视频总弹幕数量前十的up主')


# In[134]:


# 统计每个up主发布的视频总评论数量，并绘制前十的柱状图（不包括'账号已注销')
plt_up_top10('review', '视频总评论数量前十的up主')


# 古月狐狸怎么这么多喵 QWQ
