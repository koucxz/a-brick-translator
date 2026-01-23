#!/usr/bin/env python3
"""
AI Brick Translator - 国际化 (i18n) 功能示例
演示如何使用JSON文件作为输入生成中文和西班牙语的国际化文件
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from brick_translator.translator import BrickTranslator
from brick_translator.i18n_generator import I18nGenerator


def demonstrate_i18n_generation():
    """演示i18n生成功能"""
    print("=== 国际化 (i18n) 文件生成示例 ===")
    print("本示例将使用 examples/sample_input.json 作为输入")
    print("生成中文 (zh) 和西班牙语 (es) 版本的国际化文件")
    print()

    input_file = "examples/sample_input.json"

    # 验证输入文件存在
    if not os.path.exists(input_file):
        print(f"[ERROR] 输入文件不存在: {input_file}")
        return

    try:
        # 创建临时配置文件（使用mock API key）
        mock_config = {
            "default_provider": "qwen",
            "qwen": {
                "api_key": "mock_api_key",
                "base_url": "https://mock.api",
                "model": "qwen3-max"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
            config_file = f.name

        try:
            # 初始化翻译器和i18n生成器
            translator = BrickTranslator(provider="qwen", config_path=config_file)
            i18n_generator = I18nGenerator(translator)

            # 使用统一的输出目录
            output_dir = "i18n_output"

            success = i18n_generator.generate_i18n(
                input_file=input_file,
                output_dir=output_dir,
                languages=['zh', 'es'],  # 中文和西班牙语
                output_format='json',
                use_cache=False
            )

            if success:
                print(f"[OK] 国际化文件生成成功！")
                print(f"输出目录: {output_dir}")
                print()

                # 显示生成的文件
                zh_file = Path(output_dir) / "sample_input_zh.json"
                es_file = Path(output_dir) / "sample_input_es.json"

                if zh_file.exists():
                    print("[OK] 中文 (zh) 文件已生成:")
                    with open(zh_file, 'r', encoding='utf-8') as f:
                        zh_content = json.load(f)
                    print(f"   - 标题: {zh_content.get('app', {}).get('title', 'N/A')}")
                    print(f"   - 描述: {zh_content.get('app', {}).get('description', 'N/A')[:50]}...")
                    print(f"   - 欢迎消息: {zh_content.get('messages', {}).get('welcome', 'N/A')}")
                    print()

                if es_file.exists():
                    print("[OK] 西班牙语 (es) 文件已生成:")
                    with open(es_file, 'r', encoding='utf-8') as f:
                        es_content = json.load(f)
                    print(f"   - 标题: {es_content.get('app', {}).get('title', 'N/A')}")
                    print(f"   - 描述: {es_content.get('app', {}).get('description', 'N/A')[:50]}...")
                    print(f"   - Mensaje de bienvenida: {es_content.get('messages', {}).get('welcome', 'N/A')}")
                    print()

                print("注意: 由于使用了模拟API密钥，实际翻译内容会保留原文。")
                print("   配置真实的API密钥后，将获得真正的中文和西班牙语翻译。")

            else:
                print("[ERROR] 国际化文件生成失败")

        finally:
            # 清理临时配置文件
            os.unlink(config_file)

    except Exception as e:
        print(f"[ERROR] i18n示例失败: {e}")


def demonstrate_yaml_output():
    """演示YAML格式输出"""
    print("\n=== YAML 格式输出示例 ===")

    input_file = "examples/sample_input.json"

    if not os.path.exists(input_file):
        print(f"[ERROR] 输入文件不存在: {input_file}")
        return

    try:
        # 使用mock配置
        mock_config = {
            "default_provider": "qwen",
            "qwen": {
                "api_key": "mock_api_key",
                "base_url": "https://mock.api",
                "model": "qwen3-max"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
            config_file = f.name

        try:
            translator = BrickTranslator(provider="qwen", config_path=config_file)
            i18n_generator = I18nGenerator(translator)

            # 使用统一的输出目录
            output_dir = "i18n_output"

            success = i18n_generator.generate_i18n(
                input_file=input_file,
                output_dir=output_dir,
                languages=['zh'],
                output_format='yaml',  # YAML格式
                use_cache=False
            )

            if success:
                print("[OK] YAML格式国际化文件生成成功！")
                yaml_file = Path(output_dir) / "sample_input_zh.yaml"
                if yaml_file.exists():
                    print(f"YAML文件路径: {yaml_file}")
            else:
                print("[ERROR] YAML格式生成失败")

        finally:
            os.unlink(config_file)

    except Exception as e:
        print(f"[ERROR] YAML示例失败: {e}")


def demonstrate_cache_mechanism():
    """演示缓存机制"""
    print("\n=== 翻译缓存机制示例 ===")

    input_file = "examples/sample_input.json"

    if not os.path.exists(input_file):
        print(f"[ERROR] 输入文件不存在: {input_file}")
        return

    try:
        mock_config = {
            "default_provider": "qwen",
            "qwen": {
                "api_key": "mock_api_key",
                "base_url": "https://mock.api",
                "model": "qwen3-max"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
            config_file = f.name

        try:
            translator = BrickTranslator(provider="qwen", config_path=config_file)
            i18n_generator = I18nGenerator(translator)

            # 使用统一的输出目录
            output_dir = "i18n_output"

            # 第一次生成（启用缓存）
            success1 = i18n_generator.generate_i18n(
                input_file=input_file,
                output_dir=output_dir,
                languages=['zh'],
                output_format='json',
                use_cache=True
            )

            # 第二次生成（使用缓存）
            success2 = i18n_generator.generate_i18n(
                input_file=input_file,
                output_dir=output_dir,
                languages=['es'],
                output_format='json',
                use_cache=True
            )

            if success1 and success2:
                print("[OK] 缓存机制演示完成！")
                print("缓存机制可以避免重复翻译相同的内容，提高效率并减少API调用成本。")
            else:
                print("[ERROR] 缓存机制演示失败")

        finally:
            os.unlink(config_file)

    except Exception as e:
        print(f"[ERROR] 缓存示例失败: {e}")


if __name__ == "__main__":
    demonstrate_i18n_generation()
    demonstrate_yaml_output()
    demonstrate_cache_mechanism()
    print("\n[SUCCESS] 国际化 (i18n) 功能示例演示完成！")