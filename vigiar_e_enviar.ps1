# Vigia a pasta TUTORIAL e envia ao GitHub alguns segundos depois de cada alteração.
# A GitHub Action então gera e publica o site.
# Uso: .\vigiar_e_enviar.ps1            (espera 15 s sem alterações antes de enviar)
#      .\vigiar_e_enviar.ps1 -Espera 60
param([int]$Espera = 15)

$pasta = $PSScriptRoot
$log = Join-Path $pasta "envio_automatico.log"
# Alterações nestas pastas/arquivos não disparam envio
$ignorar = '(^|[\\/])(\.git|_site|\.quarto)([\\/]|$)|^envio_automatico\.log$'

function Registrar($texto) {
    $linha = "{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $texto
    Write-Host $linha
    Add-Content -Path $log -Value $linha -Encoding UTF8
}

function Enviar {
    git -C $pasta add -A
    git -C $pasta diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { return }

    # O repositório é público: segura arquivos com cara de senha/chave, ou grandes demais
    $suspeito = '(^|/)\.env|\.(pem|key|pfx|p12|kdbx)$|(^|/)id_(rsa|ed25519)|senha|password|secret|credencia|token'
    $barrados = @()
    foreach ($f in (git -C $pasta diff --cached --name-only --diff-filter=AM)) {
        $caminho = Join-Path $pasta $f
        $grande = (Test-Path $caminho) -and ((Get-Item $caminho).Length -gt 50MB)
        if ($f -match $suspeito -or $grande) { $barrados += $f }
    }
    if ($barrados.Count -gt 0) {
        foreach ($f in $barrados) { git -C $pasta reset -q -- $f }
        Registrar ("BLOQUEADO (possível dado sensível ou arquivo > 50 MB, não enviado): " + ($barrados -join ", "))
        git -C $pasta diff --cached --quiet
        if ($LASTEXITCODE -eq 0) { return }
    }

    $arquivos = (git -C $pasta diff --cached --name-only) -join ", "
    git -C $pasta commit -q -m ("Atualização automática {0:yyyy-MM-dd HH:mm}" -f (Get-Date))
    git -C $pasta pull -q --rebase
    if ($LASTEXITCODE -ne 0) {
        git -C $pasta rebase --abort
        Registrar "ERRO: conflito com o GitHub. Resolva manualmente (git pull) e salve de novo."
        return
    }
    git -C $pasta push -q
    if ($LASTEXITCODE -eq 0) { Registrar "Enviado: $arquivos" }
    else { Registrar "ERRO no push. O commit ficou local e vai junto no próximo envio." }
}

$vigia = New-Object IO.FileSystemWatcher $pasta
$vigia.IncludeSubdirectories = $true
$vigia.NotifyFilter = [IO.NotifyFilters]'FileName, DirectoryName, LastWrite'

Registrar "Vigiando $pasta (envio $Espera s após a última alteração)"
Enviar  # envia o que tiver mudado enquanto o vigia estava desligado

$pendente = $false
$ultima = Get-Date
while ($true) {
    $r = $vigia.WaitForChanged([IO.WatcherChangeTypes]::All, 1000)
    if (-not $r.TimedOut) {
        if ($r.Name -notmatch $ignorar) { $pendente = $true; $ultima = Get-Date }
    }
    elseif ($pendente -and ((Get-Date) - $ultima).TotalSeconds -ge $Espera) {
        $pendente = $false
        Enviar
    }
}
