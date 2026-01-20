#!/usr/bin/env python3
"""
AI搬砖路人A - 智能翻译器
支持Qwen、Claude、Gemini、OpenAI四种API
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="AI搬砖路人A - 智能翻译器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 初始化配置文件（默认使用qwen）
  python -m brick_translator init

  # 初始化配置文件并设置默认提供商为claude
  python -m brick_translator init --default-provider claude

  # 初始化配置文件并强制覆盖
  python -m brick_translator init --force

  # 验证配置文件
  python -m brick_translator validate

  # 列出可用的提供商
  python -m brick_translator list

  # 翻译文本（使用配置文件中的默认提供商）
  python -m brick_translator translate "Hello, world!" --target zh

  # 使用特定提供商翻译
  python -m brick_translator translate "你好世界" --provider gemini --target en

  # 带上下文的翻译
  python -m brick_translator translate-with-context "bug" --context "software development" --target zh
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化配置文件')
    init_parser.add_argument('--config', default='config.json', help='配置文件路径')
    init_parser.add_argument('--force', action='store_true', help='强制覆盖已存在的配置文件')
    init_parser.add_argument('--default-provider', choices=['qwen', 'claude', 'gemini', 'openai'],
                           default='qwen', help='设置默认API提供商')

    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证配置文件')
    validate_parser.add_argument('--config', default='config.json', help='配置文件路径')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出可用的提供商')
    list_parser.add_argument('--config', default='config.json', help='配置文件路径')

    # translate 命令
    translate_parser = subparsers.add_parser('translate', help='翻译文本')
    translate_parser.add_argument('text', help='要翻译的文本')
    translate_parser.add_argument('--provider', choices=['qwen', 'claude', 'gemini', 'openai'],
                                help='API提供商（如果不指定，则使用配置文件中的默认提供商）')
    translate_parser.add_argument('--target', choices=['zh', 'en'], default='zh',
                                help='目标语言 (zh=中文, en=英文)')
    translate_parser.add_argument('--config', default='config.json', help='配置文件路径')
    translate_parser.add_argument('--temperature', type=float, default=0.3,
                                help='温度参数 (0.0-1.0)')

    # translate-with-context 命令
    translate_context_parser = subparsers.add_parser('translate-with-context', help='带上下文的翻译')
    translate_context_parser.add_argument('text', help='要翻译的文本')
    translate_context_parser.add_argument('--context', required=True, help='上下文信息')
    translate_context_parser.add_argument('--provider', choices=['qwen', 'claude', 'gemini', 'openai'],
                                        help='API提供商（如果不指定，则使用配置文件中的默认提供商）')
    translate_context_parser.add_argument('--target', choices=['zh', 'en'], default='zh',
                                        help='目标语言 (zh=中文, en=英文)')
    translate_context_parser.add_argument('--config', default='config.json', help='配置文件路径')

    # test 命令
    test_parser = subparsers.add_parser('test', help='测试所有API连接')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'init':
            from .config_manager import init_config
            success = init_config(args.config, args.force, args.default_provider)
            sys.exit(0 if success else 1)

        elif args.command == 'validate':
            from .config_manager import validate_config
            config = validate_config(args.config)
            print("[OK] 配置文件验证通过")

        elif args.command == 'list':
            from .config_manager import get_available_providers
            providers = get_available_providers(args.config)
            if providers:
                print(f"[OK] 可用的提供商: {', '.join(providers)}")
            else:
                print("[WARN] 没有配置任何有效的提供商")
                print("   请先运行 'python -m brick_translator init' 初始化配置文件")

        elif args.command == 'translate':
            from .translator import BrickTranslator
            # 如果未指定provider，则使用None，让BrickTranslator使用配置文件中的默认提供商
            provider = args.provider if args.provider is not None else None
            translator = BrickTranslator(provider=provider, config_path=args.config)
            result = translator.translate(args.text, target_lang=args.target, temperature=args.temperature)
            print(result)

        elif args.command == 'translate-with-context':
            from .translator import BrickTranslator
            # 如果未指定provider，则使用None，让BrickTranslator使用配置文件中的默认提供商
            provider = args.provider if args.provider is not None else None
            translator = BrickTranslator(provider=provider, config_path=args.config)
            result = translator.translate_with_context(args.text, args.context, target_lang=args.target)
            print(result)

        elif args.command == 'test':
            # 测试命令需要从tests目录运行
            print("请运行 'python -m pytest tests/' 或 'python tests/api_check.py' 来测试API连接")

    except Exception as e:
        print(f"[ERROR] 错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()