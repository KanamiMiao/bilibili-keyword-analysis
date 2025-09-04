import yaml
import os
os.chdir(os.path.abspath(os.path.dirname(__file__)))

base_report = ''
config = {}

with open('base_report.html', 'r', encoding='utf-8') as f:
    base_report = f.read()

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)


fig_dir = config['fig_dir']
keyword = config['keyword']

with open(f'{fig_dir}/{keyword}分析报告.html', 'w', encoding='utf-8') as f:
    base_report = base_report.replace('{fill_keyword}', keyword)
    f.write(base_report)
