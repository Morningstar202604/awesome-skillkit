# ml-pipeline · 全量测试过程全量记录

- 域: paper | 时间: 2026-09-20 16:48:49 UTC
- 结果: **pass** | 真实可运行 ML 模型：双模型 CV + 测试准确率 + 混淆矩阵 + 模型落盘

### 思维链 / 过程
paper 域挑 ml-pipeline（建模）。要「复杂+可运行」→ 真实写一个鸢尾花分类器：加载 sklearn 数据集 → 划分 → 训练逻辑回归/随机森林 → 交叉验证 + 混淆矩阵 → 保存模型。真跑一遍，输出准确率 + 混淆矩阵。边界：缺 sklearn 给纯 numpy 降级说明。

**产出文件**: `iris_model.py` — 可运行 ML 模型（鸢尾花）

### 执行
```
$ python C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\tests\_full_test_artifacts\paper\ml-pipeline\iris_model.py
```

**退出码**: 0

**stdout**:
```
LogReg: cv5=0.971 test_acc=0.933 conf_matrix=[[15, 0, 0], [0, 14, 1], [0, 2, 13]]
RF: cv5=0.952 test_acc=0.911 conf_matrix=[[15, 0, 0], [0, 14, 1], [0, 3, 12]]
BEST=LogReg cv=0.971 saved=model_LogReg.pkl
```

### 思维链 / 过程
输出:
LogReg: cv5=0.971 test_acc=0.933 conf_matrix=[[15, 0, 0], [0, 14, 1], [0, 2, 13]]
RF: cv5=0.952 test_acc=0.911 conf_matrix=[[15, 0, 0], [0, 14, 1], [0, 3, 12]]
BEST=LogReg cv=0.971 saved=model_LogReg.pkl

## 遇到的问题（全量记录）
- （无）

## 缺失 / 更优方案备忘
- 可接真实数据源 + 超参搜索 + SHAP 解释；当前鸢尾花足以验证可运行性。

## 交付物清单（全部保留，不删除）
- `iris_model.py`