# Smart Memory

智能记忆系统 - 从对话中自动提取、存储、检索记忆，零成本实现 Mem0 核心功能。

## 核心特性

- 🧠 **自动提取** - 从对话中提取关键事实（偏好、项目、决策、待办）
- 💰 **零成本** - 纯规则提取，无需调用 LLM
- 🔄 **冲突检测** - 自动检测重复/矛盾记忆
- 💾 **本地存储** - Markdown 文件 + 可选向量搜索
- 🔌 **易于集成** - 简单 CLI 和 Python API

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

# 安装依赖（可选，用于向量搜索）
pip install requests
```

## 快速开始

### CLI 使用

```bash
# 检查状态
python smart_memory/cli.py status

# 从对话提取记忆
python smart_memory/cli.py extract '{"conversation": "我素食，对坚果过敏。项目是聚合兽，目标是商业产品。"}'

# 快速添加记忆
python smart_memory/cli.py add '{"content": "翔哥偏好本地模型", "category": "偏好"}'

# 搜索记忆
python smart_memory/cli.py search '{"query": "偏好"}'

# 列出所有记忆
python smart_memory/cli.py list
```

### Python API

```python
from smart_memory import SmartMemory

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
```

## 记忆分类

| 类型 | 示例 | 提取规则 |
|------|------|---------|
| **偏好** | "我喜欢 Python" | 我喜欢/偏好/讨厌... |
| **项目** | "项目叫聚合兽" | 项目是/目标是... |
| **决策** | "决定用本地模型" | 决定/选择/确定... |
| **待办** | "明天要部署" | 明天/下周/计划... |
| **事实** | "服务器用户是 cyber_rex44" | 是/叫/在... |

## 配置

```python
# 默认配置
SmartMemory(
    memory_dir="~/.openclaw/workspace/memory",  # 记忆存储目录
    memory_file="MEMORY.md",                    # 长期记忆文件
)
```

## 与 Mem0 对比

| 特性 | Mem0 | Smart Memory |
|------|------|--------------|
| 提取方式 | LLM（每次 ~$0.001） | **规则（零成本）** |
| 冲突检测 | LLM 判断 | 规则检测 |
| 存储位置 | 云端/自托管 | 本地文件 |
| 向量搜索 | 必须 | 可选 |
| 离线可用 | ❌ | **✅** |
| 成本 | $0.001/次 | **$0** |

## 适用场景

- ✅ AI 助手的长期记忆
- ✅ 对话历史自动整理
- ✅ 用户偏好追踪
- ✅ 项目上下文管理
- ✅ 本地优先/离线场景

## 扩展

### 添加自定义提取规则

```python
from smart_memory import RuleExtractor

extractor = RuleExtractor()
extractor.RULES["自定义分类"] = [
    (r"自定义模式", 0.8),
]
```

### 集成向量搜索

```python
# 需要安装 chromadb 或使用现有向量库
# smart_memory 支持与 Chroma 集成
```

## 项目结构

```
smart-memory/
├── smart_memory/
│   ├── __init__.py
│   ├── extractor.py      # 核心提取器
│   ├── storage.py        # 存储层
│   └── cli.py            # 命令行入口
├── README.md
├── LICENSE
└── pyproject.toml
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

灵感来源于 [Mem0](https://github.com/mem0ai/mem0)，但专注于零成本本地优先的场景。