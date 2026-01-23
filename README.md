# AI Brick Translator

一个支持多种 AI 模型的智能翻译工具，提供简洁的 Python API 接口和命令行工具。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 初始化配置
```bash
python -m brick_translator init
```

### 2. 配置 API Key
编辑 `config.json` 文件，填入你的 API Key。

### 3. 基本使用

#### 命令行
```bash
# 英译中
python -m brick_translator translate "Hello, world!" --target zh

# 中译英
python -m brick_translator translate "你好世界" --target en

# 带上下文翻译
python -m brick_translator translate-with-context "bug" --context "software development" --target zh

# 生成国际化文件（JSON格式）
python -m brick_translator generate-i18n source.json --languages zh en --output-dir i18n

# 生成国际化文件（YAML格式，启用缓存）
python -m brick_translator generate-i18n source.json --format yaml --cache --languages zh en
```

#### Python API
```python
from brick_translator.translator import BrickTranslator

translator = BrickTranslator()
result = translator.translate("Hello, world!", target_lang="zh")
print(result)
```

## 作为外部库使用

### 基础翻译
```python
from brick_translator.translator import BrickTranslator

# 使用默认提供商（从config.json读取）
translator = BrickTranslator()

# 或指定特定提供商
translator = BrickTranslator(provider="qwen")

# 翻译
result = translator.translate("Hello, world!", target_lang="zh")
```

### 高级功能
```python
# 带上下文的翻译（提高准确性）
result = translator.translate_with_context(
    text="API",
    context="software development",
    target_lang="zh"
)

# 调整temperature参数
result = translator.translate(
    "Hello world",
    target_lang="zh",
    temperature=0.1  # 默认0.3，值越低越稳定
)
```

## 配置文件

初始化后生成的 `config.json` 格式：

```json
{
  "qwen": {
    "api_key": "your_api_key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen3-max"
  },
  "claude": {
    "api_key": "your_api_key"
  },
  "gemini": {
    "api_key": "your_api_key"
  },
  "openai": {
    "api_key": "your_api_key",
    "base_url": "https://api.openai.com/v1"
  },
  "default_provider": "qwen"
}
```

## 注意事项

- **API密钥安全**: `config.json` 已添加到 `.gitignore`，不会被提交
- **错误处理**: 建议在生产环境中添加 try-except 处理API异常
- **Windows兼容**: 已移除emoji字符，避免编码问题

### 支持的提供商
- **Qwen**: 阿里云推出的超大规模语言模型
- **Claude**: Anthropic公司开发的AI助手
- **Gemini**: Google开发的多模态AI模型
- **OpenAI**: OpenAI公司开发的GPT系列语言模型

## Examples 运行示例

项目包含完整的使用示例：

```bash
# 运行基础示例
python examples/basic.py
```

### 实际输出示例：
```
=== 基础翻译示例 ===
使用 QWEN API
英译中: 你好，你怎么样？
中译英: The weather is really nice today.

=== 使用不同模型示例 ===
Claude 不可用: 请在 config.json 中配置 claude.api_key
Gemini 不可用: 请在 config.json 中配置 gemini.api_key

=== 带上下文的翻译示例 ===
使用 QWEN API
带上下文翻译: 他进了一个球

=== Temperature参数示例 ===
使用 QWEN API
低Temperature翻译: 你好，世界！
```

### basic.py 核心用法
```python
from brick_translator.translator import BrickTranslator

# 1. 基础翻译
translator = BrickTranslator()
result = translator.translate("Hello, how are you?", target_lang="zh")

# 2. 多提供商切换（需要配置对应API密钥）
try:
    claude_translator = BrickTranslator(provider="claude")
    result = claude_translator.translate("Machine learning is amazing!", target_lang="zh")
except Exception as e:
    print(f"Claude 不可用: {e}")

# 3. 带上下文翻译
result = translator.translate_with_context(
    "He scored a goal",
    "This is about a football match",
    target_lang="zh"
)

# 4. Temperature参数控制
result = translator.translate("Hello world", target_lang="zh", temperature=0.1)
```

### i18n_example.py - 国际化示例
项目还包含专门的国际化功能示例：

```bash
# 运行i18n示例
python examples/i18n_example.py
```

该示例演示了：
- 生成中文 (zh) 和西班牙语 (es) 版本
- JSON 和 YAML 格式输出
- 翻译缓存机制
- 结构保留功能

## 国际化 (i18n) 文件生成

AI Brick Translator 现在支持从源 JSON 文件生成多语言国际化文件，保留原始结构并只翻译值部分。

### 功能特性
- **保留原始结构**: 保持 JSON 的嵌套结构和键名不变，只翻译字符串值
- **多格式支持**: 支持输出 JSON 和 YAML 格式
- **翻译缓存**: 避免重复翻译相同内容，提高效率并减少 API 调用
- **多语言支持**: 默认支持中文 (zh) 和西班牙语 (es)，可扩展其他语言

### 命令行使用
```bash
# 基本用法 - 生成中文和西班牙语版本（默认）
python -m brick_translator generate-i18n source.json

# 指定输出目录和格式
python -m brick_translator generate-i18n source.json --output-dir locales --format yaml

# 生成特定语言版本
python -m brick_translator generate-i18n source.json --languages zh es

# 启用翻译缓存（推荐用于大型文件）
python -m brick_translator generate-i18n source.json --cache --languages zh es
```

### Python API 使用
```python
from brick_translator.translator import BrickTranslator
from brick_translator.i18n_generator import I18nGenerator

translator = BrickTranslator()
i18n_generator = I18nGenerator(translator)

# 生成多语言文件（默认: 中文和西班牙语）
success = i18n_generator.generate_i18n(
    input_file="source.json",
    output_dir="i18n",
    output_format="json",
    use_cache=True
)

# 生成特定语言版本
success = i18n_generator.generate_i18n(
    input_file="source.json",
    output_dir="i18n",
    languages=["zh", "es"],
    output_format="json",
    use_cache=True
)
```

### 输出示例
**输入文件 (source.json):**
```json
{
  "title": "Hello World",
  "description": "This is a test application",
  "buttons": {
    "save": "Save",
    "cancel": "Cancel"
  }
}
```

**输出文件 (source_zh.json) - 中文:**
```json
{
  "title": "你好世界",
  "description": "这是一个测试应用程序",
  "buttons": {
    "save": "保存",
    "cancel": "取消"
  }
}
```

**输出文件 (source_es.json) - 西班牙语:**
```json
{
  "title": "Hola Mundo",
  "description": "Esta es una aplicación de prueba",
  "buttons": {
    "save": "Guardar",
    "cancel": "Cancelar"
  }
}
```

## 单元测试

项目包含完整的单元测试，覆盖所有核心功能：

### 运行单元测试
```bash
# 运行功能性单元测试（不调用实际API，使用Mock）
python tests/test_translator.py

# 运行API连接测试（需要配置API密钥）
python tests/api_check.py
```

### 测试覆盖范围
- **基础翻译功能**: 英译中、中译英
- **多提供商支持**: Qwen、Claude、Gemini、OpenAI 初始化测试
- **带上下文翻译**: 验证上下文信息对翻译结果的影响
- **Temperature参数**: 测试不同temperature值的功能

### i18n 专用测试
- **i18n功能**: 提取可翻译值、重建结构、JSON/YAML格式输出、翻译缓存机制、中文/西班牙语支持
- **测试文件**: `tests/test_i18n_generator.py`

### 测试特点
- **安全测试**: `test_translator.py` 和 `test_i18n_generator.py` 使用Mock技术，不会产生实际API调用费用
- **独立运行**: 无需配置API密钥即可运行功能性测试
- **完整覆盖**: 参考 `examples/basic.py` 和 `examples/i18n_example.py` 中的所有功能点

## 开源协议

MIT License