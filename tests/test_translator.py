#!/usr/bin/env python3
"""
AI Brick Translator - 单元测试文件
参考examples/basic.py中的功能点进行测试
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from brick_translator.translator import BrickTranslator


def create_mock_config(provider="qwen"):
    """创建模拟配置"""
    mock_config = {
        "default_provider": provider,
        "qwen": {
            "api_key": "test_key",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen3-max"
        }
    }

    if provider == "claude":
        mock_config["claude"] = {"api_key": "test_key"}
    elif provider == "gemini":
        mock_config["gemini"] = {"api_key": "test_key"}
    elif provider == "openai":
        mock_config["openai"] = {
            "api_key": "test_key",
            "base_url": "https://api.openai.com/v1"
        }

    return mock_config


def create_mock_response(content):
    """创建模拟API响应"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = content
    return mock_response


def test_basic_translation_english_to_chinese():
    """测试基础翻译功能 - 英译中"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("你好，你怎么样？")

            result = translator.translate("Hello, how are you?", target_lang="zh")

            # 验证结果
            assert result is not None
            assert "你好" in result
            print("[OK] 基础翻译功能 - 英译中 测试通过")

    finally:
        os.unlink(temp_config_path)


def test_basic_translation_chinese_to_english():
    """测试基础翻译功能 - 中译英"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("The weather is really nice today")

            result = translator.translate("今天天气真好", target_lang="en")

            # 验证结果
            assert result is not None
            assert "weather" in result.lower()
            print("[OK] 基础翻译功能 - 中译英 测试通过")

    finally:
        os.unlink(temp_config_path)


def test_different_providers_initialization():
    """测试不同API提供商初始化"""
    providers = ["qwen", "claude", "gemini", "openai"]
    success_count = 0

    for provider in providers:
        mock_config = create_mock_config(provider)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_config, f)
            temp_config_path = f.name

        try:
            translator = BrickTranslator(provider=provider, config_path=temp_config_path)
            assert translator.provider == provider
            success_count += 1
            print(f"[OK] {provider.upper()} 初始化测试通过")
        except Exception as e:
            print(f"[WARN] {provider.upper()} 初始化失败: {e}")
        finally:
            os.unlink(temp_config_path)
    assert success_count > 0, "至少应该有一个提供商初始化成功"
    print(f"[INFO] API提供商初始化测试: {success_count}/{len(providers)} 通过")


def test_context_translation_functionality():
    """测试带上下文的翻译功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("他进了一个球")

            result = translator.translate_with_context(
                text="He scored a goal",
                context="This is about a football match",
                target_lang="zh"
            )

            # 验证结果
            assert result is not None
            assert "球" in result
            print("[OK] 带上下文翻译功能测试通过")

    finally:
        os.unlink(temp_config_path)


def test_temperature_parameter_functionality():
    """测试Temperature参数功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)

        # 测试不同的temperature值
        temperatures = [0.1, 0.9]
        for temp in temperatures:
            with patch.object(translator.client, 'chat') as mock_chat:
                mock_chat.completions.create.return_value = create_mock_response(f"温度{temp}的翻译结果")

                result = translator.translate(
                    "Test text for temperature",
                    target_lang="zh",
                    temperature=temp
                )

                # 验证结果
                assert result is not None
                print(f"[OK] Temperature {temp} 参数功能测试通过")

    finally:
        os.unlink(temp_config_path)


def run_all_tests():
    """运行所有单元测试"""
    print("="*60)
    print("AI Brick Translator - 单元测试")
    print("="*60)

    test_functions = [
        test_basic_translation_english_to_chinese,
        test_basic_translation_chinese_to_english,
        test_different_providers_initialization,
        test_context_translation_functionality,
        test_temperature_parameter_functionality
    ]

    passed_tests = 0
    total_tests = len(test_functions)

    for i, test_func in enumerate(test_functions, 1):
        try:
            test_func()
            passed_tests += 1
        except Exception as e:
            print(f"[ERROR] 测试 {i} 失败: {e}")

    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"通过: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("[SUCCESS] 所有单元测试通过！")
        return True
    else:
        print("[ERROR] 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)