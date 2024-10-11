setlocal EnableDelayedExpansion

:: Execute all Python scripts except *_scraper_utils.py
for %%F in (*.py) do (
    echo %%F | findstr /i "_scraper_utils.py" >nul
    if errorlevel 1 (
        echo Executing: %%F
        python "%%F"

        :: Calculate a random delay between 1 and 5 seconds
        set /a "delay=1 + !random! %% 5"
        echo Waiting for !delay! seconds...
        timeout /t !delay! /nobreak >nul
    )
)

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
