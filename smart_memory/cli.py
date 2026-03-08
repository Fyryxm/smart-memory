#!/usr/bin/env python3
"""
Smart Memory CLI - Command line interface
"""

import json
import sys
from pathlib import Path
from typing import Dict

# 添加当前目录到路径
PACKAGE_DIR = Path(__file__).parent
sys.path.insert(0, str(PACKAGE_DIR))

from .extractor import SmartMemory


def handle_extract(params: Dict) -> Dict:
    """处理提取请求"""
    conversation = params.get("conversation", "")
    use_cloud = params.get("use_cloud", False)
    
    if not conversation:
        return {"success": False, "error": "缺少 conversation 参数"}
    
    sm = SmartMemory()
    result = sm.process_conversation(conversation, use_cloud)
    
    return {
        "success": True,
        "result": result,
        "message": f"提取 {len(result['extracted'])} 条，新增 {len(result['added'])} 条，跳过 {len(result['skipped'])} 条"
    }


def handle_add(params: Dict) -> Dict:
    """处理添加请求"""
    content = params.get("content", "")
    category = params.get("category", "事实")
    
    if not content:
        return {"success": False, "error": "缺少 content 参数"}
    
    sm = SmartMemory()
    success = sm.quick_add(content, category)
    
    return {
        "success": success,
        "message": f"✅ 已添加: {content}" if success else "❌ 添加失败（可能已存在）"
    }


def handle_search(params: Dict) -> Dict:
    """处理搜索请求"""
    query = params.get("query", "")
    if not query:
        return {"success": False, "error": "缺少 query 参数"}
    
    sm = SmartMemory()
    results = sm.storage.search_existing(query)
    
    return {
        "success": True,
        "results": results,
        "count": len(results),
        "message": f"找到 {len(results)} 条相关记忆"
    }


def handle_list(params: Dict) -> Dict:
    """处理列表请求"""
    memory_md = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
    
    if not memory_md.exists():
        return {"success": True, "memories": [], "message": "MEMORY.md 不存在"}
    
    content = memory_md.read_text(encoding="utf-8")
    
    memories = []
    current_section = "其他"
    
    for line in content.split("\n"):
        if line.startswith("## "):
            current_section = line[3:].strip()
        elif line.startswith("- ") and not line.startswith("  -"):
            memories.append({
                "content": line[2:].strip(),
                "section": current_section
            })
    
    return {
        "success": True,
        "memories": memories,
        "count": len(memories),
        "message": f"共 {len(memories)} 条记忆"
    }


def handle_status(params: Dict) -> Dict:
    """检查系统状态"""
    sm = SmartMemory()
    
    local_available = sm.local_extractor.is_available()
    
    return {
        "success": True,
        "status": {
            "rule_extractor": {
                "available": True,
                "cost": "free"
            },
            "local_model": {
                "available": local_available,
                "model": sm.local_extractor.model,
                "endpoint": sm.local_extractor.endpoint
            },
            "storage": {
                "memory_md": str(sm.storage.memory_md),
                "exists": sm.storage.memory_md.exists()
            }
        },
        "message": "系统就绪" if local_available else "规则提取器可用，本地模型不可用"
    }


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "需要指定命令",
            "usage": "smart-memory <command> [params]",
            "commands": ["extract", "add", "search", "list", "status"],
            "examples": [
                "smart-memory status",
                "smart-memory extract '{\"conversation\": \"对话内容\"}'",
                "smart-memory add '{\"content\": \"记忆内容\", \"category\": \"偏好\"}'",
                "smart-memory search '{\"query\": \"关键词\"}'"
            ]
        }, ensure_ascii=False))
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 解析参数
    params = {}
    if len(sys.argv) > 2:
        try:
            params = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            for arg in sys.argv[2:]:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    params[key] = value
    
    # 处理命令
    handlers = {
        "extract": handle_extract,
        "add": handle_add,
        "search": handle_search,
        "list": handle_list,
        "status": handle_status
    }
    
    handler = handlers.get(command)
    if not handler:
        print(json.dumps({
            "success": False,
            "error": f"未知命令: {command}",
            "available_commands": list(handlers.keys())
        }, ensure_ascii=False))
        sys.exit(1)
    
    result = handler(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()