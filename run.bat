@echo off
echo ��ʼ��װ���⻷��
if not exist ".venv\" (
    echo �������⻷��...
    python -m venv .venv
    echo ���⻷���Ѵ���
)

echo ��ʼ��װ����
pip install -r requirements.txt
echo ������װ���

echo ��ȡ���ݼ�
python get_dataset.py

echo ��ʼ��������
python analysis_dataset.py

echo ��ʼ���ɱ���
python write_report.py

pause