# 模块卡片：hivi_network_flutter_core（初步版——基于 L1/L2 与分诊证据，考古任务待补全）
- 基线 commit：dev@402853ab964f026761ba63130f495b9d213ea8b5
- 检出：E:\SwanAppeposlutter\hivi_network_flutter_core
- 已知组成：core/platform_ports（AppSystemPort、LocalPlaybackPort 等端口）、packages/hivi_upnp_core、多平台通道 stub（OHOS/iOS/Android）
- 测试现状：自带 2465 测试，43 失败（分诊见 002 矩阵）；analyze 328 诊断（280 error 主因 package:test 依赖边界）
- 已知坑（分诊结论）：嵌套包测试依赖边界破坏；测试替身缺接口实现；平台通道 stub 未显式化；3 处时序超时
- 考古任务ID：（待排）
