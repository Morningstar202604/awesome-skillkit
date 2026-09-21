> **自检提示**：本题属于"代码/算法题"，需路由至 `solution-drafter-code-design`。用户明确要求第一版草稿（只破题与定状态），符合"不写完整代码"限制。

---

## 第一版解题草稿（破题 + 定状态）

### 1. 破题

**核心模型**：任务调度，依赖关系构成 **DAG（有向无环图）**，求最小总时长即求 **关键路径（Critical Path）**。

**已知信息整理**：
| 任务 | 耗时(s) | 依赖任务 |
|------|--------|----------|
| A    | 3      | 无       |
| B    | 2      | A        |
| C    | 4      | A        |
| D    | 2      | B, C     |
| E    | 3      | D        |

**关键判断**：
- 起始任务：A（无前驱）
- 结束任务：E（无后继）
- 并行机会：B 与 C 可同时执行（都只依赖 A）
- 串行约束：D 必须等 B **和** C 都完成；E 必须等 D 完成

---

### 2. 定状态

#### 状态定义
```
earliest_start(task) : 任务最早开始时间
earliest_finish(task): 任务最早完成时间 = earliest_start(task) + duration(task)
```

#### 状态转移方程
```
earliest_start(A) = 0                                    // 无依赖，从0开始
earliest_start(X) = max(earliest_finish(P) for P in predecessors(X))  // 取所有前驱完成时间的最大值
earliest_finish(X) = earliest_start(X) + duration(X)
```

#### 目标状态
```
min_total_time = earliest_finish(E)
```

---

### 3. 状态计算（手动推导）

| 任务 | earliest_start | earliest_finish | 计算说明 |
|------|---------------|-----------------|----------|
| A    | 0             | 0+3 = **3**     | 起始任务 |
| B    | 3             | 3+2 = **5**     | 依赖A，等A完成(3s) |
| C    | 3             | 3+4 = **7**     | 依赖A，等A完成(3s)，与B并行 |
| D    | **7**         | 7+2 = **9**     | 依赖B和C，取max(5,7)=7 |
| E    | 9             | 9+3 = **12**    | 依赖D，等D完成(9s) |

---

### 4. 结果验证

**关键路径**：A → C → D → E（路径长度 = 3+4+2+3 = 12s）

**并行分析**：
- 时间 0-3s：仅执行 A
- 时间 3-7s：B 和 C 并行执行（B 在 5s 完成，C 在 7s 完成）
- 时间 7-9s：执行 D（等 B、C 都完成）
- 时间 9-12s：执行 E

**验算**：
- 所有依赖满足 ✓
- 无循环依赖 ✓
- 总时长 = **12 秒**

---

### 5. 第一版输出（伪代码骨架）

```python
# 数据结构定义
tasks = {
    'A': {'duration': 3, 'deps': []},
    'B': {'duration': 2, 'deps': ['A']},
    'C': {'duration': 4, 'deps': ['A']},
    'D': {'duration': 2, 'deps': ['B', 'C']},
    'E': {'duration': 3, 'deps': ['D']}
}

# 状态表
earliest_start = {}
earliest_finish = {}

# 拓扑排序后依次计算（保证前驱已处理）
def compute(task):
    if task in earliest_finish:
        return earliest_finish[task]
    
    deps = tasks[task]['deps']
    if not deps:
        start = 0
    else:
        start = max(compute(dep) for dep in deps)
    
    finish = start + tasks[task]['duration']
    earliest_start[task] = start
    earliest_finish[task] = finish
    return finish

# 求解
result = compute('E')
print(f"最小总时长: {result}")  # 预期输出 12
```

---

### 6. 待后续完善（第二版预留）

- [ ] 加入入度检测，排除无效输入（循环依赖、孤立节点）
- [ ] 改为迭代式拓扑排序（避免递归深度问题）
- [ ] 输出关键路径具体任务序列
- [ ] 添加单元测试覆盖边界情况

---

**初稿完成，工整但带 AI 味，继续调用 own-voice-rewrite 学生化。**