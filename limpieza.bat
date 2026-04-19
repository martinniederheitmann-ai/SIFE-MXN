@echo off
echo limpiando archivos temporales...

del /q /f /s %TEMPS%\*
del /q /f /s C:\Windows\Temp\*
del /q /f /s c:\Windows\Prefetch*

cleanmgr /sagerun:1

echo limpieza concluida

pause