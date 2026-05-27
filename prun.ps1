param(
    [Parameter(Position=0)]
    [string]$Mode = "",

    [Parameter(Position=1)]
    [string]$Arg2 = ""
)

if ($Mode -eq "") {
    Write-Host "[并行] 3实例, 全量, 调试模式（不换包）"
    python run_parallel.py -n 3 --debug
}
elseif ($Mode -eq "setup") {
    $n = if ($Arg2 -ne "") { $Arg2 } else { "3" }
    Write-Host "[并行] 仅启动 $n 台设备，不执行用例"
    python run_parallel.py -n $n --debug -t 0
}
elseif ($Mode -eq "full") {
    if ($Arg2 -eq "") {
        Write-Host "[并行] 3实例, 全量, 默认分支换包"
        python run_parallel.py -n 3
    } else {
        Write-Host "[并行] 3实例, 全量, 分支: $Arg2"
        python run_parallel.py -n 3 --branch $Arg2
    }
}
elseif ($Mode -eq "all") {
    $n = if ($Arg2 -ne "") { $Arg2 } else { "3" }
    Write-Host "[并行] ${n}实例, 全量, 调试模式（不换包）"
    python run_parallel.py -n $n --debug
}
else {
    $n = if ($Arg2 -ne "") { $Arg2 } else { "3" }
    Write-Host "[并行] ${n}实例, ${Mode}个文件, 调试模式（不换包）"
    python run_parallel.py -n $n -t $Mode --debug
}
