param(
    [Parameter(Position=0)]
    [int]$N = 3
)

Write-Host "[parallel] ${N}实例并行，全量用例" -ForegroundColor Cyan
python run_parallel.py -n $N --debug
