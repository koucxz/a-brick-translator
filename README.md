# AI Brick Translator

一个支持多种 AI 模型的智能翻译工具。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化配置
```bash
python -m brick_translator init
```

### 3. 配置 API Key
编辑 `config.json` 文件，填入你的 API Key。

### 4. 测试连接
```bash
python tests/api_check.py
```

### 5. 基本使用

#### 命令行
```bash
# 英译中
python -m brick_translator translate "Hello, world!" --target zh

# 中译英
python -m brick_translator translate "你好世界" --target en

# 带上下文翻译
python -m brick_translator translate-with-context "bug" --context "software development" --target zh
```

#### Python API
```python
from brick_translator.translator import BrickTranslator

translator = BrickTranslator()
result = translator.translate("Hello, world!", target_lang="zh")
print(result)
```

## TODO

### 国际化 JSON 生成
- [ ] 添加命令行工具，支持从源 JSON 文件生成多语言版本
- [ ] 实现 i18n 文件格式支持（如 .json, .yaml）
- [ ] 支持保留原始 JSON 结构，只翻译值部分
- [ ] 添加翻译缓存机制，避免重复翻译相同内容

## 开源协议

本项目采用 MIT 许可证。

Copyright (c) 2026 AI Brick Translator
