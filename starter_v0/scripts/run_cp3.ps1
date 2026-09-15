$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
Push-Location $labRoot
try {
    $python = Join-Path $labRoot '.venv/Scripts/python.exe'
    $snapshot = 'artifacts/versions/v3_cp3'
    New-Item -ItemType Directory -Force -Path 'runs/cp3' | Out-Null
    & $python scripts/preflight_provider.py --provider openrouter --model openrouter/free --tools "$snapshot/tools.yaml" 2>&1 | Tee-Object -FilePath 'runs/cp3/preflight.txt'
    if ($LASTEXITCODE -ne 0) { throw 'Preflight failed; no further API calls.' }
    foreach ($suite in @('base', 'adversarial')) {
        & $python run_eval.py --provider openrouter --model openrouter/free --version v3_cp3 --suite $suite --eval-cases "data/eval_$suite.json" --system-prompt "$snapshot/system_prompt.md" --tools "$snapshot/tools.yaml" --runs-dir runs/cp3
        if ($LASTEXITCODE -ne 0) { throw "Eval failed: $suite" }
    }
    # Calls the actual chat CLI: all assistant replies/tool events are generated live.
    $scenario = Get-Content -LiteralPath scripts/cp3_scenarios.json -Raw -Encoding UTF8 | ConvertFrom-Json
    $previousEncoding = $OutputEncoding
    $previousPythonEncoding = $env:PYTHONIOENCODING
    try {
        $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $env:PYTHONIOENCODING = 'utf-8'
        (@($scenario.turns) + @('/exit')) | & $python chat.py --provider openrouter --model openrouter/free --version v3_cp3 --system-prompt "$snapshot/system_prompt.md" --tools "$snapshot/tools.yaml" --history-window 12 --transcripts-dir transcripts/cp3
        if ($LASTEXITCODE -ne 0) { throw 'Chat failed' }
    } finally {
        $OutputEncoding = $previousEncoding
        $env:PYTHONIOENCODING = $previousPythonEncoding
    }
    Write-Output 'Review actual case results and transcript before claiming CP3 complete; exit code alone is not a passing score.'
} finally {
    Pop-Location
}
