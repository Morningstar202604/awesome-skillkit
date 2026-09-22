# 设计说明

hello_stats.py 演示"合格脚本"的五条纪律：stdlib-only、__main__ guard、
--help 自描述、--json 机器可读、错误路径退出码 2 + 可读提示。

golden 输出（expected_outputs/）由 `--json` 生成，供 script_tester 比对。
