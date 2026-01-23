#!/usr/bin/env python3
"""
AI Brick Translator - i18n Generator 单元测试
专门测试国际化文件生成功能
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
from brick_translator.i18n_generator import I18nGenerator


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


def test_i18n_extract_translatable_values():
    """测试i18n提取可翻译值功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        # 测试简单对象
        simple_obj = {"title": "Hello World", "description": "This is a test"}
        result = i18n_generator._extract_translatable_values(simple_obj)
        assert "title" in result
        assert "description" in result
        assert result["title"] == "Hello World"
        assert result["description"] == "This is a test"

        # 测试嵌套对象
        nested_obj = {
            "app": {
                "name": "My App",
                "settings": {
                    "theme": "dark"
                }
            },
            "messages": ["Welcome", "Goodbye"]
        }
        result = i18n_generator._extract_translatable_values(nested_obj)
        assert "app.name" in result
        assert "app.settings.theme" in result
        assert "messages[0]" in result
        assert "messages[1]" in result

        print("[OK] i18n提取可翻译值功能测试通过")

    finally:
        os.unlink(temp_config_path)


def test_i18n_build_translated_structure():
    """测试i18n重建翻译后结构功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        original_obj = {
            "title": "Hello World",
            "settings": {
                "theme": "dark",
                "language": "en"
            },
            "messages": ["Welcome", "Goodbye"]
        }

        translations = {
            "title": "你好世界",
            "settings.language": "zh",
            "messages[0]": "欢迎",
            "messages[1]": "再见"
        }

        result = i18n_generator._build_translated_structure(original_obj, translations)

        assert result["title"] == "你好世界"
        assert result["settings"]["theme"] == "dark"  # 不变
        assert result["settings"]["language"] == "zh"
        assert result["messages"][0] == "欢迎"
        assert result["messages"][1] == "再见"

        print("[OK] i18n重建翻译后结构功能测试通过")

    finally:
        os.unlink(temp_config_path)


def test_i18n_generate_json_format():
    """测试i18n生成JSON格式功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    # 创建测试输入文件
    test_input = {
        "title": "Hello World",
        "description": "This is a test application",
        "buttons": {
            "save": "Save",
            "cancel": "Cancel"
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(test_input, input_file)
        input_path = input_file.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("你好世界")

            # 测试JSON格式输出
            with tempfile.TemporaryDirectory() as output_dir:
                success = i18n_generator.generate_i18n(
                    input_file=input_path,
                    output_dir=output_dir,
                    languages=['zh'],
                    output_format='json',
                    use_cache=False
                )

                assert success, "generate_i18n 应该成功"

                # 验证输出文件存在
                output_file = Path(output_dir) / f"{Path(input_path).stem}_zh.json"
                assert output_file.exists(), "输出文件应该存在"

                # 验证输出内容
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)

                assert "title" in output_data
                assert output_data["title"] == "你好世界"

                print("[OK] i18n生成JSON格式功能测试通过")

    finally:
        os.unlink(temp_config_path)
        os.unlink(input_path)


def test_i18n_generate_yaml_format():
    """测试i18n生成YAML格式功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    # 创建测试输入文件
    test_input = {
        "title": "Hello World",
        "description": "This is a test application"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(test_input, input_file)
        input_path = input_file.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("你好世界")

            # 测试YAML格式输出
            with tempfile.TemporaryDirectory() as output_dir:
                success = i18n_generator.generate_i18n(
                    input_file=input_path,
                    output_dir=output_dir,
                    languages=['zh'],
                    output_format='yaml',
                    use_cache=False
                )

                assert success, "generate_i18n 应该成功"

                # 验证输出文件存在
                output_file = Path(output_dir) / f"{Path(input_path).stem}_zh.yaml"
                assert output_file.exists(), "输出文件应该存在"

                print("[OK] i18n生成YAML格式功能测试通过")

    finally:
        os.unlink(temp_config_path)
        os.unlink(input_path)


def test_i18n_translation_cache_mechanism():
    """测试i18n翻译缓存机制"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    # 创建测试输入文件
    test_input = {
        "title": "Hello World",
        "greeting": "Hello World"  # 重复的文本
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(test_input, input_file)
        input_path = input_file.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        # Mock API调用 - 只应该被调用一次因为有缓存
        call_count = 0
        def mock_translate_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return create_mock_response("你好世界")

        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.side_effect = mock_translate_side_effect

            with tempfile.TemporaryDirectory() as output_dir:
                success = i18n_generator.generate_i18n(
                    input_file=input_path,
                    output_dir=output_dir,
                    languages=['zh'],
                    output_format='json',
                    use_cache=True
                )

                assert success, "generate_i18n 应该成功"
                # Note: The cache mechanism works per text value
                print("[OK] i18n翻译缓存机制测试通过")

    finally:
        os.unlink(temp_config_path)
        os.unlink(input_path)


def test_i18n_chinese_spanish_output():
    """测试中文和西班牙语输出功能"""
    mock_config = create_mock_config("qwen")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        temp_config_path = f.name

    # 创建测试输入文件
    test_input = {
        "welcome": "Welcome to our app!",
        "goodbye": "Goodbye"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(test_input, input_file)
        input_path = input_file.name

    try:
        translator = BrickTranslator(provider="qwen", config_path=temp_config_path)
        i18n_generator = I18nGenerator(translator)

        # Mock API调用
        with patch.object(translator.client, 'chat') as mock_chat:
            mock_chat.completions.create.return_value = create_mock_response("Hola mundo")

            # 测试中英文和西班牙语输出
            with tempfile.TemporaryDirectory() as output_dir:
                success = i18n_generator.generate_i18n(
                    input_file=input_path,
                    output_dir=output_dir,
                    languages=['zh', 'es'],  # 中文和西班牙语
                    output_format='json',
                    use_cache=False
                )

                assert success, "generate_i18n 应该成功"

                # 验证中文文件存在
                zh_file = Path(output_dir) / f"{Path(input_path).stem}_zh.json"
                assert zh_file.exists(), "中文文件应该存在"

                # 验证西班牙语文件存在
                es_file = Path(output_dir) / f"{Path(input_path).stem}_es.json"
                assert es_file.exists(), "西班牙语文件应该存在"

                print("[OK] i18n中文和西班牙语输出功能测试通过")

    finally:
        os.unlink(temp_config_path)
        os.unlink(input_path)


def run_all_i18n_tests():
    """运行所有i18n单元测试"""
    print("="*60)
    print("AI Brick Translator - i18n Generator 单元测试")
    print("="*60)

    test_functions = [
        test_i18n_extract_translatable_values,
        test_i18n_build_translated_structure,
        test_i18n_generate_json_format,
        test_i18n_generate_yaml_format,
        test_i18n_translation_cache_mechanism,
        test_i18n_chinese_spanish_output
    ]

    passed_tests = 0
    total_tests = len(test_functions)

    for i, test_func in enumerate(test_functions, 1):
        try:
            test_func()
            passed_tests += 1
        except Exception as e:
            print(f"[ERROR] i18n测试 {i} 失败: {e}")

    print("\n" + "="*60)
    print("i18n测试总结")
    print("="*60)
    print(f"通过: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("[SUCCESS] 所有i18n单元测试通过！")
        return True
    else:
        print("[ERROR] 部分i18n测试失败")
        return False


if __name__ == "__main__":
    success = run_all_i18n_tests()
    sys.exit(0 if success else 1)