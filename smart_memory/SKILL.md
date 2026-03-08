# Smart Memory Skill

智能记忆系统 - 从对话中自动提取、存储、检索记忆。

## 核心功能

1. **自动提取** - 从对话中提取关键事实（偏好、项目、决策、待办）
2. **零成本** - 纯规则提取，无需调用 LLM
3. **冲突检测** - 自动检测重复/矛盾记忆
4. **本地存储** - Markdown 文件

## 使用方式

### Python API

```python
from smart_memory import RuleExtractor

# 初始化
extractor = RuleExtractor()

# 从对话提取
memories = extractor.extract("我素食，对坚果过敏。项目叫聚合兽。")

for mem in memories:
    print(f"[{mem.category}] {mem.content}")
# 输出:
# [偏好] 素食
# [偏好] 过敏
# [项目] 聚合兽
```

### CLI

```bash
# 提取
python -m smart_memory extract '{"conversation": "我素食，对坚果过敏"}'

# 状态
python -m smart_memory status
```

## 记忆分类

| 类型 | 示例 | 规则 |
|------|------|------|
| 偏好 | "我素食" | 素食/过敏/喜欢/讨厌 |
| 项目 | "项目叫聚合兽" | 项目是/目标是 |
| 决策 | "决定用本地模型" | 决定/选择/确定 |
| 待办 | "明天要部署" | 明天/下周/计划 |
| 事实 | "我是翔哥" | 我是/我叫 |

## 测试结果

```
基础提取:   ✓ 5/5 通过
分类准确率: ✓ 100% (9/9)
性能测试:   ✓ < 1ms
```

## 架构

```
对话输入
    ↓
┌─────────────────────────────────┐
│  规则提取器（RuleExtractor）     │
│  - 纯正则匹配，零成本            │
│  - 5类：偏好/项目/决策/待办/事实  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  冲突检测                        │
│  - 重复跳过                      │
│  - 矛盾更新                      │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  存储                            │
│  - MEMORY.md                    │
│  - 或集成到统一记忆系统           │
└─────────────────────────────────┘
```

## 与 OpenClaw 集成

smart-memory 已链接到 OpenClaw 的统一记忆系统：

```python
from memory.unified import UnifiedMemorySystem

# 统一入口
memory = UnifiedMemorySystem()

# 从对话自动提取 + 存储
result = memory.process("我素食，对坚果过敏。项目是聚合兽。")
# → {"extracted": [...], "stored": [...]}
```

## 文件位置

- GitHub: https://github.com/Fyryxm/smart-memory
- Skills: ~/.openclaw/workspace/skills/smart-memory/
- Unified: ~/.openclaw/workspace/memory/unified/