@echo off
rem Cria um atalho na pasta Inicializar do Windows para o vigia ligar a cada login,
rem e ja liga o vigia agora. Para desfazer: desativar_envio_automatico.cmd
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$a = Join-Path ([Environment]::GetFolderPath('Startup')) 'GeoCiS - envio automatico do tutorial.lnk';" ^
  "$l = (New-Object -ComObject WScript.Shell).CreateShortcut($a);" ^
  "$l.TargetPath = \"$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe\";" ^
  "$l.Arguments = '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%~dp0vigiar_e_enviar.ps1\"';" ^
  "$l.WorkingDirectory = '%~dp0';" ^
  "$l.Save();" ^
  "Write-Host ('Atalho criado: ' + $a)"
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.CommandLine -like '*vigiar_e_enviar.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
start "" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0vigiar_e_enviar.ps1"
echo Envio automatico ativado. Ele passa a ligar sozinho sempre que voce entrar no Windows.
pause
