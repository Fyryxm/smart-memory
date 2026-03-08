#!/usr/bin/env python3
"""
Smart Memory 测试脚本
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_memory.extractor import RuleExtractor, ExtractedMemory


def test_basic_extraction():
    """测试基础提取"""
    print("\n📊 测试1：基础提取")
    print("-" * 40)
    
    extractor = RuleExtractor()
    
    test_cases = [
        ("我素食，对坚果过敏", "偏好", 2),
        ("项目叫聚合兽", "项目", 1),
        ("决定用本地模型", "决策", 1),
        ("明天要部署", "待办", 1),
        ("我是翔哥", "事实", 1),
    ]
    
    passed = 0
    for text, expected_cat, min_count in test_cases:
        memories = extractor.extract(text)
        count = len([m for m in memories if m.category == expected_cat])
        status = "✓" if count >= min_count else "✗"
        print(f"  {status} '{text[:20]}...' → {count} 个 {expected_cat}")
        if count >= min_count:
            passed += 1
    
    print(f"\n结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


def test_category_accuracy():
    """测试分类准确率"""
    print("\n📊 测试2：分类准确率")
    print("-" * 40)
    
    extractor = RuleExtractor()
    
    test_cases = {
        "偏好": ["我素食", "我喜欢 Python", "对坚果过敏"],
        "项目": ["项目叫聚合兽", "目标是商业产品"],
        "决策": ["决定用本地模型", "选择 Python"],
        "事实": ["我是翔哥", "我叫 cyber_rex44"],
    }
    
    correct = 0
    total = 0
    
    for expected_cat, texts in test_cases.items():
        for text in texts:
            memories = extractor.extract(text)
            total += 1
            if memories and memories[0].category == expected_cat:
                correct += 1
                print(f"  ✓ '{text}' → {memories[0].category}")
            else:
                actual = memories[0].category if memories else "无"
                print(f"  ✗ '{text}' → {actual} (期望: {expected_cat})")
    
    accuracy = correct / total if total > 0 else 0
    print(f"\n准确率: {accuracy:.1%} ({correct}/{total})")
    return accuracy >= 0.7


def test_performance():
    """测试性能"""
    print("\n📊 测试3：性能")
    print("-" * 40)
    
    import time
    
    extractor = RuleExtractor()
    
    test_texts = [
        "我素食",
        "我素食，对坚果过敏。项目叫聚合兽。",
        "我素食，对坚果过敏。项目叫聚合兽，是 API 网关。目标是商业产品。决定用本地模型。",
        "我素食" * 10,
    ]
    
    times = []
    for text in test_texts:
        start = time.time()
        extractor.extract(text)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"  {len(text):4d} 字符 → {elapsed:6.2f}ms")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\n平均: {avg_time:.2f}ms, 最大: {max_time:.2f}ms")
    return max_time < 100


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Smart Memory 测试套件")
    print("=" * 50)
    
    results = {
        "基础提取": test_basic_extraction(),
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