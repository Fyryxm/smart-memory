#!/usr/bin/env python3
"""
Smart Memory - 规则提取器
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ExtractedMemory:
    """提取的记忆"""
    content: str
    category: str
    confidence: float
    source: str
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


class RuleExtractor:
    """规则提取器 - 小脑核心"""
    
    # 规则定义（简化版）
    RULES = {
        "偏好": [
            (r"(素食|吃素)", 0.85),
            (r"(过敏)", 0.85),
            (r"我(喜欢|偏好|爱)([^。！？，\n]+)", 0.8),
            (r"我(不喜欢|讨厌)([^。！？，\n]+)", 0.8),
        ],
        "项目": [
            (r"项目(是|叫)([^。！？，\n]+)", 0.85),
            (r"目标是([^。！？，\n]+)", 0.8),
        ],
        "决策": [
            (r"(决定|确定|选择)([^。！？，\n]+)", 0.85),
            (r"(就用|决定用)([^。！？，\n]+)", 0.85),
        ],
        "待办": [
            (r"(明天|下周|计划)([^。！？，\n]+)", 0.75),
        ],
        "事实": [
            (r"我(是|叫)([^。！？，\n]+)", 0.8),
        ]
    }
    
    # 否定词
    NEGATION_PATTERNS = [
        r"(测试|试试|临时|暂时|可能|也许|大概)",
    ]
    
    def extract(self, conversation: str) -> List[ExtractedMemory]:
        """从对话中提取记忆"""
        memories = []
        
        for category, patterns in self.RULES.items():
            for pattern, confidence in patterns:
                matches = list(re.finditer(pattern, conversation))
                for match in matches:
                    # 提取内容
                    if match.groups():
                        # 取最长的组
                        groups = [g for g in match.groups() if g]
                        content = max(groups, key=len) if groups else match.group(0)
                    else:
                        content = match.group(0)
                    
                    content = content.strip()
                    if len(content) < 2:  # 至少2个字符
                        continue
                    
                    # 检查否定词
                    adjusted_confidence = confidence
                    for neg_pattern in self.NEGATION_PATTERNS:
                        if re.search(neg_pattern, content):
                            adjusted_confidence *= 0.5
                            break
                    
                    # 去重
                    if any(m.content == content for m in memories):
                        continue
                    
                    memories.append(ExtractedMemory(
                        content=content,
                        category=category,
                        confidence=adjusted_confidence,
                        source="rule_extraction"
                    ))
        
        return memories


# 测试
if __name__ == "__main__":
    extractor = RuleExtractor()
    
    test_cases = [
        "我素食，对坚果过敏",
        "项目叫聚合兽",
        "决定用本地模型",
        "明天要部署",
        "我是翔哥",
    ]
    
    for text in test_cases:
        memories = extractor.extract(text)
        print(f"\n'{text}':")
        for m in memories:
            print(f"  [{m.category}] {m.content} ({m.confidence:.0%})")