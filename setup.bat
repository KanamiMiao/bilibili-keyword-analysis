@echo off
echo ��������Python��Ŀ����...

REM ���Python�Ƿ�װ
python --version >nul 2>&1
if errorlevel 1 (
    echo ����: δ�ҵ�Python�����Ȱ�װPython 3.6+
    pause
    exit /b 1
)

REM �������⻷������������ڣ�
if not exist ".venv\Scripts\activate.bat" (
    echo �������⻷��...
    python -m venv .venv
    echo ���⻷�������ɹ�
)

REM �������⻷��
echo �������⻷��...
call .venv\Scripts\activate.bat

REM ����pip
echo ����pip...
python -m pip install --upgrade pip

REM ���requirements.txt�Ƿ����
if not exist "requirements.txt" (
    echo ����: δ�ҵ�requirements.txt�ļ�
    pause
    exit /b 1
)

REM ��װ����
echo ��װ����...
pip install -r requirements.txt
if errorlevel 1 (
    echo ������װʧ��
    pause
    exit /b 1
)

echo �����������!
echo ���ֶ�����: .venv\Scripts\activate.bat ���������⻷��
pause