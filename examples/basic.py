#!/usr/bin/env python3
"""
AI Brick Translator - 使用示例
"""

# 基础翻译示例
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from brick_translator.translator import BrickTranslator

def basic_translation_example():
    """基础翻译示例"""
    print("=== 基础翻译示例 ===")

    # 初始化翻译器（使用配置文件中的默认提供商）
    translator = BrickTranslator()

    # 英译中
    result = translator.translate("Hello, how are you?", target_lang="zh")
    print(f"英译中: {result}")

    # 中译英
    result = translator.translate("今天天气真好", target_lang="en")
    print(f"中译英: {result}")

def different_providers_example():
    """使用不同模型示例"""
    print("\n=== 使用不同模型示例 ===")

    # 使用 Claude API
    try:
        translator = BrickTranslator(provider="claude")
        result = translator.translate("Machine learning is amazing!", target_lang="zh")
        print(f"Claude 翻译: {result}")
    except Exception as e:
        print(f"Claude 不可用: {e}")

    # 使用 Gemini API
    try:
        translator = BrickTranslator(provider="gemini")
        result = translator.translate("Artificial intelligence is fascinating!", target_lang="zh")
        print(f"Gemini 翻译: {result}")
    except Exception as e:
        print(f"Gemini 不可用: {e}")

def context_translation_example():
    """带上下文的翻译示例"""
    print("\n=== 带上下文的翻译示例 ===")

    translator = BrickTranslator()

    # 提供上下文信息以提高翻译准确性
    result = translator.translate_with_context(
        text="He scored a goal",
        context="This is about a football match",
        target_lang="zh"
    )
    print(f"带上下文翻译: {result}")

def temperature_example():
    """调整Temperature参数示例"""
    print("\n=== Temperature参数示例 ===")

    text_to_translate = "This is absolutely amazing!"

    translator = BrickTranslator()

    result_low = translator.translate(
        text_to_translate,
        target_lang="zh",
        temperature=0.1
    )
    print(f"低Temperature (0.1): {result_low}")

    result_high = translator.translate(
        text_to_translate,
        target_lang="zh",
        temperature=0.9
    )
    print(f"高Temperature (0.9): {result_high}")

    print("\n说明: Temperature值越低，翻译结果越稳定一致；值越高，翻译结果越有创造性但可能不够准确。")

if __name__ == "__main__":
    basic_translation_example()
    different_providers_example()
    context_translation_example()
    temperature_example()