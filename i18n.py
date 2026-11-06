#!/usr/bin/env python3

# Written in 2026 by Iwakawa-2173
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
# See <http://creativecommons.org> for CC0 full legal text.

"""
Localization for GHHT clock/map.
Supported: ru, en, zh, ja, ko
"""

from typing import Dict, Callable, Optional

LANGUAGES: Dict[str, str] = {
    "en": "English",
    "ru": "Русский",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
}

DEFAULT_LANG = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title":        "Half-Hour Time Zones — Clock & Map",
        "header_title":     "GLOBAL HALF-HOUR TIME",
        "coords_title":     "ENTER YOUR COORDINATES",
        "lat":              "LAT",
        "lon":              "LON",
        "apply":            "APPLY",
        "reset":            "RESET",
        "reset_tip":        "Reset map zoom (coordinates unchanged)",
        "search_title":     "SEARCH CITY",
        "search_ph":        "Type a name...",
        "search_hint":      "Arrows — select, Enter — go",
        "sync_title":       "SYNCHRONIZATION",
        "language":         "LANGUAGE",
        "mode_auto":        "Autonomous",
        "mode_ntp":         "Network (NTP)",
        "ntp_off":          "NTP: disabled",
        "ntp_syncing":      "NTP: syncing…",
        "ntp_unreachable":  "NTP: unreachable → autonomous",
        "ntp_ok":           "NTP: OK (Δ {ms:+.0f} ms)",
        "selected_title":   "SELECTED POINT",
        "click_map":        "Click on the map",
        "quick_select":     "QUICK SELECT:",
        "map_hint":         "Click — time | Wheel — zoom | Drag LMB — pan",
        "zenith":           "Zenith",
        "tooltip_lat":      "Latitude",
        "tooltip_lon":      "Longitude",
        "tooltip_zone":     "Zone",
        "tooltip_time":     "GHHT time",
        "selected_lat":     "Latitude:",
        "selected_lon":     "Longitude:",
        "selected_zone":    "Zone:",
        "selected_time":    "GHHT:",
        "selected_noon":    "Zenith:",
        "err_title":        "Error",
        "err_numbers":      "Please enter valid numbers.",
        "err_lat_range":    "Latitude: -90…90.",
        "err_lon_range":    "Longitude: -180…180.",
        "city_not_found":   "City not found",
        "ghht_prefix":      "GHHT",
        "sub_label_fmt":    "{offset}   ·   Zenith: {noon}",
    },
    "ru": {
        "app_title":        "Часы и Карта Получасовых Поясов",
        "header_title":     "ГЛОБАЛЬНОЕ ПОЛУЧАСОВОЕ ВРЕМЯ",
        "coords_title":     "ВВЕДИТЕ ВАШИ КООРДИНАТЫ",
        "lat":              "ШИР",
        "lon":              "ДОЛ",
        "apply":            "ПРИМЕНИТЬ",
        "reset":            "СБРОС",
        "reset_tip":        "Сбросить зум карты (без изменения координат)",
        "search_title":     "ПОИСК ГОРОДА",
        "search_ph":        "Введите название...",
        "search_hint":      "Стрелки — выбор, Enter — перейти",
        "sync_title":       "СИНХРОНИЗАЦИЯ",
        "language":         "ЯЗЫК",
        "mode_auto":        "Автономный",
        "mode_ntp":         "Сетевой (NTP)",
        "ntp_off":          "NTP: отключено",
        "ntp_syncing":      "NTP: синхронизация…",
        "ntp_unreachable":  "NTP: недоступен → автономный",
        "ntp_ok":           "NTP: OK (Δ {ms:+.0f} мс)",
        "selected_title":   "ВЫБРАННАЯ ТОЧКА",
        "click_map":        "Кликните по карте",
        "quick_select":     "БЫСТРЫЙ ВЫБОР:",
        "map_hint":         "Клик — время | Колесо — зум | Зажать ЛКМ — панорама",
        "zenith":           "Зенит",
        "tooltip_lat":      "Широта",
        "tooltip_lon":      "Долгота",
        "tooltip_zone":     "Пояс",
        "tooltip_time":     "GHHT-время",
        "selected_lat":     "Широта:",
        "selected_lon":     "Долгота:",
        "selected_zone":    "Пояс:",
        "selected_time":    "GHHT:",
        "selected_noon":    "Зенит:",
        "err_title":        "Ошибка",
        "err_numbers":      "Введите корректные числа.",
        "err_lat_range":    "Широта: -90…90.",
        "err_lon_range":    "Долгота: -180…180.",
        "city_not_found":   "Город не найден",
        "ghht_prefix":      "GHHT",
        "sub_label_fmt":    "{offset}   ·   Зенит: {noon}",
    },
    "zh": {
        "app_title":        "半小时时区 — 时钟与地图",
        "header_title":     "全球半小时时区",
        "coords_title":     "输入您的坐标",
        "lat":              "纬度",
        "lon":              "经度",
        "apply":            "应用",
        "reset":            "重置",
        "reset_tip":        "重置地图缩放（坐标不变）",
        "search_title":     "搜索城市",
        "search_ph":        "输入城市名...",
        "search_hint":      "方向键选择，回车跳转",
        "sync_title":       "同步",
        "language":         "语言",
        "mode_auto":        "本地时间",
        "mode_ntp":         "网络 (NTP)",
        "ntp_off":          "NTP：已关闭",
        "ntp_syncing":      "NTP：正在同步…",
        "ntp_unreachable":  "NTP：不可达 → 本地时间",
        "ntp_ok":           "NTP：正常 (Δ {ms:+.0f} 毫秒)",
        "selected_title":   "选定点",
        "click_map":        "点击地图",
        "quick_select":     "快速选择：",
        "map_hint":         "点击—时间 | 滚轮—缩放 | 按住左键—平移",
        "zenith":           "正午",
        "tooltip_lat":      "纬度",
        "tooltip_lon":      "经度",
        "tooltip_zone":     "时区",
        "tooltip_time":     "GHHT 时间",
        "selected_lat":     "纬度：",
        "selected_lon":     "经度：",
        "selected_zone":    "时区：",
        "selected_time":    "GHHT：",
        "selected_noon":    "正午：",
        "err_title":        "错误",
        "err_numbers":      "请输入有效的数字。",
        "err_lat_range":    "纬度：-90…90。",
        "err_lon_range":    "经度：-180…180。",
        "city_not_found":   "城市未找到",
        "ghht_prefix":      "GHHT",
        "sub_label_fmt":    "{offset}   ·   正午：{noon}",
    },
    "ja": {
        "app_title":        "ハーフアワータイムゾーン — 時計と地図",
        "header_title":     "グローバル・ハーフアワータイム",
        "coords_title":     "座標を入力",
        "lat":              "緯度",
        "lon":              "経度",
        "apply":            "適用",
        "reset":            "リセット",
        "reset_tip":        "地図のズームをリセット（座標は変更なし）",
        "search_title":     "都市を検索",
        "search_ph":        "都市名を入力...",
        "search_hint":      "矢印キーで選択、Enter で移動",
        "sync_title":       "同期",
        "language":         "言語",
        "mode_auto":        "ローカル",
        "mode_ntp":         "ネットワーク (NTP)",
        "ntp_off":          "NTP：オフ",
        "ntp_syncing":      "NTP：同期中…",
        "ntp_unreachable":  "NTP：到達不能 → ローカル",
        "ntp_ok":           "NTP：OK (Δ {ms:+.0f} ミリ秒)",
        "selected_title":   "選択地点",
        "click_map":        "地図をクリック",
        "quick_select":     "クイック選択：",
        "map_hint":         "クリック—時刻 | ホイール—ズーム | 左ドラッグ—移動",
        "zenith":           "南中",
        "tooltip_lat":      "緯度",
        "tooltip_lon":      "経度",
        "tooltip_zone":     "タイムゾーン",
        "tooltip_time":     "GHHT 時刻",
        "selected_lat":     "緯度：",
        "selected_lon":     "経度：",
        "selected_zone":    "タイムゾーン：",
        "selected_time":    "GHHT：",
        "selected_noon":    "南中：",
        "err_title":        "エラー",
        "err_numbers":      "有効な数値を入力してください。",
        "err_lat_range":    "緯度：-90…90。",
        "err_lon_range":    "経度：-180…180。",
        "city_not_found":   "都市が見つかりません",
        "ghht_prefix":      "GHHT",
        "sub_label_fmt":    "{offset}   ·   南中：{noon}",
    },
    "ko": {
        "app_title":        "반시간 시간대 — 시계와 지도",
        "header_title":     "글로벌 반시간 시간",
        "coords_title":     "좌표를 입력하세요",
        "lat":              "위도",
        "lon":              "경도",
        "apply":            "적용",
        "reset":            "재설정",
        "reset_tip":        "지도 확대/축소 재설정 (좌표 유지)",
        "search_title":     "도시 검색",
        "search_ph":        "도시 이름 입력...",
        "search_hint":      "화살표 — 선택, Enter — 이동",
        "sync_title":       "동기화",
        "language":         "언어",
        "mode_auto":        "로컬 시간",
        "mode_ntp":         "네트워크 (NTP)",
        "ntp_off":          "NTP: 꺼짐",
        "ntp_syncing":      "NTP: 동기화 중…",
        "ntp_unreachable":  "NTP: 연결 불가 → 로컬 시간",
        "ntp_ok":           "NTP: 정상 (Δ {ms:+.0f} ms)",
        "selected_title":   "선택한 지점",
        "click_map":        "지도를 클릭하세요",
        "quick_select":     "빠른 선택:",
        "map_hint":         "클릭—시간 | 휠—확대 | 좌클릭 드래그—이동",
        "zenith":           "남중",
        "tooltip_lat":      "위도",
        "tooltip_lon":      "경도",
        "tooltip_zone":     "시간대",
        "tooltip_time":     "GHHT 시간",
        "selected_lat":     "위도:",
        "selected_lon":     "경도:",
        "selected_zone":    "시간대:",
        "selected_time":    "GHHT:",
        "selected_noon":    "남중:",
        "err_title":        "오류",
        "err_numbers":      "올바른 숫자를 입력하세요.",
        "err_lat_range":    "위도: -90…90.",
        "err_lon_range":    "경도: -180…180.",
        "city_not_found":   "도시를 찾을 수 없습니다",
        "ghht_prefix":      "GHHT",
        "sub_label_fmt":    "{offset}   ·   남중: {noon}",
    },
}

CITY_NAMES: Dict[str, Dict[str, str]] = {
    "ru": {
        "Москва": "Москва", "Санкт-Петербург": "Санкт-Петербург",
        "Лондон": "Лондон", "Париж": "Париж", "Берлин": "Берлин",
        "Нью-Йорк": "Нью-Йорк", "Лос-Анджелес": "Лос-Анджелес",
        "Токио": "Токио", "Пекин": "Пекин", "Сидней": "Сидней",
        "Сингапур": "Сингапур", "Дубай": "Дубай", "Каир": "Каир",
        "Рио-де-Жанейро": "Рио-де-Жанейро", "Дели": "Дели",
    },
    "en": {
        "Москва": "Moscow", "Санкт-Петербург": "Saint Petersburg",
        "Лондон": "London", "Париж": "Paris", "Берлин": "Berlin",
        "Нью-Йорк": "New York", "Лос-Анджелес": "Los Angeles",
        "Токио": "Tokyo", "Пекин": "Beijing", "Сидней": "Sydney",
        "Сингапур": "Singapore", "Дубай": "Dubai", "Каир": "Cairo",
        "Рио-де-Жанейро": "Rio de Janeiro", "Дели": "Delhi",
    },
    "zh": {
        "Москва": "莫斯科", "Санкт-Петербург": "圣彼得堡",
        "Лондон": "伦敦", "Париж": "巴黎", "Берлин": "柏林",
        "Нью-Йорк": "纽约", "Лос-Анджелес": "洛杉矶",
        "Токио": "东京", "Пекин": "北京", "Сидней": "悉尼",
        "Сингапур": "新加坡", "Дубай": "迪拜", "Каир": "开罗",
        "Рио-де-Жанейро": "里约热内卢", "Дели": "德里",
    },
    "ja": {
        "Москва": "モスクワ", "Санкт-Петербург": "サンクトペテルブルク",
        "Лондон": "ロンドン", "Париж": "パリ", "Берлин": "ベルリン",
        "Нью-Йорк": "ニューヨーク", "Лос-Анджелес": "ロサンゼルス",
        "Токио": "東京", "Пекин": "北京", "Сидней": "シドニー",
        "Сингапур": "シンガポール", "Дубай": "ドバイ", "Каир": "カイロ",
        "Рио-де-Жанейро": "リオデジャネイロ", "Дели": "デリー",
    },
    "ko": {
        "Москва": "모스크바", "Санкт-Петербург": "상트페테르부르크",
        "Лондон": "런던", "Париж": "파리", "Берлин": "베를린",
        "Нью-Йорк": "뉴욕", "Лос-Анджелес": "로스앤젤레스",
        "Токио": "도쿄", "Пекин": "베이징", "Сидней": "시드니",
        "Сингапур": "싱가포르", "Дубай": "두바이", "Каир": "카이로",
        "Рио-де-Жанейро": "리우데자네이루", "Дели": "델리",
    },
}


class I18N:
    def __init__(self, lang: str = DEFAULT_LANG):
        self._lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
        self._observers: list = []

    @property
    def lang(self) -> str:
        return self._lang

    def set_lang(self, lang: str):
        if lang not in TRANSLATIONS or lang == self._lang:
            return
        self._lang = lang
        for cb in list(self._observers):
            cb()

    def subscribe(self, cb: Callable[[], None]):
        self._observers.append(cb)

    def t(self, key: str, **fmt) -> str:
        table = TRANSLATIONS.get(self._lang) or TRANSLATIONS[DEFAULT_LANG]
        text = table.get(key) or TRANSLATIONS[DEFAULT_LANG].get(key, key)
        if fmt:
            try:
                return text.format(**fmt)
            except (KeyError, IndexError):
                return text
        return text

    def city(self, key_ru: str) -> str:
        table = CITY_NAMES.get(self._lang) or CITY_NAMES["ru"]
        return table.get(key_ru, key_ru)

    def city_reverse(self, display_name: str) -> Optional[str]:
        dn = display_name.strip().lower()
        for table in CITY_NAMES.values():
            for ru_key, disp in table.items():
                if disp.lower() == dn:
                    return ru_key
        return None


i18n = I18N(DEFAULT_LANG)