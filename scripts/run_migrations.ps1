# Run all SQL files in migrations/ in lexical order
$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot '..\migrations'
Get-ChildItem -Path $folder -Filter '*.sql' | Sort-Object Name | ForEach-Object {
    Write-Host "Applying migration: $($_.FullName)"
    psql -h localhost -U postgres -d Nexgen_erp -f $_.FullName
}
Write-Host "Migrations complete." 
