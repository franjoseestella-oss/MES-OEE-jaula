$inputFile = "C:\Users\franj\.gemini\antigravity\brain\fb4a348d-b9a5-4ddc-b0bd-921ea2180790\.system_generated\steps\3974\output.txt"
$outputFile = "c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\turno_actual_dashboard.json"

$raw = Get-Content $inputFile -Raw
$json = $raw | ConvertFrom-Json
$dash = $json.dashboard

# Remove runtime fields
$dash.PSObject.Properties.Remove('id')
$dash.PSObject.Properties.Remove('version')

$out = $dash | ConvertTo-Json -Depth 50
[System.IO.File]::WriteAllText($outputFile, $out, [System.Text.Encoding]::UTF8)

Write-Host "Dashboard exported successfully"
