import json
from pathlib import Path
from typing import Optional

def generate_default_config(default_provider: str = "qwen") -> dict:
    """
    生成默认配置字典

    Args:
        default_provider: 默认的API提供商，默认为"qwen"
    """
    config = {
        "qwen": {
            "api_key": "your_dashscope_api_key_here",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen3-max"
        },
        "claude": {
            "api_key": "your_anthropic_api_key_here"
        },
        "gemini": {
            "api_key": "your_google_api_key_here"
        },
        "openai": {
            "api_key": "your_openai_api_key_here",
            "base_url": "https://api.openai.com/v1"
        }
    }

    # 设置默认提供商
    config["default_provider"] = default_provider

    return config

def init_config(config_path: str = "config.json", force: bool = False, default_provider: str = "qwen") -> bool:
    """
    初始化配置文件

    Args:
        config_path: 配置文件路径，默认为config.json
        force: 是否强制覆盖已存在的配置文件
        default_provider: 默认的API提供商，默认为"qwen"

    Returns:
        bool: 是否成功初始化
    """
    config_file = Path(config_path)

    # 检查目标配置文件是否已存在
    if config_file.exists() and not force:
        print(f"[WARN] 配置文件 {config_path} 已存在，跳过初始化")
        print("   如需重新初始化，请使用 --force 参数")
        return False

    try:
        # 直接生成配置内容并写入文件
        default_config = generate_default_config(default_provider)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        print(f"[OK] 配置文件已生成: {config_path}")
        print(f"[INFO] 默认API提供商设置为: {default_provider}")
        print("\n[INFO] 请编辑配置文件，填入你的API密钥:")
        print("   - Qwen: 在阿里云DashScope控制台获取API Key")
        print("   - Claude: 在Anthropic官网获取API Key")
        print("   - Gemini: 在Google AI Studio获取API Key")
        print("   - OpenAI: 在OpenAI平台获取API Key")
        return True

    except Exception as e:
        print(f"[ERROR] 配置文件初始化失败: {e}")
        return False

def validate_config(config_path: str = "config.json") -> dict:
    """
    验证配置文件并返回配置内容

    Args:
        config_path: 配置文件路径

    Returns:
        dict: 配置内容
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(
            f"配置文件 {config_path} 不存在。\n"
            f"请先运行 'python -m brick_translator init' 初始化配置文件。"
        )

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误: {e}")
    except Exception as e:
        raise ValueError(f"读取配置文件失败: {e}")

def get_available_providers(config_path: str = "config.json") -> list:
    """
    获取可用的提供商列表

    Args:
        config_path: 配置文件路径

    Returns:
        list: 可用的提供商列表
    """
    try:
        config = validate_config(config_path)
        providers = []
        for provider in ["qwen", "claude", "gemini", "openai"]:
            if provider in config and config[provider].get("api_key") and config[provider]["api_key"] != f"your_{provider}_api_key_here":
                providers.append(provider)
        return providers
    except (FileNotFoundError, ValueError):
        return []

def get_default_provider(config_path: str = "config.json") -> str:
    """
    获取默认的API提供商

    Args:
        config_path: 配置文件路径

    Returns:
        str: 默认的API提供商
    """
    try:
        config = validate_config(config_path)
        return config.get("default_provider", "qwen")
    except (FileNotFoundError, ValueError):
        return "qwen"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="配置文件管理工具")
    parser.add_argument("command", choices=["init", "validate", "list"],
                       help="命令: init(初始化), validate(验证), list(列出可用提供商)")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的配置文件")
    parser.add_argument("--default-provider", choices=["qwen", "claude", "gemini", "openai"],
                       default="qwen", help="设置默认API提供商")

    args = parser.parse_args()

    if args.command == "init":
        init_config(args.config, args.force, args.default_provider)
    elif args.command == "validate":
        try:
            config = validate_config(args.config)
            print("[OK] 配置文件验证通过")
            print(f"配置内容: {json.dumps(config, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"[ERROR] 配置文件验证失败: {e}")
    elif args.command == "list":
        providers = get_available_providers(args.config)
        if providers:
            print(f"[OK] 可用的提供商: {', '.join(providers)}")
        else:
            print("[WARN] 没有配置任何有效的提供商")
            print("   请编辑配置文件并填入API密钥")