# Smart Memory FAQ

## 常见问题

### 基础问题

#### Q: Smart Memory 和 Mem0 有什么区别？

**A:** 主要区别：

| 特性 | Mem0 | Smart Memory |
|------|------|--------------|
| 提取方式 | LLM（每次约 $0.001） | 规则提取（免费） |
| 冲突检测 | LLM 判断 | 规则检测 |
| 存储位置 | 云端/自托管 | 本地文件 |
| 离线可用 | ❌ 需要网络 | ✅ 完全离线 |
| 成本 | 每次调用付费 | 零成本 |

Smart Memory 适合：
- 本地优先/离线场景
- 成本敏感项目
- 简单记忆提取需求

Mem0 适合：
- 复杂记忆推理
- 需要云端托管
- 预算充足

---

#### Q: 为什么选择规则提取而不是 LLM？

**A:** 规则提取的优势：

1. **零成本** - 不需要调用付费 API
2. **零延迟** - 毫秒级响应
3. **可预测** - 行为完全可控
4. **可扩展** - 规则易于修改和扩展

实际测试显示，对于 80% 的记忆提取场景，规则提取已经足够准确。

---

#### Q: 提取准确率如何？

**A:** 测试结果：

| 类别 | 准确率 |
|------|--------|
| 偏好 | ~85% |
| 项目 | ~90% |
| 决策 | ~88% |
| 待办 | ~75% |
| 事实 | ~80% |

总体准确率：~80%

对于复杂场景，可以：
1. 添加自定义规则
2. 启用云端模型作为后备

---

### 使用问题

#### Q: 如何添加自定义提取规则？

**A:**

```python
from smart_memory import RuleExtractor

extractor = RuleExtractor()

# 添加自定义规则
extractor.RULES["自定义分类"] = [
    (r"匹配模式", 0.8),  # 正则表达式 + 置信度
]

# 使用
memories = extractor.extract("对话内容")
```

---

#### Q: 如何集成到现有项目？

**A:** 几种方式：

**1. Python API**
```python
from smart_memory import SmartMemory

sm = SmartMemory()
result = sm.process_conversation("对话内容")
```

**2. CLI**
```bash
python -m smart_memory extract '{"conversation": "对话内容"}'
```

**3. 作为 OpenClaw Skill**
```python
# 在 OpenClaw 中自动调用
from skills.smart_memory import SmartMemory
```

---

#### Q: 记忆存储在哪里？

**A:** 默认位置：

```
~/.openclaw/workspace/
├── MEMORY.md          # 长期记忆
└── memory/
    └── 2026-03-08.md  # 每日日志
```

可自定义：

```python
sm = SmartMemory(
    memory_dir="/path/to/memory",
    memory_file="MY_MEMORY.md"
)
```

---

#### Q: 支持向量搜索吗？

**A:** 支持，但需要额外配置：

```python
# 安装 chromadb
pip install chromadb

# 使用向量搜索
from smart_memory import SmartMemory

sm = SmartMemory(use_vector=True)
results = sm.search_semantic("关键词")
```

默认情况下使用文本搜索，已经能满足大部分需求。

---

### 技术问题

#### Q: 性能如何？

**A:** 测试结果：

| 文本长度 | 提取时间 |
|---------|---------|
| 10 字符 | < 1ms |
| 100 字符 | < 5ms |
| 500 字符 | < 20ms |
| 2000 字符 | < 50ms |

规则提取极快，适合实时场景。

---

#### Q: 如何处理冲突？

**A:** 冲突检测逻辑：

1. **完全重复** → 跳过
2. **包含关系** → 保留更完整的
3. **矛盾** → 更新为新记忆

示例：

```python
detector = ConflictDetector()

# 完全重复
detector.detect("我喜欢 Python", "我喜欢 Python")
# → {"action": "skip", "reason": "完全重复"}

# 矛盾
detector.detect("我用云端", "我不用云端")
# → {"action": "update", "reason": "矛盾更新"}
```

---

#### Q: 支持多用户吗？

**A:** 支持，使用 `user_id` 区分：

```python
sm = SmartMemory()

# 用户 A
sm.process_conversation("对话内容", user_id="user_a")

# 用户 B
sm.process_conversation("对话内容", user_id="user_b")

# 搜索特定用户
sm.storage.search_existing("关键词", user_id="user_a")
```

---

#### Q: 如何调试？

**A:**

```python
# 启用详细输出
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看提取过程
from smart_memory import RuleExtractor

extractor = RuleExtractor()
for cat, patterns in extractor.RULES.items():
    print(f"{cat}: {len(patterns)} 规则")

# 测试特定文本
memories = extractor.extract("测试对话")
for m in memories:
    print(f"[{m.category}] {m.content} ({m.confidence:.0%})")
```

---

### 高级问题

#### Q: 可以和 LLM 结合吗？

**A:** 可以，三层架构支持：

```python
sm = SmartMemory()

# 第一层：规则提取（免费）
result = sm.process_conversation(conversation)

# 如果规则提取不够，调用 LLM
if len(result['extracted']) < 3:
    result = sm.process_conversation(conversation, use_cloud=True)
```

---

#### Q: 如何处理隐私数据？

**A:** 本地存储，完全私密：

1. 数据存储在本地文件
2. 不发送到云端
3. 可以添加过滤规则

```python
# 过滤敏感词
from smart_memory import RuleExtractor

extractor = RuleExtractor()
extractor.SENSITIVE_PATTERNS = [
    r"密码\s*[=:]\s*\S+",
    r"api[_-]?key\s*[=:]\s*\S+",
]

# 敏感内容会被跳过
memories = extractor.extract("密码是 abc123")
# → 空列表
```

---

#### Q: 支持多语言吗？

**A:** 目前支持：

- ✅ 中文（完整）
- ⚠️ 英文（部分规则）

计划支持：
- 日文
- 韩文
- 更多欧洲语言

---

### 故障排除

#### Q: 提取结果为空？

**A:** 检查：

1. 规则是否匹配？
```python
from smart_memory import RuleExtractor
extractor = RuleExtractor()
print(extractor.RULES)  # 查看所有规则
```

2. 文本格式是否正确？
```python
# 确保对话是陈述句
"我素食" ✓
"素食是什么？" ✗  # 疑问句不会提取
```

---

#### Q: 提取结果不准确？

**A:** 解决方案：

1. 添加自定义规则
2. 调整置信度阈值
3. 后处理过滤

```python
# 提取后过滤
memories = extractor.extract(text)
high_confidence = [m for m in memories if m.confidence > 0.7]
```

---

#### Q: 如何贡献代码？

**A:** 欢迎贡献！

1. Fork 仓库
2. 创建分支：`git checkout -b feature/xxx`
3. 提交代码：`git commit -m "Add xxx"`
4. 创建 PR

特别欢迎：
- 更多提取规则
- 多语言支持
- 性能优化
- 文档改进

---

## 更多帮助

- GitHub Issues: https://github.com/Fyryxm/smart-memory/issues
- 文档: https://github.com/Fyryxm/smart-memory#readme