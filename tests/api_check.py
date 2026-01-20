import json
from pathlib import Path

def load_config(config_path: str = "config.json") -> dict:
    """加载配置文件"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"配置文件 {config_path} 不存在。\n"
            f"请先运行 'python -m brick_translator init' 初始化配置文件。"
        )

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_qwen():
    """测试通义千问API"""
    print("="*60)
    print("测试通义千问 Qwen")
    print("="*60)

    try:
        from openai import OpenAI

        config = load_config()
        qwen_config = config.get("qwen", {})
        api_key = qwen_config.get("api_key")
        base_url = qwen_config.get("base_url")

        if not api_key or api_key == "your_dashscope_api_key_here":
            print("[ERROR] Qwen API Key未配置，请在 config.json 中配置 qwen.api_key")
            return False

        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        model = qwen_config.get("model", "qwen3-max")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请回复：Qwen API连接成功！"}
            ],
            max_tokens=50
        )

        print("[OK] Qwen API连接成功！")
        print(f"回复：{response.choices[0].message.content}")
        print(f"使用Token：{response.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"[ERROR] Qwen API连接失败：{e}")
        return False

def test_claude():
    """测试Claude API"""
    print("\n" + "="*60)
    print("测试Claude API")
    print("="*60)

    try:
        import anthropic

        config = load_config()
        claude_config = config.get("claude", {})
        api_key = claude_config.get("api_key")

        if not api_key or api_key == "your_anthropic_api_key_here":
            print("[WARN] 未配置Claude API Key，跳过测试")
            return None

        client = anthropic.Anthropic(
            api_key=api_key
        )

        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "你好，请回复：Claude API连接成功！"}
            ]
        )

        print("[OK] Claude API连接成功！")
        print(f"回复：{response.content[0].text}")
        print(f"使用Token：{response.usage.input_tokens + response.usage.output_tokens}")
        return True

    except Exception as e:
        print(f"[ERROR] Claude API连接失败：{e}")
        return False

def test_gemini():
    """测试Gemini API"""
    print("\n" + "="*60)
    print("测试Gemini API")
    print("="*60)

    try:
        import google.generativeai as genai

        config = load_config()
        gemini_config = config.get("gemini", {})
        api_key = gemini_config.get("api_key")

        if not api_key or api_key == "your_google_api_key_here":
            print("[WARN] 未配置Gemini API Key，跳过测试")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(
            "你好，请回复：Gemini API连接成功！",
            generation_config={
                "max_output_tokens": 50
            }
        )

        print("[OK] Gemini API连接成功！")
        print(f"回复：{response.text}")
        return True

    except Exception as e:
        print(f"[ERROR] Gemini API连接失败：{e}")
        return False

def test_openai():
    """测试OpenAI API"""
    print("\n" + "="*60)
    print("测试OpenAI API")
    print("="*60)

    try:
        from openai import OpenAI

        config = load_config()
        openai_config = config.get("openai", {})
        api_key = openai_config.get("api_key")
        base_url = openai_config.get("base_url", "https://api.openai.com/v1")

        if not api_key or api_key == "your_openai_api_key_here":
            print("[WARN] 未配置OpenAI API Key，跳过测试")
            return None

        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "你好，请回复：OpenAI API连接成功！"}
            ],
            max_tokens=50
        )

        print("[OK] OpenAI API连接成功！")
        print(f"回复：{response.choices[0].message.content}")
        print(f"使用Token：{response.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"[ERROR] OpenAI API连接失败：{e}")
        return False

def main():
    print("\nAI Brick Translator - API连接测试\n")

    # 测试所有API
    qwen_ok = test_qwen()
    claude_ok = test_claude()
    gemini_ok = test_gemini()
    openai_ok = test_openai()

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    if qwen_ok:
        print("[OK] Qwen可用 - 推荐使用（免费额度大）")

    if claude_ok:
        print("[OK] Claude可用 - 质量最高")
    elif claude_ok is None:
        print("[WARN] Claude未配置 - 可以后续添加")

    if gemini_ok:
        print("[OK] Gemini可用 - Google出品")
    elif gemini_ok is None:
        print("[WARN] Gemini未配置 - 可以后续添加")

    if openai_ok:
        print("[OK] OpenAI可用 - 行业标准")
    elif openai_ok is None:
        print("[WARN] OpenAI未配置 - 可以后续添加")

    available_apis = sum([
        bool(qwen_ok),
        bool(claude_ok),
        bool(gemini_ok),
        bool(openai_ok)
    ])

    if available_apis > 0:
        print(f"\n[SUCCESS] 恭喜！{available_apis}个API可用，可以开始使用了！")
    else:
        print("\n[ERROR] 所有API都不可用，请检查配置")

if __name__ == "__main__":
    main()