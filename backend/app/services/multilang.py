"""
Multi-Language Support Service
Provides internationalization and localization features
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    ARABIC = "ar"
    HINDI = "hi"
    THAI = "th"
    VIETNAMESE = "vi"
    TURKISH = "tr"
    POLISH = "pl"
    DUTCH = "nl"
    SWEDISH = "sv"
    DANISH = "da"
    NORWEGIAN = "no"

class LocalizationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    context: str = "general"
    preserve_formatting: bool = True

class LocalizationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    processing_time: float
    alternatives: List[str] = []

class LanguageDetectionRequest(BaseModel):
    text: str
    hint_languages: List[str] = []

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    alternative_languages: List[Tuple[str, float]]
    processing_time: float

class MultiLanguageSupport:
    """Advanced multi-language support service"""
    
    def __init__(self):
        # Language configurations
        self.supported_languages = {
            Language.ENGLISH: {
                "name": "English",
                "native_name": "English",
                "code": "en",
                "rtl": False,
                "charset": "utf-8",
                "region": "US"
            },
            Language.SPANISH: {
                "name": "Spanish",
                "native_name": "Español",
                "code": "es",
                "rtl": False,
                "charset": "utf-8",
                "region": "ES"
            },
            Language.FRENCH: {
                "name": "French",
                "native_name": "Français",
                "code": "fr",
                "rtl": False,
                "charset": "utf-8",
                "region": "FR"
            },
            Language.GERMAN: {
                "name": "German",
                "native_name": "Deutsch",
                "code": "de",
                "rtl": False,
                "charset": "utf-8",
                "region": "DE"
            },
            Language.CHINESE_SIMPLIFIED: {
                "name": "Chinese (Simplified)",
                "native_name": "简体中文",
                "code": "zh-CN",
                "rtl": False,
                "charset": "utf-8",
                "region": "CN"
            },
            Language.JAPANESE: {
                "name": "Japanese",
                "native_name": "日本語",
                "code": "ja",
                "rtl": False,
                "charset": "utf-8",
                "region": "JP"
            },
            Language.KOREAN: {
                "name": "Korean",
                "native_name": "한국어",
                "code": "ko",
                "rtl": False,
                "charset": "utf-8",
                "region": "KR"
            },
            Language.ARABIC: {
                "name": "Arabic",
                "native_name": "العربية",
                "code": "ar",
                "rtl": True,
                "charset": "utf-8",
                "region": "SA"
            }
        }
        
        # Common phrases and UI translations
        self.translations = {
            "en": {
                "welcome": "Welcome to IELTS Master Platform",
                "login": "Login",
                "register": "Register",
                "dashboard": "Dashboard",
                "writing": "Writing",
                "reading": "Reading",
                "listening": "Listening",
                "speaking": "Speaking",
                "score": "Score",
                "feedback": "Feedback",
                "practice": "Practice",
                "test": "Test",
                "results": "Results",
                "profile": "Profile",
                "settings": "Settings",
                "logout": "Logout",
                "submit": "Submit",
                "cancel": "Cancel",
                "save": "Save",
                "edit": "Edit",
                "delete": "Delete",
                "confirm": "Confirm",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information"
            },
            "es": {
                "welcome": "Bienvenido a IELTS Master Platform",
                "login": "Iniciar sesión",
                "register": "Registrarse",
                "dashboard": "Panel de control",
                "writing": "Escritura",
                "reading": "Lectura",
                "listening": "Comprensión auditiva",
                "speaking": "Expresión oral",
                "score": "Puntuación",
                "feedback": "Comentarios",
                "practice": "Práctica",
                "test": "Examen",
                "results": "Resultados",
                "profile": "Perfil",
                "settings": "Configuración",
                "logout": "Cerrar sesión",
                "submit": "Enviar",
                "cancel": "Cancelar",
                "save": "Guardar",
                "edit": "Editar",
                "delete": "Eliminar",
                "confirm": "Confirmar",
                "back": "Atrás",
                "next": "Siguiente",
                "previous": "Anterior",
                "loading": "Cargando...",
                "error": "Error",
                "success": "Éxito",
                "warning": "Advertencia",
                "info": "Información"
            },
            "fr": {
                "welcome": "Bienvenue sur IELTS Master Platform",
                "login": "Connexion",
                "register": "S'inscrire",
                "dashboard": "Tableau de bord",
                "writing": "Écriture",
                "reading": "Lecture",
                "listening": "Compréhension orale",
                "speaking": "Expression orale",
                "score": "Score",
                "feedback": "Commentaires",
                "practice": "Pratique",
                "test": "Test",
                "results": "Résultats",
                "profile": "Profil",
                "settings": "Paramètres",
                "logout": "Déconnexion",
                "submit": "Soumettre",
                "cancel": "Annuler",
                "save": "Enregistrer",
                "edit": "Modifier",
                "delete": "Supprimer",
                "confirm": "Confirmer",
                "back": "Retour",
                "next": "Suivant",
                "previous": "Précédent",
                "loading": "Chargement...",
                "error": "Erreur",
                "success": "Succès",
                "warning": "Avertissement",
                "info": "Information"
            },
            "de": {
                "welcome": "Willkommen bei IELTS Master Platform",
                "login": "Anmelden",
                "register": "Registrieren",
                "dashboard": "Dashboard",
                "writing": "Schreiben",
                "reading": "Lesen",
                "listening": "Hören",
                "speaking": "Sprechen",
                "score": "Punktzahl",
                "feedback": "Feedback",
                "practice": "Übung",
                "test": "Test",
                "results": "Ergebnisse",
                "profile": "Profil",
                "settings": "Einstellungen",
                "logout": "Abmelden",
                "submit": "Einreichen",
                "cancel": "Abbrechen",
                "save": "Speichern",
                "edit": "Bearbeiten",
                "delete": "Löschen",
                "confirm": "Bestätigen",
                "back": "Zurück",
                "next": "Weiter",
                "previous": "Vorherige",
                "loading": "Laden...",
                "error": "Fehler",
                "success": "Erfolg",
                "warning": "Warnung",
                "info": "Information"
            },
            "zh-CN": {
                "welcome": "欢迎使用IELTS Master Platform",
                "login": "登录",
                "register": "注册",
                "dashboard": "仪表板",
                "writing": "写作",
                "reading": "阅读",
                "listening": "听力",
                "speaking": "口语",
                "score": "分数",
                "feedback": "反馈",
                "practice": "练习",
                "test": "测试",
                "results": "结果",
                "profile": "个人资料",
                "settings": "设置",
                "logout": "退出",
                "submit": "提交",
                "cancel": "取消",
                "save": "保存",
                "edit": "编辑",
                "delete": "删除",
                "confirm": "确认",
                "back": "返回",
                "next": "下一步",
                "previous": "上一步",
                "loading": "加载中...",
                "error": "错误",
                "success": "成功",
                "warning": "警告",
                "info": "信息"
            },
            "ja": {
                "welcome": "IELTS Master Platformへようこそ",
                "login": "ログイン",
                "register": "登録",
                "dashboard": "ダッシュボード",
                "writing": "ライティング",
                "reading": "リーディング",
                "listening": "リスニング",
                "speaking": "スピーキング",
                "score": "スコア",
                "feedback": "フィードバック",
                "practice": "練習",
                "test": "テスト",
                "results": "結果",
                "profile": "プロフィール",
                "settings": "設定",
                "logout": "ログアウト",
                "submit": "送信",
                "cancel": "キャンセル",
                "save": "保存",
                "edit": "編集",
                "delete": "削除",
                "confirm": "確認",
                "back": "戻る",
                "next": "次へ",
                "previous": "前へ",
                "loading": "読み込み中...",
                "error": "エラー",
                "success": "成功",
                "warning": "警告",
                "info": "情報"
            },
            "ko": {
                "welcome": "IELTS Master Platform에 오신 것을 환영합니다",
                "login": "로그인",
                "register": "회원가입",
                "dashboard": "대시보드",
                "writing": "라이팅",
                "reading": "리딩",
                "listening": "리스닝",
                "speaking": "스피킹",
                "score": "점수",
                "feedback": "피드백",
                "practice": "연습",
                "test": "테스트",
                "results": "결과",
                "profile": "프로필",
                "settings": "설정",
                "logout": "로그아웃",
                "submit": "제출",
                "cancel": "취소",
                "save": "저장",
                "edit": "편집",
                "delete": "삭제",
                "confirm": "확인",
                "back": "뒤로",
                "next": "다음",
                "previous": "이전",
                "loading": "로딩 중...",
                "error": "오류",
                "success": "성공",
                "warning": "경고",
                "info": "정보"
            },
            "ar": {
                "welcome": "مرحباً بك في منصة IELTS Master",
                "login": "تسجيل الدخول",
                "register": "التسجيل",
                "dashboard": "لوحة التحكم",
                "writing": "الكتابة",
                "reading": "القراءة",
                "listening": "الاستماع",
                "speaking": "التحدث",
                "score": "النتيجة",
                "feedback": "التعليقات",
                "practice": "الممارسة",
                "test": "الاختبار",
                "results": "النتائج",
                "profile": "الملف الشخصي",
                "settings": "الإعدادات",
                "logout": "تسجيل الخروج",
                "submit": "إرسال",
                "cancel": "إلغاء",
                "save": "حفظ",
                "edit": "تعديل",
                "delete": "حذف",
                "confirm": "تأكيد",
                "back": "رجوع",
                "next": "التالي",
                "previous": "السابق",
                "loading": "جاري التحميل...",
                "error": "خطأ",
                "success": "نجح",
                "warning": "تحذير",
                "info": "معلومات"
            }
        }
        
        # Language detection patterns
        self.language_patterns = {
            "en": ["the", "and", "is", "in", "to", "of", "a", "that", "it", "with"],
            "es": ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se"],
            "fr": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
            "zh-CN": ["的", "了", "在", "是", "我", "有", "和", "就", "不", "人"],
            "ja": ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し"],
            "ko": ["이", "가", "을", "를", "에", "의", "로", "으로", "와", "과"],
            "ar": ["في", "من", "إلى", "على", "هذا", "هذه", "التي", "الذي", "كان", "كانت"]
        }
    
    async def translate_text(self, request: LocalizationRequest) -> LocalizationResponse:
        """Translate text between languages"""
        
        try:
            # In real implementation, this would use a translation service like Google Translate API
            # For now, return a mock translation
            translated_text = self._mock_translation(request.text, request.source_language, request.target_language)
            
            return LocalizationResponse(
                original_text=request.text,
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence=0.85,
                processing_time=0.5,
                alternatives=[translated_text + " (alt1)", translated_text + " (alt2)"]
            )
            
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            raise e
    
    async def detect_language(self, request: LanguageDetectionRequest) -> LanguageDetectionResponse:
        """Detect the language of given text"""
        
        try:
            detected_language, confidence = self._detect_language_patterns(request.text)
            
            # Get alternative languages
            alternatives = self._get_alternative_languages(request.text, request.hint_languages)
            
            return LanguageDetectionResponse(
                detected_language=detected_language,
                confidence=confidence,
                alternative_languages=alternatives,
                processing_time=0.2
            )
            
        except Exception as e:
            logger.error(f"❌ Language detection failed: {e}")
            raise e
    
    def get_translation(self, key: str, language: str) -> str:
        """Get translation for a specific key and language"""
        
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        
        # Fallback to English
        if key in self.translations.get("en", {}):
            return self.translations["en"][key]
        
        return key  # Return key if no translation found
    
    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Get all supported languages"""
        return self.supported_languages
    
    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific language"""
        
        for lang, info in self.supported_languages.items():
            if info["code"] == language_code:
                return info
        
        return None
    
    def is_rtl_language(self, language_code: str) -> bool:
        """Check if a language is right-to-left"""
        
        language_info = self.get_language_info(language_code)
        return language_info.get("rtl", False) if language_info else False
    
    def format_text_for_language(self, text: str, language_code: str) -> str:
        """Format text according to language-specific rules"""
        
        language_info = self.get_language_info(language_code)
        if not language_info:
            return text
        
        # Apply language-specific formatting
        if language_info["rtl"]:
            # For RTL languages, ensure proper text direction
            return f"<div dir='rtl'>{text}</div>"
        
        return text
    
    def get_date_format(self, language_code: str) -> str:
        """Get date format for a specific language"""
        
        date_formats = {
            "en": "%m/%d/%Y",
            "es": "%d/%m/%Y",
            "fr": "%d/%m/%Y",
            "de": "%d.%m.%Y",
            "zh-CN": "%Y年%m月%d日",
            "ja": "%Y年%m月%d日",
            "ko": "%Y년 %m월 %d일",
            "ar": "%d/%m/%Y"
        }
        
        return date_formats.get(language_code, "%m/%d/%Y")
    
    def get_number_format(self, language_code: str) -> Dict[str, str]:
        """Get number formatting rules for a specific language"""
        
        number_formats = {
            "en": {"decimal": ".", "thousands": ","},
            "es": {"decimal": ",", "thousands": "."},
            "fr": {"decimal": ",", "thousands": " "},
            "de": {"decimal": ",", "thousands": "."},
            "zh-CN": {"decimal": ".", "thousands": ","},
            "ja": {"decimal": ".", "thousands": ","},
            "ko": {"decimal": ".", "thousands": ","},
            "ar": {"decimal": ".", "thousands": ","}
        }
        
        return number_formats.get(language_code, {"decimal": ".", "thousands": ","})
    
    def _mock_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation function"""
        
        # Simple mock translations for demonstration
        mock_translations = {
            ("en", "es"): f"[ES] {text}",
            ("en", "fr"): f"[FR] {text}",
            ("en", "de"): f"[DE] {text}",
            ("en", "zh-CN"): f"[中文] {text}",
            ("en", "ja"): f"[日本語] {text}",
            ("en", "ko"): f"[한국어] {text}",
            ("en", "ar"): f"[العربية] {text}",
            ("es", "en"): f"[EN] {text}",
            ("fr", "en"): f"[EN] {text}",
            ("de", "en"): f"[EN] {text}",
            ("zh-CN", "en"): f"[EN] {text}",
            ("ja", "en"): f"[EN] {text}",
            ("ko", "en"): f"[EN] {text}",
            ("ar", "en"): f"[EN] {text}"
        }
        
        return mock_translations.get((source_lang, target_lang), f"[{target_lang.upper()}] {text}")
    
    def _detect_language_patterns(self, text: str) -> Tuple[str, float]:
        """Detect language using pattern matching"""
        
        text_lower = text.lower()
        word_counts = {}
        
        # Count occurrences of common words for each language
        for lang, patterns in self.language_patterns.items():
            count = sum(1 for pattern in patterns if pattern in text_lower)
            word_counts[lang] = count
        
        if not word_counts or max(word_counts.values()) == 0:
            return "en", 0.5  # Default to English with low confidence
        
        # Find language with highest count
        detected_lang = max(word_counts, key=word_counts.get)
        confidence = min(0.95, word_counts[detected_lang] / len(text.split()) * 10)
        
        return detected_lang, confidence
    
    def _get_alternative_languages(self, text: str, hint_languages: List[str]) -> List[Tuple[str, float]]:
        """Get alternative language suggestions"""
        
        alternatives = []
        
        # Check hint languages first
        for hint_lang in hint_languages:
            if hint_lang in self.language_patterns:
                count = sum(1 for pattern in self.language_patterns[hint_lang] if pattern in text.lower())
                if count > 0:
                    confidence = min(0.9, count / len(text.split()) * 10)
                    alternatives.append((hint_lang, confidence))
        
        # Add other languages with lower confidence
        for lang, patterns in self.language_patterns.items():
            if lang not in hint_languages:
                count = sum(1 for pattern in patterns if pattern in text.lower())
                if count > 0:
                    confidence = min(0.7, count / len(text.split()) * 10)
                    alternatives.append((lang, confidence))
        
        # Sort by confidence and return top 3
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives[:3]
    
    def get_ielts_specific_translations(self, language_code: str) -> Dict[str, str]:
        """Get IELTS-specific translations"""
        
        ielts_translations = {
            "en": {
                "task_achievement": "Task Achievement",
                "coherence_cohesion": "Coherence and Cohesion",
                "lexical_resource": "Lexical Resource",
                "grammatical_range": "Grammatical Range and Accuracy",
                "band_score": "Band Score",
                "overall_score": "Overall Score",
                "writing_task_1": "Writing Task 1",
                "writing_task_2": "Writing Task 2",
                "academic_writing": "Academic Writing",
                "general_writing": "General Writing"
            },
            "es": {
                "task_achievement": "Logro de la Tarea",
                "coherence_cohesion": "Coherencia y Cohesión",
                "lexical_resource": "Recurso Léxico",
                "grammatical_range": "Rango Gramatical y Precisión",
                "band_score": "Puntuación de Banda",
                "overall_score": "Puntuación General",
                "writing_task_1": "Tarea de Escritura 1",
                "writing_task_2": "Tarea de Escritura 2",
                "academic_writing": "Escritura Académica",
                "general_writing": "Escritura General"
            },
            "zh-CN": {
                "task_achievement": "任务完成度",
                "coherence_cohesion": "连贯性和衔接",
                "lexical_resource": "词汇资源",
                "grammatical_range": "语法范围和准确性",
                "band_score": "分数段",
                "overall_score": "总分",
                "writing_task_1": "写作任务1",
                "writing_task_2": "写作任务2",
                "academic_writing": "学术写作",
                "general_writing": "普通写作"
            }
        }
        
        return ielts_translations.get(language_code, ielts_translations["en"])
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate if a language code is supported"""
        
        return any(info["code"] == language_code for info in self.supported_languages.values())
    
    def get_language_family(self, language_code: str) -> str:
        """Get the language family for a given language code"""
        
        language_families = {
            "en": "Germanic",
            "de": "Germanic",
            "nl": "Germanic",
            "sv": "Germanic",
            "da": "Germanic",
            "no": "Germanic",
            "es": "Romance",
            "fr": "Romance",
            "it": "Romance",
            "pt": "Romance",
            "ru": "Slavic",
            "pl": "Slavic",
            "zh-CN": "Sino-Tibetan",
            "zh-TW": "Sino-Tibetan",
            "ja": "Japonic",
            "ko": "Koreanic",
            "ar": "Semitic",
            "hi": "Indo-Aryan",
            "th": "Tai-Kadai",
            "vi": "Austroasiatic",
            "tr": "Turkic"
        }
        
        return language_families.get(language_code, "Unknown")


