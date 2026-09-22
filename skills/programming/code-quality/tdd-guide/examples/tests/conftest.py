# -*- coding: utf-8 -*-
"""让示例测试可被任意位置的 pytest 收集：把 ../src 加进 sys.path。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
