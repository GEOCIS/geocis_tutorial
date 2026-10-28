# Envia as alterações para o GitHub; a GitHub Action renderiza e publica o site.
# Uso (na pasta TUTORIAL):  .\atualizar_site.ps1 "mensagem do commit"
param([string]$Mensagem = "Atualiza o site")

Set-Location $PSScriptRoot
git add -A
git diff --cached --quiet
if ($?) {
    Write-Host "Nada para enviar."
    exit 0
}
git commit -m $Mensagem
if ($?) { git push }
if ($?) { Write-Host "Enviado. Acompanhe em https://github.com/GEOCIS/geocis_tutorial/actions" }
