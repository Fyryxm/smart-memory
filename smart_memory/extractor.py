#!/usr/bin/env python3
"""
智能记忆提取器 - 多层架构

设计原则：
1. 规则提取 → 零成本（小脑）
2. 本地模型 → 低成本（可选）
3. 云端模型 → 按需调用（大脑）
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import subprocess

# 添加工作目录到路径
WORKSPACE = Path.home() / ".openclaw" / "workspace"
sys.path.insert(0, str(WORKSPACE / "memory"))

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


@dataclass
class ExtractedMemory:
    """提取的记忆"""
    content: str
    category: str  # 偏好/项目/决策/待办/事实
    confidence: float
    source: str  # 提取来源
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "category": self.category,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
            "extracted_at": datetime.now().isoformat()
        }


# ============================================
# 第一层：规则提取器（零成本）
# ============================================

class RuleExtractor:
    """规则提取器 - 小脑核心"""
    
    # 规则定义（更精准）
    RULES = {
        "偏好": [
            (r"我(喜欢|偏好|爱|钟意|倾向)([^。！？\n]{1,20})", 0.8),
            (r"我(不喜欢|讨厌|反感|避免)([^。！？\n]{1,20})", 0.8),
            (r"(不喜欢|讨厌)([^。！？\n]{1,20})", 0.75),
            (r"(素食|吃素|过敏|不?吃[^。！？\n]{1,10})", 0.85),
        ],
        "项目": [
            (r"项目([叫名是])([^。！？\n]{1,20})", 0.85),
            (r"([^。！？\n]{1,20})项目", 0.7),
            (r"目标是([^。！？\n]{1,30})", 0.8),
            (r"(开发|构建|设计)([^。！？\n]{1,30})", 0.65),
        ],
        "决策": [
            (r"(决定|确定|定了)([^。！？\n]{1,30})", 0.85),
            (r"(选择|选用|采用)([^。！？\n]{1,20})", 0.8),
            (r"(就用|确定用|决定用)([^。！？\n]{1,20})", 0.85),
            (r"不再([^。！？\n]{1,20})", 0.75),
        ],
        "待办": [
            (r"(明天|下周|稍后|计划|准备)([^。！？\n]{1,20})", 0.75),
            (r"(需要|要|得)([^。！？\n]{1,15})(一下|完成)", 0.65),
            (r"别忘了([^。！？\n]{1,30})", 0.85),
        ],
        "事实": [
            (r"我(是|叫|在)([^。！？\n]{1,20})", 0.8),
            (r"(服务器|账号|用户名|密码)([^。！？\n]{1,30})", 0.7),
            (r"(用|使用)(本地|云端)([^。！？\n]{0,20})", 0.7),
            (r"([^。！？\n]{1,10})是([^。！？\n]{1,20})(网关|产品|工具)", 0.65),
        ]
    }
    
    # 否定词（降低重要性）
    NEGATION_PATTERNS = [
        r"(测试|试试|临时|暂时|可能|也许|大概)",
    ]
    
    def extract(self, conversation: str) -> List[ExtractedMemory]:
        """从对话中提取记忆"""
        raw_memories = []
        seen_positions = set()  # 避免重叠提取
        
        for category, patterns in self.RULES.items():
            for pattern, confidence in patterns:
                matches = list(re.finditer(pattern, conversation))
                for match in matches:
                    # 检查位置是否已被使用
                    start, end = match.span()
                    if any(start <= p < end or start < p <= e for p, e in seen_positions for p in [start] for e in [end]):
                        continue
                    
                    # 提取内容
                    if match.lastindex and match.lastindex >= 1:
                        groups = [g for g in match.groups() if g]
                        if groups:
                            # 使用最长且有意义的组
                            content = max(groups, key=lambda x: len(x) if len(x) >= 3 else 0)
                        else:
                            content = match.group(0)
                    else:
                        content = match.group(0)
                    
                    content = content.strip()
                    if len(content) < 3:
                        continue
                    
                    # 检查否定词
                    adjusted_confidence = confidence
                    for neg_pattern in self.NEGATION_PATTERNS:
                        if re.search(neg_pattern, content):
                            adjusted_confidence *= 0.5
                            break
                    
                    # 记录位置
                    seen_positions.add((start, end))
                    
                    raw_memories.append({
                        "content": content,
                        "category": category,
                        "confidence": adjusted_confidence,
                        "start": start,
                        "end": end
                    })
        
        # 后处理：合并重叠/相邻的记忆
        memories = self._merge_memories(raw_memories, conversation)
        
        return memories
    
    def _merge_memories(self, raw_memories: List[Dict], conversation: str) -> List[ExtractedMemory]:
        """合并重叠的记忆片段"""
        if not raw_memories:
            return []
        
        # 按位置排序
        sorted_memories = sorted(raw_memories, key=lambda x: x["start"])
        
        # 合并逻辑
        merged = []
        for mem in sorted_memories:
            # 检查是否可以与现有合并
            can_merge = False
            for existing in merged:
                # 如果内容有重叠或相邻，合并
                if (mem["content"] in existing["content"] or 
                    existing["content"] in mem["content"] or
                    abs(mem["start"] - existing["end"]) < 10):
                    # 保留更长的内容
                    if len(mem["content"]) > len(existing["content"]):
                        existing["content"] = mem["content"]
                        existing["end"] = mem["end"]
                    can_merge = True
                    break
            
            if not can_merge:
                merged.append(mem.copy())
        
        # 转换为 ExtractedMemory
        result = []
        for mem in merged:
            result.append(ExtractedMemory(
                content=mem["content"],
                category=mem["category"],
                confidence=mem["confidence"],
                source="rule_extraction"
            ))
        
        return result


# ============================================
# 第二层：本地模型提取器（低成本）
# ============================================

class LocalExtractor:
    """本地模型提取器"""
    
    EXTRACT_PROMPT = """从对话中提取关键事实，输出JSON数组格式。

示例：
对话：我素食，对坚果过敏。项目是聚合兽，目标是商业产品。
输出：[{"content": "素食，对坚果过敏", "category": "偏好"}, {"content": "项目聚合兽，目标是商业产品", "category": "项目"}]

分类：偏好/项目/决策/待办/事实
只提取明确陈述的事实，不要推断。

对话：
{conversation}

输出（JSON数组）："""

    def __init__(self, model: str = "glm-4.7-flash:q4_K_M", endpoint: str = "http://localhost:11434"):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        try:
            resp = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # 检查模型是否存在且可用
                for name in model_names:
                    if self.model.split(":")[0] in name:
                        return True
        except:
            pass
        return False
    
    def extract(self, conversation: str) -> List[ExtractedMemory]:
        """使用本地模型提取"""
        if not self.is_available():
            return []
        
        try:
            prompt = self.EXTRACT_PROMPT.format(conversation=conversation[:1000])
            
            resp = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512
                    }
                },
                timeout=30
            )
            
            if resp.status_code != 200:
                return []
            
            result = resp.json().get("response", "")
            return self._parse_response(result)
            
        except Exception as e:
            print(f"⚠️ 本地模型提取失败: {e}")
            return []
    
    def _parse_response(self, response: str) -> List[ExtractedMemory]:
        """解析模型响应"""
        memories = []
        
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                items = json.loads(json_str)
                
                for item in items:
                    if isinstance(item, dict) and "content" in item:
                        memories.append(ExtractedMemory(
                            content=item.get("content", ""),
                            category=item.get("category", "事实"),
                            confidence=item.get("confidence", 0.8),
                            source="local_model"
                        ))
        except:
            pass
        
        return memories


# ============================================
# 第三层：云端模型提取器（高成本）
# ============================================

class CloudExtractor:
    """云端模型提取器 - 大脑"""
    
    EXTRACT_PROMPT = """从对话中提取关键事实。

规则：
1. 只提取明确陈述的事实，不要推断
2. 每条记忆独立、简洁
3. 分类：偏好/项目/决策/待办/事实
4. 如果用户说"不喜欢"或否定，用"否定偏好"标记

对话：
{conversation}

输出JSON数组格式：[{{"content": "...", "category": "..."}}]"""

    def __init__(self, model: str = "glm-5:cloud", endpoint: str = "http://localhost:11434"):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
    
    def extract(self, conversation: str) -> List[ExtractedMemory]:
        """使用云端模型提取"""
        try:
            prompt = self.EXTRACT_PROMPT.format(conversation=conversation)
            
            resp = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 1024
                    }
                },
                timeout=60
            )
            
            if resp.status_code != 200:
                return []
            
            result = resp.json().get("response", "")
            return self._parse_response(result)
            
        except Exception as e:
            print(f"⚠️ 云端模型提取失败: {e}")
            return []
    
    def _parse_response(self, response: str) -> List[ExtractedMemory]:
        """解析模型响应"""
        memories = []
        
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                items = json.loads(json_str)
                
                for item in items:
                    if isinstance(item, dict) and "content" in item:
                        memories.append(ExtractedMemory(
                            content=item.get("content", ""),
                            category=item.get("category", "事实"),
                            confidence=0.9,  # 云端模型置信度高
                            source="cloud_model"
                        ))
        except:
            pass
        
        return memories


# ============================================
# 冲突检测器
# ============================================

class ConflictDetector:
    """冲突检测器"""
    
    CONTRADICTIONS = [
        ("喜欢", "不喜欢"), ("要", "不要"), ("是", "不是"),
        ("会", "不会"), ("能", "不能"), ("有", "没有"),
        ("用", "不用"), ("需要", "不需要")
    ]
    
    def detect(self, existing: str, new: str) -> Dict:
        """检测冲突"""
        # 完全重复
        if existing.strip() == new.strip():
            return {"has_conflict": True, "action": "skip", "reason": "完全重复"}
        
        # 包含关系
        if new in existing:
            return {"has_conflict": True, "action": "skip", "reason": "已有记录"}
        if existing in new:
            return {"has_conflict": True, "action": "update", "reason": "更新已有记录"}
        
        # 矛盾检测
        for pos, neg in self.CONTRADICTIONS:
            # 提取关键词
            for pattern in [rf"{pos}\s*(.+)", rf"{neg}\s*(.+)"]:
                pos_match = re.search(rf"{pos}\s*(.+)", existing)
                neg_match = re.search(rf"{neg}\s*(.+)", new)
                
                if pos_match and neg_match:
                    if pos_match.group(1).strip() in neg_match.group(1):
                        return {"has_conflict": True, "action": "update", "reason": f"矛盾更新: {pos} -> {neg}"}
        
        return {"has_conflict": False, "action": "add", "reason": "无冲突"}


# ============================================
# 存储层
# ============================================

class MemoryStorage:
    """记忆存储器"""
    
    def __init__(self):
        self.memory_md = WORKSPACE / "MEMORY.md"
        self.memory_dir = WORKSPACE / "memory"
    
    def add_to_memory_md(self, memory: ExtractedMemory) -> bool:
        """添加到 MEMORY.md"""
        content = self.memory_md.read_text(encoding="utf-8") if self.memory_md.exists() else ""
        
        # 检查是否已存在
        if memory.content in content:
            return False
        
        # 找到对应章节
        section_map = {
            "偏好": "## 用户偏好",
            "项目": "## 项目",
            "决策": "## 决策记录",
            "待办": "## 待办",
            "事实": "## 用户信息"
        }
        
        section = section_map.get(memory.category, "## 其他")
        
        # 添加到章节
        lines = content.split("\n")
        new_lines = []
        added = False
        
        for line in lines:
            new_lines.append(line)
            if line.strip() == section and not added:
                new_lines.append(f"- {memory.content}")
                added = True
        
        if not added:
            new_lines.append(f"\n{section}")
            new_lines.append(f"- {memory.content}")
        
        self.memory_md.write_text("\n".join(new_lines), encoding="utf-8")
        return True
    
    def add_to_daily_log(self, memory: ExtractedMemory) -> bool:
        """添加到每日日志"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.memory_dir / f"{today}.md"
        
        self.memory_dir.mkdir(exist_ok=True)
        
        content = ""
        if log_file.exists():
            content = log_file.read_text(encoding="utf-8")
        
        if f"[记忆] {memory.content}" in content:
            return False
        
        entry = f"\n### 记忆提取\n- [记忆] {memory.content}\n  - 分类: {memory.category}\n  - 置信度: {memory.confidence:.0%}\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        
        return True
    
    def search_existing(self, query: str) -> List[str]:
        """搜索现有记忆"""
        results = []
        
        if self.memory_md.exists():
            content = self.memory_md.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if query.lower() in line.lower() and line.strip().startswith("-"):
                    results.append(line.strip("- ").strip())
        
        return results


# ============================================
# 主入口
# ============================================

class SmartMemory:
    """智能记忆系统"""
    
    def __init__(self):
        self.rule_extractor = RuleExtractor()
        self.local_extractor = LocalExtractor()
        self.cloud_extractor = CloudExtractor()
        self.detector = ConflictDetector()
        self.storage = MemoryStorage()
    
    def extract(self, conversation: str, use_cloud: bool = False) -> List[ExtractedMemory]:
        """提取记忆 - 三层架构"""
        memories = []
        
        # 第一层：规则提取（零成本）
        rule_memories = self.rule_extractor.extract(conversation)
        memories.extend(rule_memories)
        
        # 第二层：本地模型（可选，目前内存不够）
        # local_memories = self.local_extractor.extract(conversation)
        # memories.extend(local_memories)
        
        # 第三层：云端模型（按需）
        if use_cloud and len(memories) < 3:  # 只有规则提取不够时才调用云端
            cloud_memories = self.cloud_extractor.extract(conversation)
            # 去重
            for m in cloud_memories:
                if not any(existing.content == m.content for existing in memories):
                    memories.append(m)
        
        return memories
    
    def process_conversation(self, conversation: str, use_cloud: bool = False) -> Dict:
        """处理对话，提取并存储"""
        result = {
            "extracted": [],
            "added": [],
            "skipped": [],
            "updated": []
        }
        
        # 提取
        memories = self.extract(conversation, use_cloud)
        result["extracted"] = [m.to_dict() for m in memories]
        
        # 处理
        for memory in memories:
            existing = self.storage.search_existing(memory.content)
            conflict = self.detector.detect("\n".join(existing) if existing else "", memory.content)
            
            if conflict["action"] == "add":
                self.storage.add_to_memory_md(memory)
                self.storage.add_to_daily_log(memory)
                result["added"].append(memory.content)
            elif conflict["action"] == "update":
                self.storage.add_to_memory_md(memory)
                self.storage.add_to_daily_log(memory)
                result["updated"].append(memory.content)
            else:
                result["skipped"].append(memory.content)
        
        return result
    
    def quick_add(self, content: str, category: str = "事实") -> bool:
        """快速添加"""
        memory = ExtractedMemory(
            content=content,
            category=category,
            confidence=1.0,
            source="manual"
        )
        return self.storage.add_to_memory_md(memory)


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智能记忆提取")
    parser.add_argument("command", choices=["extract", "add", "search", "status"])
    parser.add_argument("--text", "-t", help="对话文本或记忆内容")
    parser.add_argument("--category", "-c", default="事实")
    parser.add_argument("--cloud", action="store_true", help="使用云端模型")
    
    args = parser.parse_args()
    sm = SmartMemory()
    
    if args.command == "status":
        local_ok = sm.local_extractor.is_available()
        print(json.dumps({
            "success": True,
            "local_model": local_ok,
            "model": sm.local_extractor.model,
            "storage": str(sm.storage.memory_md),
            "exists": sm.storage.memory_md.exists()
        }, ensure_ascii=False, indent=2))
    
    elif args.command == "extract":
        if not args.text:
            print(json.dumps({"success": False, "error": "缺少 --text"}))
            exit(1)
        result = sm.process_conversation(args.text, args.cloud)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "add":
        if not args.text:
            print(json.dumps({"success": False, "error": "缺少 --text"}))
            exit(1)
        ok = sm.quick_add(args.text, args.category)
        print(json.dumps({"success": ok, "message": "已添加" if ok else "添加失败"}, ensure_ascii=False))
    
    elif args.command == "search":
        if not args.text:
            print(json.dumps({"success": False, "error": "缺少 --text"}))
            exit(1)
        results = sm.storage.search_existing(args.text)
        print(json.dumps({"success": True, "results": results}, ensure_ascii=False, indent=2))