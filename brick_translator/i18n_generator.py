import json
import os
import yaml
from pathlib import Path
from typing import Literal, Dict, Any, Optional
from .translator import BrickTranslator


class I18nGenerator:
    """
    国际化 (i18n) 文件生成器
    从源 JSON 文件生成多语言版本，保留原始结构并只翻译值部分
    """

    def __init__(self, translator: BrickTranslator):
        """
        初始化 i18n 生成器

        Args:
            translator: BrickTranslator 实例，用于执行实际翻译
        """
        self.translator = translator

    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json_file(self, data: Dict[str, Any], file_path: str):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_yaml_file(self, data: Dict[str, Any], file_path: str):
        """保存YAML文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=2)

    def _extract_translatable_values(self, obj: Any, path: str = "") -> Dict[str, str]:
        """递归提取所有字符串值进行翻译"""
        translatable = {}

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                translatable.update(self._extract_translatable_values(value, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                translatable.update(self._extract_translatable_values(item, new_path))
        elif isinstance(obj, str):
            # 翻译所有非空字符串
            if obj.strip():
                translatable[path] = obj

        return translatable

    def _build_translated_structure(self, original_obj: Any, translations: Dict[str, str], path: str = "") -> Any:
        """根据翻译结果重建原始结构"""
        if isinstance(original_obj, dict):
            result = {}
            for key, value in original_obj.items():
                new_path = f"{path}.{key}" if path else key
                result[key] = self._build_translated_structure(value, translations, new_path)
            return result
        elif isinstance(original_obj, list):
            result = []
            for i, item in enumerate(original_obj):
                new_path = f"{path}[{i}]"
                result.append(self._build_translated_structure(item, translations, new_path))
            return result
        elif isinstance(original_obj, str):
            if path in translations:
                return translations[path]
            else:
                return original_obj
        else:
            return original_obj

    def _get_cache_file_path(self, input_file: str, language: str) -> str:
        """获取缓存文件路径"""
        input_path = Path(input_file)
        cache_dir = input_path.parent / ".i18n_cache"
        cache_dir.mkdir(exist_ok=True)
        return str(cache_dir / f"{input_path.stem}_{language}.json")

    def _load_translation_cache(self, cache_file: str) -> Dict[str, str]:
        """加载翻译缓存"""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_translation_cache(self, cache_file: str, cache_data: Dict[str, str]):
        """保存翻译缓存"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def generate_i18n(
        self,
        input_file: str,
        output_dir: str = "i18n",
        languages: list = None,
        output_format: Literal["json", "yaml"] = "json",
        use_cache: bool = False
    ) -> bool:
        """
        生成国际化文件

        Args:
            input_file: 源JSON文件路径
            output_dir: 输出目录
            languages: 目标语言列表 (默认: ['zh', 'es'])
            output_format: 输出文件格式 ('json' 或 'yaml')
            use_cache: 是否启用翻译缓存

        Returns:
            bool: 是否成功
        """
        if languages is None:
            languages = ['zh', 'es']  # Default to Chinese and Spanish

        try:
            # 创建输出目录
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # 加载源文件
            source_data = self._load_json_file(input_file)

            # 提取所有可翻译的值
            translatable_values = self._extract_translatable_values(source_data)

            if not translatable_values:
                print("[WARN] 源文件中没有找到可翻译的内容")
                return True

            # 为每种语言生成翻译
            for lang in languages:
                lang_name = {"zh": "中文", "en": "英文", "es": "西班牙语"}.get(lang, lang)
                print(f"[INFO] 正在生成 {lang_name} ({lang}) 版本...")

                # 获取缓存文件路径
                cache_file = self._get_cache_file_path(input_file, lang) if use_cache else None
                translation_cache = self._load_translation_cache(cache_file) if use_cache else {}

                # 执行翻译
                translations = {}
                for path, text in translatable_values.items():
                    if use_cache and text in translation_cache:
                        # 使用缓存
                        translations[path] = translation_cache[text]
                    else:
                        # 执行新翻译
                        try:
                            translated_text = self.translator.translate(text, target_lang=lang)
                            translations[path] = translated_text
                            if use_cache:
                                translation_cache[text] = translated_text
                        except Exception as e:
                            print(f"[WARN] 翻译 '{text}' 失败: {e}")
                            translations[path] = text  # 保留原文

                # 保存缓存
                if use_cache:
                    self._save_translation_cache(cache_file, translation_cache)

                # 重建翻译后的结构
                translated_data = self._build_translated_structure(source_data, translations)

                # 保存输出文件
                output_file = Path(output_dir) / f"{Path(input_file).stem}_{lang}.{output_format}"
                if output_format == "json":
                    self._save_json_file(translated_data, str(output_file))
                else:  # yaml
                    self._save_yaml_file(translated_data, str(output_file))

                print(f"[OK] {lang_name} 版本已保存到 {output_file}")

            return True

        except Exception as e:
            print(f"[ERROR] 生成国际化文件失败: {e}")
            return False