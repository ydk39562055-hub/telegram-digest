@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==================================================== >> run_log.txt
echo RUN %date% %time% >> run_log.txt
"C:\Users\ydk39\AppData\Local\Python\pythoncore-3.14-64\python.exe" main.py >> run_log.txt 2>&1
echo DONE %date% %time% >> run_log.txt
