import pandas as pd
import os
import yaml  # 添加yaml支持

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 读取配置文件
config = {}
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
keyword = config['keyword']


df = pd.read_csv(f'{keyword}_dataset.csv')
print(df.head(1))