import json
from typing import Literal, Optional
from openai import OpenAI
import anthropic
import google.generativeai as genai
from pathlib import Path

class BrickTranslator:
    """
    AI搬砖路人A的智能翻译器
    支持Qwen、Claude、Gemini、OpenAI四种API
    """

    def __init__(self, provider: Optional[Literal["qwen", "claude", "gemini", "openai"]] = None, config_path: str = "config.json"):
        """
        初始化翻译器

        Args:
            provider: API提供商，"qwen"、"claude"、"gemini"或"openai"。如果为None，则使用配置文件中的默认提供商
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # 如果未指定provider，则使用配置文件中的默认提供商
        if provider is None:
            self.provider = self.config.get("default_provider", "qwen")
        else:
            self.provider = provider

        self.client = self._init_client()
        print(f"使用 {self.provider.upper()} API")

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"配置文件 {config_path} 不存在。\n"
                f"请先运行 'python -m brick_translator init' 初始化配置文件。"
            )

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _init_client(self):
        """根据provider初始化客户端"""

        if self.provider == "qwen":
            qwen_config = self.config.get("qwen", {})
            api_key = qwen_config.get("api_key")
            base_url = qwen_config.get("base_url")

            if not api_key or api_key == "your_dashscope_api_key_here":
                raise ValueError("请在 config.json 中配置 qwen.api_key")

            return OpenAI(
                api_key=api_key,
                base_url=base_url
            )

        elif self.provider == "claude":
            claude_config = self.config.get("claude", {})
            api_key = claude_config.get("api_key")

            if not api_key or api_key == "your_anthropic_api_key_here":
                raise ValueError("请在 config.json 中配置 claude.api_key")

            return anthropic.Anthropic(api_key=api_key)

        elif self.provider == "gemini":
            gemini_config = self.config.get("gemini", {})
            api_key = gemini_config.get("api_key")

            if not api_key or api_key == "your_google_api_key_here":
                raise ValueError("请在 config.json 中配置 gemini.api_key")

            genai.configure(api_key=api_key)
            return genai

        elif self.provider == "openai":
            openai_config = self.config.get("openai", {})
            api_key = openai_config.get("api_key")
            base_url = openai_config.get("base_url", "https://api.openai.com/v1")

            if not api_key or api_key == "your_openai_api_key_here":
                raise ValueError("请在 config.json 中配置 openai.api_key")

            return OpenAI(
                api_key=api_key,
                base_url=base_url
            )

        else:
            raise ValueError(f"不支持的provider: {self.provider}")

    def translate(
        self,
        text: str,
        target_lang: Literal["zh", "en"] = "zh",
        temperature: float = 0.3
    ) -> str:
        """
        翻译文本

        Args:
            text: 要翻译的文本
            target_lang: 目标语言，"zh"(中文)或"en"(英文)
            temperature: 温度参数，控制随机性

        Returns:
            翻译后的文本
        """

        # 构建prompt
        lang_name = "中文" if target_lang == "zh" else "英文"
        prompt = f"请将以下文本翻译成{lang_name}，保持原文的格式和语气：\n\n{text}"

        # 根据provider调用不同的API
        if self.provider == "claude":
            # Claude 使用 default 模型
            response = self.client.messages.create(
                model="default",
                max_tokens=2048,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        elif self.provider == "gemini":
            # Gemini 使用默认模型
            model = self.client.GenerativeModel('gemini-pro')
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 2048
                }
            )
            return response.text

        elif self.provider == "qwen":
            # Qwen 使用配置文件中指定的模型
            qwen_config = self.config.get("qwen", {})
            model = qwen_config.get("model", "qwen3-max")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content

        else:  # openai
            # OpenAI 不指定模型，使用API的默认模型
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content

    def translate_with_context(
        self,
        text: str,
        context: str,
        target_lang: Literal["zh", "en"] = "zh"
    ) -> str:
        """
        带上下文的翻译（更准确）

        Args:
            text: 要翻译的文本
            context: 上下文信息
            target_lang: 目标语言

        Returns:
            翻译后的文本
        """

        lang_name = "中文" if target_lang == "zh" else "英文"
        prompt = f"""请将以下文本翻译成{lang_name}。

上下文信息：
{context}

要翻译的文本：
{text}

翻译："""

        if self.provider == "claude":
            response = self.client.messages.create(
                model="default",
                max_tokens=2048,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        elif self.provider == "gemini":
            model = self.client.GenerativeModel('gemini-pro')
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2048
                }
            )
            return response.text

        elif self.provider == "qwen":
            # Qwen 使用配置文件中指定的模型
            qwen_config = self.config.get("qwen", {})
            model = qwen_config.get("model", "qwen3-max")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content

        else:  # openai
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content