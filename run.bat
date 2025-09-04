@echo off
echo 开始安装虚拟环境
if not exist ".venv\" (
    echo 创建虚拟环境...
    python -m venv .venv
    echo 虚拟环境已创建
)

echo 开始安装依赖
pip install -r requirements.txt
echo 依赖安装完成

echo 获取数据集
python get_dataset.py

echo 开始处理数据
python analysis_dataset.py

echo 开始生成报告
python write_report.py

pause