@echo off
setlocal enabledelayedexpansion

REM Activate the virtual environment
call C:\path\to\your\venv\Scripts\activate.bat

REM Check if arguments are provided
if "%~1"=="" (
  echo {"result": "Please specify a command. Available commands: list-tests, run-test, report, charts, compare"}
  exit /b
)

REM Execute the command and capture output
set output_file=%TEMP%\bp_agent_output.txt
python "%~dp0\main.py" %* > "%output_file%" 2>&1

REM Read the file content
set "content="
for /f "usebackq delims=" %%a in ("%output_file%") do (
  set "line=%%a"
  set "line=!line:\=\\!"
  set "line=!line:"=\"!"
  if defined content (
    set "content=!content!\n!line!"
  ) else (
    set "content=!line!"
  )
)

REM Output JSON formatted result
echo {"result": "!content!"}

REM Clean up
del "%output_file%"
