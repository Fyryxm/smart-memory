#!/usr/bin/env python3
"""
Smart Memory 使用示例
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_memory import SmartMemory


def example_basic_extraction():
    """示例1：基础记忆提取"""
    print("\n" + "="*50)
    print("示例1：基础记忆提取")
    print("="*50)
    
    sm = SmartMemory()
    
    conversation = """
    翔哥：我素食，对坚果过敏。项目叫聚合兽，是通用API网关，目标是商业产品。
    决定用本地模型，不用云端的。
    """
    
    result = sm.process_conversation(conversation)
    
    print(f"\n提取结果：")
    for mem in result["extracted"]:
        print(f"  [{mem['category']}] {mem['content']} (置信度: {mem['confidence']:.0%})")
    
    print(f"\n新增: {len(result['added'])} 条")
    print(f"跳过: {len(result['skipped'])} 条")


def example_preference_extraction():
    """示例2：偏好提取"""
    print("\n" + "="*50)
    print("示例2：偏好提取")
    print("="*50)
    
    sm = SmartMemory()
    
    conversations = [
        "我喜欢 Python，不喜欢 JavaScript",
        "我偏好本地部署，避免用云端服务",
        "习惯用 Vim 编辑器",
    ]
    
    for conv in conversations:
        result = sm.process_conversation(conv)
        for mem in result["extracted"]:
            if mem["category"] == "偏好":
                print(f"  ✓ {mem['content']}")


def example_project_extraction():
    """示例3：项目信息提取"""
    print("\n" + "="*50)
    print("示例3：项目信息提取")
    print("="*50)
    
    sm = SmartMemory()
    
    conversation = """
    我们在做聚合兽项目，这是一个通用的 API 网关。
    目标是做成商业产品，定价 $29-499/月 订阅。
    技术栈用 Python + FastAPI。
    """
    
    result = sm.process_conversation(conversation)
    
    print("\n项目相关记忆：")
    for mem in result["extracted"]:
        if mem["category"] in ["项目", "决策"]:
            print(f"  [{mem['category']}] {mem['content']}")


def example_conflict_detection():
    """示例4：冲突检测"""
    print("\n" + "="*50)
    print("示例4：冲突检测")
    print("="*50)
    
    sm = SmartMemory()
    
    # 先添加一条记忆
    print("第一次对话：")
    result1 = sm.process_conversation("我喜欢用云端模型")
    print(f"  新增: {result1['added']}")
    
    # 再添加冲突记忆
    print("\n第二次对话（矛盾）：")
    result2 = sm.process_conversation("我不用云端模型了，改用本地模型")
    print(f"  新增: {result2['added']}")
    print(f"  更新: {result2['updated']}")


def example_quick_add():
    """示例5：快速添加"""
    print("\n" + "="*50)
    print("示例5：快速添加记忆")
    print("="*50)
    
    sm = SmartMemory()
    
    # 直接添加
    sm.quick_add("用户名：翔哥", "事实")
    sm.quick_add("服务器用户：cyber_rex44", "事实")
    sm.quick_add("偏好：本地模型优先", "偏好")
    
    print("已快速添加 3 条记忆")


def example_search():
    """示例6：搜索记忆"""
    print("\n" + "="*50)
    print("示例6：搜索记忆")
    print("="*50)
    
    sm = SmartMemory()
    
    # 先添加一些记忆
    sm.quick_add("偏好 Python 编程", "偏好")
    sm.quick_add("项目聚合兽用 Python", "项目")
    sm.quick_add("服务器用 Python 3.10", "事实")
    
    # 搜索
    results = sm.storage.search_existing("Python")
    
    print("\n搜索 'Python' 结果：")
    for r in results:
        print(f"  - {r}")


def example_real_conversation():
    """示例7：真实对话场景"""
    print("\n" + "="*50)
    print("示例7：真实对话场景")
    print("="*50)
    
    sm = SmartMemory()
    
    # 模拟真实对话
    conversation = """
    用户：我最近在做聚合兽项目，这是一个 API 聚合网关。
    目标是做成 SaaS 产品赚钱，定价 $29-499/月。
    
    我编程 0 基础，需要有人帮我写代码。
    
    我偏好用本地模型，不喜欢把数据发到云端。
    服务器用户是 cyber_rex44。
    
    对了，我对坚果过敏，素食主义者。
    """
    
    result = sm.process_conversation(conversation)
    
    print("\n提取的记忆：")
    print("-" * 40)
    
    # 按分类显示
    categories = {}
    for mem in result["extracted"]:
        cat = mem["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(mem["content"])
    
    for cat, items in sorted(categories.items()):
        print(f"\n{cat}:")
        for item in items:
            print(f"  • {item}")


def example_list_all():
    """示例8：列出所有记忆"""
    print("\n" + "="*50)
    print("示例8：列出所有记忆")
    print("="*50)
    
    from smart_memory.cli import handle_list
    
    result = handle_list({})
    
    if result["success"] and result["memories"]:
        print(f"\n共 {result['count']} 条记忆：")
        
        current_section = None
        for mem in result["memories"]:
            if mem["section"] != current_section:
                current_section = mem["section"]
                print(f"\n{current_section}:")
            print(f"  • {mem['content']}")
    else:
        print("\n暂无记忆")


if __name__ == "__main__":
    print("="*50)
    print("Smart Memory 使用示例")
    print("="*50)
    
    example_basic_extraction()
    example_preference_extraction()
    example_project_extraction()
    example_conflict_detection()
    example_quick_add()
    example_search()
    example_real_conversation()
    # example_list_all()  # 需要有 MEMORY.md
    
    print("\n" + "="*50)
    print("示例完成！")
    print("="*50)