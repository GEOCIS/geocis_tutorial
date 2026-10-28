@echo off
rem Remove o atalho da pasta Inicializar e desliga o vigia que estiver rodando.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Remove-Item (Join-Path ([Environment]::GetFolderPath('Startup')) 'GeoCiS - envio automatico do tutorial.lnk') -ErrorAction SilentlyContinue;" ^
  "Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -like '*vigiar_e_enviar.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo Envio automatico desativado.
pause
