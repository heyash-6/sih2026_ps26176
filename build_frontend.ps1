$env:PATH = "C:\Users\tidke\AppData\Local\ms-playwright-go\1.57.0;" + $env:PATH
$nodePath = "C:\Users\tidke\AppData\Local\ms-playwright-go\1.57.0\node.exe"
$npmCli = "C:\Users\tidke\.nodejs_tools\npm\bin\npm-cli.js"
Set-Location -Path "$PSScriptRoot\frontend"
& $nodePath $npmCli run build
