#!/usr/bin/env python3
"""
Smart Memory 测试脚本
"""

import sys
import time
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_memory import SmartMemory, RuleExtractor, ConflictDetector


def test_rule_extraction():
    """测试规则提取"""
    print("\n📊 测试1：规则提取")
    print("-" * 40)
    
    extractor = RuleExtractor()
    
    test_cases = [
        ("我素食，对坚果过敏", "偏好"),
        ("项目叫聚合兽", "项目"),
        ("决定用本地模型", "决策"),
        ("明天要部署", "待办"),
        ("服务器用户是 cyber_rex44", "事实"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_cat in test_cases:
        memories = extractor.extract(text)
        
        if memories:
            cat = memories[0].category
            status = "✓" if cat == expected_cat else "✗"
            print(f"  {status} '{text[:20]}...' → {cat} (期望: {expected_cat})")
            if cat == expected_cat:
                passed += 1
        else:
            print(f"  ✗ '{text[:20]}...' → 未提取 (期望: {expected_cat})")
    
    print(f"\n结果: {passed}/{total} 通过")
    return passed == total


def test_conflict_detection():
    """测试冲突检测"""
    print("\n📊 测试2：冲突检测")
    print("-" * 40)
    
    detector = ConflictDetector()
    
    test_cases = [
        ("我喜欢 Python", "我喜欢 Python", "skip", "完全重复"),
        ("我喜欢 Python", "我喜欢 JavaScript", "add", "不同偏好"),
        ("我用云端模型", "我不用云端模型", "update", "矛盾更新"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for existing, new, expected_action, desc in test_cases:
        result = detector.detect(existing, new)
        status = "✓" if result["action"] == expected_action else "✗"
        print(f"  {status} {desc}: {result['action']} (期望: {expected_action})")
        if result["action"] == expected_action:
            passed += 1
    
    print(f"\n结果: {passed}/{total} 通过")
    return passed == total


def test_full_pipeline():
    """测试完整流程"""
    print("\n📊 测试3：完整流程")
    print("-" * 40)
    
    sm = SmartMemory()
    
    conversation = "我素食，对坚果过敏。项目聚合兽是 API 网关。"
    
    start_time = time.time()
    result = sm.process_conversation(conversation)
    elapsed = time.time() - start_time
    
    print(f"  提取: {len(result['extracted'])} 条")
    print(f"  新增: {len(result['added'])} 条")
    print(f"  跳过: {len(result['skipped'])} 条")
    print(f"  耗时: {elapsed*1000:.1f}ms")
    
    success = len(result['extracted']) > 0 and elapsed < 1.0
    
    print(f"\n结果: {'✓ 通过' if success else '✗ 失败'}")
    return success


def test_category_accuracy():
    """测试分类准确率"""
    print("\n📊 测试4：分类准确率")
    print("-" * 40)
    
    extractor = RuleExtractor()
    
    test_cases = {
        "偏好": [
            "我素食",
            "我喜欢 Python",
            "不喜欢 JavaScript",
            "偏好本地部署",
        ],
        "项目": [
            "项目叫聚合兽",
            "目标是商业产品",
            "我们在开发 API 网关",
        ],
        "决策": [
            "决定用本地模型",
            "选择 Python 作为主要语言",
            "确定用 FastAPI",
        ],
        "待办": [
            "明天要部署",
            "下周计划完成",
            "别忘了提交代码",
        ],
        "事实": [
            "服务器用户是 cyber_rex44",
            "我叫翔哥",
            "密码存在 credentials.json",
        ],
    }
    
    correct = 0
    total = 0
    
    for expected_cat, texts in test_cases.items():
        for text in texts:
            memories = extractor.extract(text)
            if memories:
                actual_cat = memories[0].category
                total += 1
                if actual_cat == expected_cat:
                    correct += 1
                    print(f"  ✓ '{text[:25]}' → {actual_cat}")
                else:
                    print(f"  ✗ '{text[:25]}' → {actual_cat} (期望: {expected_cat})")
    
    accuracy = correct / total if total > 0 else 0
    print(f"\n准确率: {accuracy:.1%} ({correct}/{total})")
    
    return accuracy >= 0.7  # 70% 准确率算通过


def test_performance():
    """测试性能"""
    print("\n📊 测试5：性能测试")
    print("-" * 40)
    
    sm = SmartMemory()
    
    # 测试不同长度的文本
    test_texts = [
        "我素食",
        "我素食，对坚果过敏。项目叫聚合兽。",
        "我素食，对坚果过敏。项目叫聚合兽，是 API 网关。目标是商业产品。决定用本地模型。",
        "我素食，对坚果过敏。项目叫聚合兽，是 API 网关。目标是商业产品。决定用本地模型。" * 3,
    ]
    
    times = []
    
    for text in test_texts:
        start = time.time()
        sm.process_conversation(text)
        elapsed = time.time() - start
        times.append(elapsed * 1000)
        print(f"  {len(text):4d} 字符 → {elapsed*1000:6.1f}ms")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\n平均耗时: {avg_time:.1f}ms")
    print(f"最大耗时: {max_time:.1f}ms")
    
    # 规则提取应该在 100ms 内完成
    return max_time < 100


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Smart Memory 测试套件")
    print("=" * 50)
    
    results = {
        "规则提取": test_rule_extraction(),
        "冲突检测": test_conflict_detection(),
        "完整流程": test_full_pipeline(),
        "分类准确率": test_category_accuracy(),
        "性能测试": test_performance(),
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()