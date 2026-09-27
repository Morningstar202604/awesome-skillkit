"""本目录脚本为随包发布的独立脚本（非包结构），测试用相对导入依赖同目录 sys.path。

上游 larksuite/cli 的测试（xml_lint_test.py 等）按“同目录直接运行”设计，
本仓库 CI 用 pytest --import-mode=importlib 收集，需要把本目录加入 sys.path 才能
导入 xml_lint / sxsd_validator / xml_text_overlap_lint 等同级模块。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))