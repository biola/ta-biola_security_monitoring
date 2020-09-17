@ECHO OFF
cd /d %~dp0
cscript.exe /NoLogo /T:240 check_update_stats.vbs
