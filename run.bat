@echo off
echo ��ʼ���нű�...

REM �������⻷��
echo �������⻷��...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ����: δ�ҵ����⻷������������ setup.bat
    pause
    exit /b 1
)

echo ��ȡ���ݼ�
python get_dataset.py

echo ��ʼ��������
python analysis_dataset.py

echo ��ʼ���ɱ���
python write_report.py

pause