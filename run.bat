@echo off
echo 开始运行脚本...

REM 激活虚拟环境
echo 激活虚拟环境...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo 错误: 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

echo 获取数据集
python get_dataset.py

echo 开始处理数据
python analysis_dataset.py

echo 开始生成报告
python write_report.py

pause