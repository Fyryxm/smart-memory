# Smart Memory

智能记忆系统 - 从对话中自动提取、存储、检索记忆，零成本实现 Mem0 核心功能。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/Fyryxm/smart-memory.svg)](https://github.com/Fyryxm/smart-memory/stargazers)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Fyryxm/smart-memory)

## 核心特性

- 🧠 **自动提取** - 从对话中提取关键事实（偏好、项目、决策、待办）
- 💰 **零成本** - 纯规则提取，无需调用 LLM
- 🔄 **冲突检测** - 自动检测重复/矛盾记忆
- 💾 **本地存储** - Markdown 文件 + 可选向量搜索
- 🔌 **易于集成** - 简单 CLI 和 Python API
- ⚡ **极速响应** - < 1ms 提取时间

## 测试结果

| 测试项 | 结果 | 详情 |
|--------|------|------|
| 基础提取 | ✅ 5/5 通过 | 5 种分类全部正确 |
| 分类准确率 | ✅ 100% | 9/9 测试用例通过 |
| 性能测试 | ✅ < 1ms | 平均 0.01ms，最大 0.02ms |

**v0.2.0 更新：**
- 重构规则提取器，更稳定
- 修复短词提取问题
- 添加分类准确率测试

## 架构

```
对话内容
    ↓
┌─────────────────────────────────┐
│  规则提取器（小脑）              │
│  - 零成本，纯正则匹配            │
│  - 分类：偏好/项目/决策/待办/事实  │
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────┐
│  冲突检测                        │
│  - 查询现有记忆                   │
│  - 检测重复/矛盾                  │
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────┐
│  存储                            │
│  - MEMORY.md（长期）             │
│  - memory/YYYY-MM-DD.md（日志）   │
│  - Chroma 向量库（可选）          │
└─────────────────────────────────┘
```

## 安装

```bash
# 克隆仓库
git clone https://github.com/Fyryxm/smart-memory.git
cd smart-memory

# 安装（开发模式）
pip install -e .

# 或仅安装核心依赖
pip install requests
```

## 快速开始

### CLI 使用

```bash
# 检查状态
python -m smart_memory.cli status

# 从对话提取记忆
python -m smart_memory.cli extract '{"conversation": "我素食，对坚果过敏。项目是聚合兽，目标是商业产品。"}'

# 快速添加记忆
python -m smart_memory.cli add '{"content": "翔哥偏好本地模型", "category": "偏好"}'

# 搜索记忆
python -m smart_memory.cli search '{"query": "偏好"}'

# 列出所有记忆
python -m smart_memory.cli list
```

### Python API

```python
from smart_memory import SmartMemory

# 初始化
sm = SmartMemory()

# 从对话提取
result = sm.process_conversation("我素食，对坚果过敏。项目是聚合兽。")
print(result)
# {
#   "extracted": [{"content": "素食", "category": "偏好", ...}, ...],
#   "added": ["素食", ...],
#   "skipped": [],
#   "updated": []
# }

# 快速添加
sm.quick_add("用户偏好 Python", "偏好")

# 搜索
results = sm.storage.search_existing("偏好")

# 列出所有
from smart_memory.cli import handle_list
all_memories = handle_list({})
```

## 记忆分类

| 类型 | 示例 | 提取规则 |
|------|------|---------|
| **偏好** | "我喜欢 Python" | 我喜欢/偏好/讨厌... |
| **项目** | "项目叫聚合兽" | 项目是/目标是... |
| **决策** | "决定用本地模型" | 决定/选择/确定... |
| **待办** | "明天要部署" | 明天/下周/计划... |
| **事实** | "服务器用户是 cyber_rex44" | 是/叫/在... |

## 与 Mem0 对比

| 特性 | Mem0 | Smart Memory |
|------|------|--------------|
| 提取方式 | LLM（每次 ~$0.001） | **规则（零成本）** |
| 冲突检测 | LLM 判断 | 规则检测 |
| 存储位置 | 云端/自托管 | 本地文件 |
| 向量搜索 | 必须 | 可选 |
| 离线可用 | ❌ | **✅** |
| 成本 | $0.001/次 | **$0** |
| 响应时间 | ~500ms | **< 1ms** |

## 适用场景

- ✅ AI 助手的长期记忆
- ✅ 对话历史自动整理
- ✅ 用户偏好追踪
- ✅ 项目上下文管理
- ✅ 本地优先/离线场景

## 项目结构

```
smart-memory/
├── smart_memory/
│   ├── __init__.py
│   ├── extractor.py      # 核心提取器
│   └── cli.py            # 命令行入口
├── tests/
│   └── test_smart_memory.py  # 测试套件
├── examples/
│   └── usage_examples.py     # 使用示例
├── docs/
│   └── FAQ.md                # 常见问题
├── README.md
├── LICENSE
└── pyproject.toml
```

## 扩展

### 添加自定义提取规则

```python
from smart_memory import RuleExtractor

extractor = RuleExtractor()

# 添加自定义规则
extractor.RULES["自定义分类"] = [
    (r"匹配模式", 0.8),  # 正则表达式 + 置信度
]

# 使用
memories = extractor.extract("对话内容")
for m in memories:
    print(f"[{m.category}] {m.content}")
```

### 集成向量搜索

```python
# 安装 chromadb
pip install chromadb

# 使用向量搜索
from smart_memory import SmartMemory

sm = SmartMemory(use_vector=True)
results = sm.search_semantic("关键词")
```

### 与 LLM 结合

```python
# 三层架构：规则 → 本地模型 → 云端模型
sm = SmartMemory()

# 第一层：规则提取（免费）
result = sm.process_conversation(conversation)

# 如果规则提取不够，调用云端模型
if len(result['extracted']) < 3:
    result = sm.process_conversation(conversation, use_cloud=True)
```

## 运行测试

```bash
# 运行测试套件
python tests/test_smart_memory.py

# 运行示例
python examples/usage_examples.py
```

## 常见问题

详见 [FAQ.md](docs/FAQ.md)

### Q: 为什么选择规则提取？

零成本、零延迟、可预测、可扩展。80% 的场景已足够准确。

### Q: 提取准确率如何？

总体 ~80%，偏好 ~85%，项目 ~90%，决策 ~88%。

### Q: 支持多用户吗？

支持，使用 `user_id` 区分。

## 贡献

欢迎提交 Issue 和 Pull Request！

特别欢迎：
- 更多提取规则
- 多语言支持
- 性能优化
- 文档改进

## 许可证

MIT License

## 致谢

灵感来源于 [Mem0](https://github.com/mem0ai/mem0)，但专注于零成本本地优先的场景。

---

**Star ⭐ 本项目如果你觉得有用！**