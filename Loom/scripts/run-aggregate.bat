@echo off
:: -----------------------------------------------------
:: Poyi Chat Log Aggregator Batch Launcher
:: -----------------------------------------------------
echo Running Poyi Chat Log Aggregator...
python "%~dp0aggregate_win.py" %*
echo Done.
pause
