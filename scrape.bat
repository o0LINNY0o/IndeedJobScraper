@echo off
setlocal enabledelayedexpansion

:: Set the list of Python scripts to run
set "scripts=main.py xxxxx.py xxxxx.py "
for %%A in (%scripts%) do (
    echo Running %%A...
    python "%%A"
    
    if !errorlevel! equ 0 (
        echo Successfully ran %%A
    ) else (
        echo Error running %%A
    )
    
    :: Calculate a random delay 
    set /a "delay=3 + %random% %% 21"
    echo Waiting for !delay! seconds...
    timeout /t !delay! /nobreak >nul
)

@echo off
:: Set the directory to csv_files
cd csv_files

:: Get the current date and time
set dtg=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%
set dtg=%dtg: =0%

:: Copy all CSV files into a new file with date and time appended
copy *.csv merge_JOB_%dtg%.csv

:: Print completion message
echo All CSV files have been merged into merge_JOB_%dtg%.csv

pause
