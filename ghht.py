#!/usr/bin/env python3

# Written in 2026 by Iwakawa-2173
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
# See <http://creativecommons.org> for CC0 full legal text.


"""
Глобальное Получасовое Время
Clock and Half-Hour Time Zone Map — v16 (monochrome dark theme + i18n)

Settings stored in settings.json next to this script.
Requirements: Python 3.10+, PyQt6
"""

import sys
import os
import json
import socket
import struct
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple, Dict, Any, Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QFrame, QSizePolicy, QMessageBox, QGroupBox, QCompleter,
    QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QPoint, QStringListModel
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QFont, QPainterPath,
    QPolygonF, QFontMetrics, QPixmap, QGuiApplication, QTransform
)

from i18n import i18n, LANGUAGES, DEFAULT_LANG

# ============================================================================
# SETTINGS (plain JSON file next to the script — no registry!)
# ============================================================================

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "settings.json"
)


def load_settings() -> Dict[str, Any]:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def save_settings(data: Dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[WARN] Could not save settings: {e}")


# ============================================================================
# CONSTANTS & MONOCHROME DARK PALETTE
# ============================================================================

COLOR_BG          = QColor("#000000")
COLOR_PANEL       = QColor("#0a0a0a")
COLOR_PANEL_EDGE  = QColor("#1a1a1a")
COLOR_TEXT        = QColor("#e8e8e8")
COLOR_DIM         = QColor("#7a7a7a")
COLOR_MUTED       = QColor("#3a3a3a")
COLOR_ACCENT      = QColor("#ffffff")
COLOR_ACCENT_SOFT = QColor("#c8c8c8")
COLOR_INPUT_BG    = QColor("#141414")
COLOR_INPUT_BORDER= QColor("#2a2a2a")
COLOR_BTN_BG      = QColor("#1e1e1e")
COLOR_BTN_HOVER   = QColor("#2e2e2e")
COLOR_BTN_PRESSED = QColor("#3a3a3a")
COLOR_OCEAN       = QColor("#0d0d0d")
COLOR_LAND        = QColor("#2a2a2a")
COLOR_LAND_BORDER = QColor("#4a4a4a")
COLOR_CITY        = QColor("#b0b0b0")
COLOR_CITY_TEXT   = QColor("#8a8a8a")
COLOR_MARKER      = QColor("#ffffff")
COLOR_MARKER_GLOW = QColor(255, 255, 255, 70)
COLOR_SELECTED    = QColor("#e8e8e8")
COLOR_SELECTED_GLOW = QColor(232, 232, 232, 70)

GHHT_BAND_DEG = 7.5
LAND_GEOJSON = "ne_110m_land.geojson"
CITIES_GEOJSON = "ne_10m_populated_places.geojson"

# ============================================================================
# CITIES DATABASE (Quick Select)
# ============================================================================

CITIES = {
    "Москва": (55.7558, 37.6173),
    "Санкт-Петербург": (59.9343, 30.3351),
    "Лондон": (51.5074, -0.1278),
    "Париж": (48.8566, 2.3522),
    "Берлин": (52.5200, 13.4050),
    "Нью-Йорк": (40.7128, -74.0060),
    "Лос-Анджелес": (34.0522, -118.2437),
    "Токио": (35.6762, 139.6503),
    "Пекин": (39.9042, 116.4074),
    "Сидней": (-33.8688, 151.2093),
    "Сингапур": (1.3521, 103.8198),
    "Дубай": (25.2048, 55.2708),
    "Каир": (30.0444, 31.2357),
    "Рио-де-Жанейро": (-22.9068, -43.1729),
    "Дели": (28.6139, 77.2090),
}

# ============================================================================
# MATH
# ============================================================================

def GHHT_offset_hours(longitude: float) -> float:
    return round(longitude / GHHT_BAND_DEG) * 0.5

def GHHT_zone_index(longitude: float) -> int:
    return round(longitude / GHHT_BAND_DEG)

def solar_noon_local(longitude: float) -> float:
    off = GHHT_offset_hours(longitude)
    solar_noon_utc = 12.0 - (longitude / 15.0)
    return (solar_noon_utc + off) % 24.0

def format_offset(off: float) -> str:
    return f"GHHT+{off:.1f}" if off >= 0 else f"GHHT-{abs(off):.1f}"

def format_hm(hours_float: float) -> str:
    total_min = int(round(hours_float * 60)) % (24 * 60)
    return f"{total_min // 60:02d}:{total_min % 60:02d}"

# ============================================================================
# NTP CLIENT
# ============================================================================

class NTPClient:
    NTP_EPOCH_OFFSET = 2208988800

    @staticmethod
    def query(host: str = "pool.ntp.org", timeout: float = 1.0) -> Optional[datetime]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout)
            s.connect((host, 123))
            data = b'\x1b' + 47 * b'\0'
            s.send(data)
            resp = s.recv(48)
            s.close()
            if len(resp) < 48:
                return None
            secs, frac = struct.unpack("!II", resp[40:48])
            unix_secs = secs - NTPClient.NTP_EPOCH_OFFSET
            unix_time = unix_secs + frac / 2**32
            return datetime.fromtimestamp(unix_time, tz=timezone.utc)
        except Exception:
            return None

# ============================================================================
# MAP WIDGET
# ============================================================================

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.marker_lat = 55.8225
        self.marker_lon = 37.7616
        self.active_zone_lon = 0.0

        self.selected_lat: Optional[float] = None
        self.selected_lon: Optional[float] = None
        self.hover_lat: Optional[float] = None
        self.hover_lon: Optional[float] = None

        self.utc_provider = lambda: datetime.now(timezone.utc)

        self.on_point_selected: Optional[Callable[[float, float], None]] = None
        self.on_cities_loaded: Optional[Callable[[List[Dict[str, Any]]], None]] = None

        self.zoom = 1.0
        self.min_zoom = 1.0
        self.max_zoom = 20.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._dragging = False
        self._last_mouse_pos = QPointF()

        self._base_rect = QRectF()
        self._map_rect = QRectF()
        self._map_loaded = False

        self._land_polygons: List[QPolygonF] = []
        self._land_bounds: List[QRectF] = []
        self._cities: List[Dict[str, Any]] = []

        self._cache_pixmap: Optional[QPixmap] = None
        self._cache_rect: QRectF = QRectF()
        self._cache_zoom = 0.0
        self._cache_pan = QPointF()
        self._cache_map_rect: QRectF = QRectF()

        self._preview_only = False
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(80)
        self._refresh_timer.timeout.connect(self._full_refresh)

        self._load_geojson()

    # ------------------------------------------------------------------
    def set_on_cities_loaded(self, fn: Callable[[List[Dict[str, Any]]], None]):
        self.on_cities_loaded = fn
        if self._cities:
            fn(self._cities)

    def set_on_point_selected(self, fn: Callable[[float, float], None]):
        self.on_point_selected = fn

    # ------------------------------------------------------------------
    def _load_geojson(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        land_path = os.path.join(base_dir, LAND_GEOJSON)
        if not os.path.exists(land_path):
            land_path = LAND_GEOJSON

        if os.path.exists(land_path):
            try:
                with open(land_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                polygons = []
                for feature in data.get("features", []):
                    geom = feature.get("geometry", {})
                    gtype = geom.get("type", "")
                    coords = geom.get("coordinates", [])
                    if gtype == "Polygon":
                        for ring in coords:
                            polygons.append([(pt[1], pt[0]) for pt in ring])
                    elif gtype == "MultiPolygon":
                        for poly in coords:
                            for ring in poly:
                                polygons.append([(pt[1], pt[0]) for pt in ring])

                for poly in polygons:
                    qpoly = QPolygonF()
                    for lat, lon in poly:
                        qpoly.append(QPointF((lon + 180.0) / 360.0, (90.0 - lat) / 180.0))
                    if qpoly.isEmpty():
                        continue
                    self._land_polygons.append(qpoly)
                    self._land_bounds.append(qpoly.boundingRect())
                self._map_loaded = True
                print(f"[INFO] Land polygons loaded: {len(self._land_polygons)}")
            except Exception as e:
                print(f"[ERROR] Failed to load land: {e}")

        cities_path = os.path.join(base_dir, CITIES_GEOJSON)
        if not os.path.exists(cities_path):
            cities_path = CITIES_GEOJSON

        if os.path.exists(cities_path):
            try:
                with open(cities_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for feature in data.get("features", []):
                    geom = feature.get("geometry", {})
                    props = feature.get("properties", {})
                    if geom.get("type") == "Point":
                        coords = geom.get("coordinates", [])
                        if len(coords) >= 2:
                            lon, lat = coords[0], coords[1]
                            name = props.get("NAME") or props.get("NAMEASCII") or "Unknown"
                            try:
                                rank = int(props.get("SCALERANK", 10))
                            except Exception:
                                rank = 10
                            self._cities.append({
                                "lat": lat,
                                "lon": lon,
                                "name": name,
                                "rank": rank
                            })
                print(f"[INFO] Cities loaded: {len(self._cities)}")
            except Exception as e:
                print(f"[ERROR] Failed to load cities: {e}")

        if self.on_cities_loaded and self._cities:
            self.on_cities_loaded(self._cities)

    # ------------------------------------------------------------------
    def _update_rects(self):
        w, h = self.width(), self.height()
        margin = 8
        avail_w = w - 2 * margin
        avail_h = h - 2 * margin
        if avail_w / 2.0 <= avail_h:
            mw = avail_w
            mh = avail_w / 2.0
        else:
            mh = avail_h
            mw = avail_h * 2.0
        mx = (w - mw) / 2.0
        my = (h - mh) / 2.0
        self._base_rect = QRectF(mx, my, mw, mh)

        zw = self._base_rect.width() * self.zoom
        zh = self._base_rect.height() * self.zoom
        zx = self._base_rect.x() + (self._base_rect.width() - zw) / 2.0 + self.pan_x
        zy = self._base_rect.y() + (self._base_rect.height() - zh) / 2.0 + self.pan_y

        self._map_rect = QRectF(zx, zy, zw, zh)

    def _to_screen(self, lat: float, lon: float) -> QPointF:
        nx = (lon + 180.0) / 360.0
        ny = (90.0 - lat) / 180.0
        return QPointF(self._map_rect.x() + nx * self._map_rect.width(),
                       self._map_rect.y() + ny * self._map_rect.height())

    def _screen_to_latlon(self, px: float, py: float) -> Optional[Tuple[float, float]]:
        r = self._map_rect
        if r.width() <= 0 or r.height() <= 0:
            return None
        if px < r.left() or px > r.right() or py < r.top() or py > r.bottom():
            return None
        nx = (px - r.x()) / r.width()
        ny = (py - r.y()) / r.height()
        lon = nx * 360.0 - 180.0
        lat = 90.0 - ny * 180.0
        return (lat, lon)

    def _center_on(self, lat: float, lon: float):
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._update_rects()
        sp = self._to_screen(lat, lon)
        cx = self._base_rect.center().x()
        cy = self._base_rect.center().y()
        self.pan_x += cx - sp.x()
        self.pan_y += cy - sp.y()
        self._update_rects()

    def set_location(self, lat: float, lon: float, zoom: Optional[float] = None):
        self.marker_lat = lat
        self.marker_lon = lon
        self.active_zone_lon = GHHT_zone_index(lon) * GHHT_BAND_DEG
        self.zoom = zoom if zoom is not None else 1.0
        self._center_on(lat, lon)
        self._invalidate_cache()
        self.update()

    def set_utc_provider(self, fn):
        self.utc_provider = fn

    def _invalidate_cache(self):
        self._cache_pixmap = None
        self._preview_only = False

    def _full_refresh(self):
        self._preview_only = False
        self._cache_pixmap = None
        self.update()

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.fillRect(self.rect(), COLOR_BG)

        self._update_rects()

        need_full = (
            self._cache_pixmap is None
            or self._cache_rect != self._base_rect
            or self._cache_pixmap.size() != self.size()
        )

        if need_full:
            self._render_cache()

        p.save()
        if self._preview_only and self._cache_pixmap is not None and \
                self._cache_map_rect.width() > 0 and self._cache_map_rect.height() > 0:
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            old_r = self._cache_map_rect
            new_r = self._map_rect
            sx = new_r.width() / old_r.width()
            sy = new_r.height() / old_r.height()
            tx = new_r.x() - old_r.x() * sx
            ty = new_r.y() - old_r.y() * sy
            p.setClipRect(self._base_rect)
            p.translate(tx, ty)
            p.scale(sx, sy)
            p.drawPixmap(0, 0, self._cache_pixmap)
        else:
            p.drawPixmap(0, 0, self._cache_pixmap)
        p.restore()

        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.save()
        p.setClipRect(self._base_rect)

        self._draw_cities(p)

        self._draw_marker(p, self.marker_lat, self.marker_lon,
                          COLOR_MARKER, COLOR_MARKER_GLOW, 5)
        if self.selected_lat is not None:
            self._draw_marker(p, self.selected_lat, self.selected_lon,
                              COLOR_SELECTED, COLOR_SELECTED_GLOW, 6)
        if self.hover_lat is not None:
            sp = self._to_screen(self.hover_lat, self.hover_lon)
            p.setPen(QPen(COLOR_ACCENT_SOFT, 1.2, Qt.PenStyle.DotLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(sp, 10, 10)

        p.restore()

        p.setFont(QFont("Consolas", 9))
        p.setPen(COLOR_DIM)
        p.drawText(QRectF(10, self.height() - 20, self.width() - 20, 16),
                   Qt.AlignmentFlag.AlignLeft,
                   i18n.t("map_hint"))

    def _render_cache(self):
        self._cache_pixmap = QPixmap(self.size())
        self._cache_pixmap.fill(COLOR_BG)

        cache_p = QPainter(self._cache_pixmap)
        cache_p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        cache_p.setClipRect(self._base_rect)

        cache_p.setPen(Qt.PenStyle.NoPen)
        cache_p.setBrush(QBrush(COLOR_OCEAN))
        cache_p.drawRect(self._map_rect)

        if self._map_loaded:
            mr = self._map_rect
            tf = QTransform()
            tf.translate(mr.x(), mr.y())
            tf.scale(mr.width(), mr.height())

            inv, ok = tf.inverted()
            if ok:
                visible_norm = inv.mapRect(QRectF(self._base_rect).adjusted(-4, -4, 4, 4))
            else:
                visible_norm = QRectF(0, 0, 1, 1)

            cache_p.setTransform(tf)
            pen = QPen(COLOR_LAND_BORDER)
            pen.setCosmetic(True)
            pen.setWidthF(0.5)
            cache_p.setPen(pen)
            cache_p.setBrush(QBrush(COLOR_LAND))

            for qpoly, bbox in zip(self._land_polygons, self._land_bounds):
                if not bbox.intersects(visible_norm):
                    continue
                cache_p.drawPolygon(qpoly)

            cache_p.resetTransform()

        active_lon = self.active_zone_lon
        while active_lon < -180:
            active_lon += 360
        while active_lon >= 180:
            active_lon -= 360

        mr = self._map_rect

        zone_px = mr.width() * (GHHT_BAND_DEG / 360.0)
        if zone_px < 34.0:
            label_step = 4
        elif zone_px < 60.0:
            label_step = 2
        else:
            label_step = 1

        label_font = QFont("Consolas", 8, QFont.Weight.Bold)
        label_font_active = QFont("Consolas", 9, QFont.Weight.Bold)
        fm_label = QFontMetrics(label_font)
        fm_label_active = QFontMetrics(label_font_active)

        top_pad = 4

        for i in range(48):
            lon = -180.0 + i * GHHT_BAND_DEG
            x = mr.x() + ((lon + 180.0) / 360.0) * mr.width()

            is_active = abs(lon - active_lon) < 0.1
            visible_x = self._base_rect.left() - 2 <= x <= self._base_rect.right() + 2

            if visible_x:
                if is_active:
                    pen = QPen(COLOR_ACCENT, 2.0)
                    pen.setStyle(Qt.PenStyle.SolidLine)
                else:
                    pen = QPen(COLOR_MUTED, 0.8)
                    pen.setStyle(Qt.PenStyle.DashLine)
                cache_p.setPen(pen)
                cache_p.drawLine(QPointF(x, mr.top()), QPointF(x, mr.bottom()))

            if i % label_step != 0 and not is_active:
                continue
            if not is_active and not (-180.0 <= lon < 180.0):
                continue

            center_lon = lon + GHHT_BAND_DEG / 2.0
            if center_lon >= 180.0:
                continue
            cx = mr.x() + ((center_lon + 180.0) / 360.0) * mr.width()
            if cx < self._base_rect.left() - 40 or cx > self._base_rect.right() + 40:
                continue

            off = round(lon / GHHT_BAND_DEG) * 0.5
            text = format_offset(off)

            if is_active:
                cache_p.setFont(label_font_active)
                tw = fm_label_active.horizontalAdvance(text)
                th = fm_label_active.height()
            else:
                cache_p.setFont(label_font)
                tw = fm_label.horizontalAdvance(text)
                th = fm_label.height()

            plate = QRectF(cx - tw / 2.0 - 3, mr.top() + top_pad - 1,
                           tw + 6, th + 2)
            cache_p.setPen(Qt.PenStyle.NoPen)
            cache_p.setBrush(QBrush(QColor(0, 0, 0, 210)))
            cache_p.drawRect(plate)

            if is_active:
                cache_p.setPen(QPen(COLOR_ACCENT))
            else:
                cache_p.setPen(QPen(QColor("#8a8a8a")))
            cache_p.drawText(plate, Qt.AlignmentFlag.AlignCenter, text)

        cache_p.setPen(QPen(COLOR_MUTED, 0.8, Qt.PenStyle.DotLine))
        for lat in (-60, -30, 0, 30, 60):
            y = mr.y() + ((90.0 - lat) / 180.0) * mr.height()
            if y < self._base_rect.top() - 2 or y > self._base_rect.bottom() + 2:
                continue
            cache_p.drawLine(QPointF(mr.left(), y), QPointF(mr.right(), y))

        cache_p.setPen(QPen(COLOR_LAND_BORDER, 1.5))
        cache_p.setBrush(Qt.BrushStyle.NoBrush)
        cache_p.drawRect(mr)

        cache_p.end()

        self._cache_rect = QRectF(self._base_rect)
        self._cache_zoom = self.zoom
        self._cache_pan = QPointF(self.pan_x, self.pan_y)
        self._cache_map_rect = QRectF(self._map_rect)

    def _draw_cities(self, p: QPainter):
        if not self._cities:
            return

        if self.zoom < 1.5:
            max_rank = 1
        elif self.zoom < 2.5:
            max_rank = 2
        elif self.zoom < 4.0:
            max_rank = 4
        elif self.zoom < 7.0:
            max_rank = 6
        else:
            max_rank = 10

        mr = self._map_rect
        tf = QTransform()
        tf.translate(mr.x(), mr.y())
        tf.scale(mr.width(), mr.height())

        view = QRectF(self._base_rect).adjusted(-30, -20, 150, 20)

        candidates: List[Tuple[Dict[str, Any], QPointF]] = []
        for c in self._cities:
            if c["rank"] > max_rank:
                continue
            n = QPointF((c["lon"] + 180.0) / 360.0, (90.0 - c["lat"]) / 180.0)
            sp = tf.map(n)
            if not view.contains(sp):
                continue
            candidates.append((c, sp))

        if not candidates:
            return

        candidates.sort(key=lambda t: t[0]["rank"])

        font = QFont("Consolas", 8)
        p.setFont(font)
        fm = QFontMetrics(font)

        occupied_rects: List[QRectF] = []

        for city, pt in candidates:
            radius = 2.5 if city["rank"] <= 2 else 1.5
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(COLOR_CITY))
            p.drawEllipse(pt, radius, radius)

            if city["rank"] <= max_rank - 2 or self.zoom > 3.0:
                text_rect = fm.boundingRect(city["name"])
                tr = QRectF(pt.x() + 5,
                            pt.y() + text_rect.height() / 2 - text_rect.height(),
                            text_rect.width(),
                            text_rect.height())

                collision = False
                for occupied in occupied_rects:
                    if occupied.intersects(tr):
                        collision = True
                        break
                if not collision:
                    occupied_rects.append(tr)
                    p.setPen(QPen(COLOR_CITY_TEXT))
                    p.drawText(tr,
                               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                               city["name"])
                    p.setPen(Qt.PenStyle.NoPen)

    def _draw_marker(self, p: QPainter, lat: float, lon: float,
                     fill: QColor, glow: QColor, r: int):
        sp = self._to_screen(lat, lon)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(sp, r + 4, r + 4)
        p.setBrush(QBrush(fill))
        p.setPen(QPen(QColor("#000000"), 1.2))
        p.drawEllipse(sp, r, r)

    # ------------------------------------------------------------------
    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle == 0:
            return

        old_pos = event.position()
        latlon_before = self._screen_to_latlon(old_pos.x(), old_pos.y())

        zoom_factor = 1.2 if angle > 0 else 1 / 1.2
        new_zoom = self.zoom * zoom_factor
        self.zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        self._update_rects()

        if latlon_before is not None:
            new_pos = self._to_screen(latlon_before[0], latlon_before[1])
            dx = old_pos.x() - new_pos.x()
            dy = old_pos.y() - new_pos.y()
            self.pan_x += dx
            self.pan_y += dy
            self._update_rects()

        self._preview_only = True
        self._refresh_timer.start()
        self.update()
        event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position()

        if self._dragging:
            dx = pos.x() - self._last_mouse_pos.x()
            dy = pos.y() - self._last_mouse_pos.y()
            self.pan_x += dx
            self.pan_y += dy
            self._last_mouse_pos = pos
            self._update_rects()
            self._preview_only = True
            self._refresh_timer.start()
            self.update()
            self.hover_lat = self.hover_lon = None
            return

        res = self._screen_to_latlon(pos.x(), pos.y())
        if res is None:
            self.hover_lat = self.hover_lon = None
            self.setToolTip("")
        else:
            lat, lon = res
            self.hover_lat, self.hover_lon = lat, lon
            bt = self.utc_provider() + timedelta(hours=GHHT_offset_hours(lon))
            off = GHHT_offset_hours(lon)

            city_hover = None
            for c in self._cities:
                cp = self._to_screen(c["lat"], c["lon"])
                if (cp - pos).manhattanLength() < 10:
                    city_hover = c
                    break

            tooltip = (
                f"{i18n.t('tooltip_lat')}: {lat:+.2f}°\n"
                f"{i18n.t('tooltip_lon')}: {lon:+.2f}°\n"
                f"{i18n.t('tooltip_zone')}: {format_offset(off)}\n"
                f"{i18n.t('tooltip_time')}: {bt.strftime('%H:%M:%S')}"
            )
            if city_hover:
                tooltip = f"{city_hover['name']}\n" + tooltip

            self.setToolTip(tooltip)

        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hover_lat = self.hover_lon = None
        self.setToolTip("")
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(Qt.CursorShape.CrossCursor)
            pos = event.position()
            dist = (pos - self._last_mouse_pos).manhattanLength()
            if dist < 5:
                res = self._screen_to_latlon(pos.x(), pos.y())
                if res is not None:
                    lat, lon = res
                    self.selected_lat, self.selected_lon = lat, lon
                    self.update()
                    if self.on_point_selected:
                        self.on_point_selected(lat, lon)
            event.accept()

# ============================================================================
# BIG CLOCK HEADER WIDGET
# ============================================================================

class ClockHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 8, 20, 8)
        lay.setSpacing(2)

        self.title_label = QLabel(i18n.t("header_title"))
        self.title_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            f"color: {COLOR_DIM.name()}; letter-spacing: 4px;"
        )
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.title_label)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setStyleSheet(
            f"color: {COLOR_ACCENT.name()};"
            f" background: transparent;"
        )
        self.clock_label.setFont(QFont("Consolas", 72, QFont.Weight.Bold))
        lay.addWidget(self.clock_label, 1)

        self.sub_label = QLabel("GHHT+0.0")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setFont(QFont("Consolas", 12))
        self.sub_label.setStyleSheet(f"color: {COLOR_TEXT.name()};")
        lay.addWidget(self.sub_label)

    def update_clock(self, text: str, offset_text: str, noon_text: str):
        self.clock_label.setText(text)
        self.sub_label.setText(
            i18n.t("sub_label_fmt", offset=offset_text, noon=noon_text)
        )

    def retranslate(self):
        self.title_label.setText(i18n.t("header_title"))

# ============================================================================
# MAIN WINDOW — DASHBOARD LAYOUT
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(i18n.t("app_title"))

        self._settings = load_settings()

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            avail = screen.availableGeometry()
            w = min(1280, int(avail.width() * 0.95))
            h = min(860, int(avail.height() * 0.95))
            self.resize(w, h)
            self.move(avail.center().x() - w // 2,
                      avail.center().y() - h // 2)
        else:
            self.resize(1280, 860)

        self.latitude = 55.8225
        self.longitude = 37.7616
        self.time_mode = "auto"
        self.ntp_offset = 0.0
        self.ntp_ok = False

        self.selected_lat: Optional[float] = None
        self.selected_lon: Optional[float] = None

        self._city_dict: Dict[str, Tuple[float, float]] = {}
        self._city_buttons: List[Tuple[QPushButton, str]] = []

        self._build_ui()

        i18n.subscribe(self._retranslate_all)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(200)

        self.ntp_timer = QTimer(self)
        self.ntp_timer.timeout.connect(self._sync_ntp)
        self.ntp_timer.start(30000)

        self.map.set_location(self.latitude, self.longitude)
        self.map.set_utc_provider(self._current_utc)
        self.map.set_on_point_selected(self._on_map_click)
        self.map.set_on_cities_loaded(self._on_cities_loaded)

        self._update_clock()

    # ------------------------------------------------------------------
    def _on_cities_loaded(self, cities: List[Dict[str, Any]]):
        self._city_dict = {}
        for c in cities:
            name = c["name"]
            lat, lon = c["lat"], c["lon"]
            if name in self._city_dict:
                if self._city_dict[name] == (lat, lon):
                    continue
                unique = f"{name} ({lat:.2f}, {lon:.2f})"
                self._city_dict[unique] = (lat, lon)
            else:
                self._city_dict[name] = (lat, lon)

        from i18n import CITY_NAMES
        for ru_name, (la, lo) in CITIES.items():
            self._city_dict[ru_name] = (la, lo)
            for table in CITY_NAMES.values():
                alias = table.get(ru_name)
                if alias:
                    self._city_dict[alias] = (la, lo)

        names = sorted(self._city_dict.keys(), key=str.lower)
        self._completer_model.setStringList(names)
        print(f"[INFO] Search completer populated with {len(names)} names.")

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(
            f"background-color: {COLOR_BG.name()}; color: {COLOR_TEXT.name()};"
        )

        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 8, 12, 12)
        outer.setSpacing(8)

        # ============ TOP: BIG CLOCK HEADER ============
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setStyleSheet(
            f"#HeaderFrame {{"
            f" background-color: {COLOR_PANEL.name()};"
            f" border-radius: 10px;"
            f" border: 1px solid {COLOR_PANEL_EDGE.name()};"
            f"}}"
        )
        hf_lay = QVBoxLayout(header_frame)
        hf_lay.setContentsMargins(0, 0, 0, 0)
        self.header = ClockHeader()
        hf_lay.addWidget(self.header)
        outer.addWidget(header_frame)

        # ============ MIDDLE: FULL-SCREEN MAP ============
        map_frame = QFrame()
        map_frame.setStyleSheet(
            f"background-color: {COLOR_PANEL.name()};"
            f" border-radius: 10px;"
            f" border: 1px solid {COLOR_PANEL_EDGE.name()};"
        )
        mf_lay = QVBoxLayout(map_frame)
        mf_lay.setContentsMargins(6, 6, 6, 6)
        self.map = MapWidget()
        mf_lay.addWidget(self.map)
        outer.addWidget(map_frame, 1)

        # ============ BOTTOM: DASHBOARD ============
        dashboard = QFrame()
        dashboard.setObjectName("Dashboard")
        dashboard.setStyleSheet(
            f"#Dashboard {{"
            f" background-color: {COLOR_PANEL.name()};"
            f" border-radius: 10px;"
            f" border: 1px solid {COLOR_PANEL_EDGE.name()};"
            f"}}"
        )
        dash_lay = QHBoxLayout(dashboard)
        dash_lay.setContentsMargins(14, 10, 14, 10)
        dash_lay.setSpacing(14)

        # --- Column 1: Coordinates + Apply / Reset ---
        col1 = QFrame()
        c1 = QVBoxLayout(col1)
        c1.setContentsMargins(0, 0, 0, 0)
        c1.setSpacing(6)

        self.t1 = QLabel(i18n.t("coords_title"))
        self.t1.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.t1.setStyleSheet(f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px;")
        c1.addWidget(self.t1)

        row_lat = QHBoxLayout()
        row_lat.setSpacing(6)
        self.lbl_lat = QLabel(i18n.t("lat"))
        self.lbl_lat.setFont(QFont("Consolas", 9))
        self.lbl_lat.setStyleSheet(f"color: {COLOR_DIM.name()};")
        self.lbl_lat.setFixedWidth(30)
        row_lat.addWidget(self.lbl_lat)
        self.lat_edit = QLineEdit(f"{self.latitude:.4f}")
        self.lat_edit.setFont(QFont("Consolas", 11))
        self.lat_edit.setStyleSheet(self._edit_style())
        row_lat.addWidget(self.lat_edit, 1)
        c1.addLayout(row_lat)

        row_lon = QHBoxLayout()
        row_lon.setSpacing(6)
        self.lbl_lon = QLabel(i18n.t("lon"))
        self.lbl_lon.setFont(QFont("Consolas", 9))
        self.lbl_lon.setStyleSheet(f"color: {COLOR_DIM.name()};")
        self.lbl_lon.setFixedWidth(30)
        row_lon.addWidget(self.lbl_lon)
        self.lon_edit = QLineEdit(f"{self.longitude:.4f}")
        self.lon_edit.setFont(QFont("Consolas", 11))
        self.lon_edit.setStyleSheet(self._edit_style())
        row_lon.addWidget(self.lon_edit, 1)
        c1.addLayout(row_lon)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self.apply_btn = QPushButton(i18n.t("apply"))
        self.apply_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.apply_btn.setStyleSheet(self._primary_button_style())
        self.apply_btn.clicked.connect(self._apply_coords)
        btn_row.addWidget(self.apply_btn, 2)

        self.reset_btn = QPushButton(i18n.t("reset"))
        self.reset_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.reset_btn.setStyleSheet(self._city_button_style())
        self.reset_btn.setToolTip(i18n.t("reset_tip"))
        self.reset_btn.clicked.connect(self._reset_zoom)
        btn_row.addWidget(self.reset_btn, 1)
        c1.addLayout(btn_row)

        c1.addStretch(1)
        dash_lay.addWidget(col1, 2)

        # --- Column 2: Search ---
        col2 = QFrame()
        c2 = QVBoxLayout(col2)
        c2.setContentsMargins(0, 0, 0, 0)
        c2.setSpacing(6)

        self.t2 = QLabel(i18n.t("search_title"))
        self.t2.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.t2.setStyleSheet(f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px;")
        c2.addWidget(self.t2)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(i18n.t("search_ph"))
        self.search_edit.setFont(QFont("Consolas", 11))
        self.search_edit.setStyleSheet(self._edit_style())
        c2.addWidget(self.search_edit)

        self._completer_model = QStringListModel(self)
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(12)

        popup = self._completer.popup()
        if popup is not None:
            popup.setStyleSheet(f"""
                QListView {{
                    background-color: {COLOR_INPUT_BG.name()};
                    color: {COLOR_TEXT.name()};
                    border: 1px solid {COLOR_INPUT_BORDER.name()};
                    font-family: Consolas;
                    font-size: 12px;
                    outline: none;
                }}
                QListView::item:selected {{
                    background-color: #2e2e2e;
                    color: #ffffff;
                }}
            """)

        self.search_edit.setCompleter(self._completer)
        self._completer.activated[str].connect(self._on_search_activated)
        self.search_edit.returnPressed.connect(self._on_search_enter)

        self.hint_label = QLabel(i18n.t("search_hint"))
        self.hint_label.setFont(QFont("Consolas", 8))
        self.hint_label.setStyleSheet(f"color: {COLOR_DIM.name()};")
        c2.addWidget(self.hint_label)
        c2.addStretch(1)
        dash_lay.addWidget(col2, 2)

        # --- Column 3: Time sync + Language ---
        col3 = QFrame()
        c3 = QVBoxLayout(col3)
        c3.setContentsMargins(0, 0, 0, 0)
        c3.setSpacing(6)

        self.t3 = QLabel(i18n.t("sync_title"))
        self.t3.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.t3.setStyleSheet(f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px;")
        c3.addWidget(self.t3)

        self.rb_auto = QRadioButton(i18n.t("mode_auto"))
        self.rb_ntp = QRadioButton(i18n.t("mode_ntp"))
        self.rb_auto.setChecked(True)
        for rb in (self.rb_auto, self.rb_ntp):
            rb.setFont(QFont("Consolas", 10))
            rb.setStyleSheet(f"color: {COLOR_TEXT.name()};")
            c3.addWidget(rb)

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.rb_auto, 0)
        self.mode_group.addButton(self.rb_ntp, 1)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        self.ntp_status = QLabel(i18n.t("ntp_off"))
        self.ntp_status.setFont(QFont("Consolas", 8))
        self.ntp_status.setStyleSheet(f"color: {COLOR_DIM.name()};")
        c3.addWidget(self.ntp_status)

        self.lang_label = QLabel(i18n.t("language"))
        self.lang_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.lang_label.setStyleSheet(
            f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px; margin-top: 4px;"
        )
        c3.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.setFont(QFont("Consolas", 10))
        self.lang_combo.setStyleSheet(self._edit_style())
        for code, name in LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        idx = self.lang_combo.findData(i18n.lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        c3.addWidget(self.lang_combo)

        c3.addStretch(1)
        dash_lay.addWidget(col3, 2)

        # --- Column 4: Selected point ---
        col4 = QFrame()
        c4 = QVBoxLayout(col4)
        c4.setContentsMargins(0, 0, 0, 0)
        c4.setSpacing(6)

        self.t4 = QLabel(i18n.t("selected_title"))
        self.t4.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.t4.setStyleSheet(f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px;")
        c4.addWidget(self.t4)

        self.click_info = QLabel(i18n.t("click_map"))
        self.click_info.setFont(QFont("Consolas", 9))
        self.click_info.setStyleSheet(f"color: {COLOR_TEXT.name()};")
        self.click_info.setWordWrap(True)
        c4.addWidget(self.click_info)
        c4.addStretch(1)
        dash_lay.addWidget(col4, 3)

        outer.addWidget(dashboard, 0)

        # ============ BOTTOM-STRIP: QUICK SELECT ============
        quick_frame = QFrame()
        quick_frame.setStyleSheet(
            f"background-color: {COLOR_PANEL.name()};"
            f" border-radius: 10px;"
            f" border: 1px solid {COLOR_PANEL_EDGE.name()};"
        )
        qf_lay = QHBoxLayout(quick_frame)
        qf_lay.setContentsMargins(14, 8, 14, 8)
        qf_lay.setSpacing(6)

        self.qlbl = QLabel(i18n.t("quick_select"))
        self.qlbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.qlbl.setStyleSheet(f"color: {COLOR_ACCENT.name()}; letter-spacing: 2px;")
        qf_lay.addWidget(self.qlbl)

        self._city_buttons = []
        for ru_name, (la, lo) in CITIES.items():
            b = QPushButton(i18n.city(ru_name))
            b.setFont(QFont("Consolas", 8))
            b.setStyleSheet(self._city_button_style())
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.clicked.connect(lambda checked=False, a=la, o=lo: self._set_location(a, o))
            qf_lay.addWidget(b, 1)
            self._city_buttons.append((b, ru_name))

        outer.addWidget(quick_frame, 0)

    # ------------------------------------------------------------------
    def _on_lang_changed(self, index: int):
        code = self.lang_combo.itemData(index)
        if not code:
            return
        i18n.set_lang(code)
        # Persist to settings.json
        self._settings["lang"] = i18n.lang
        save_settings(self._settings)

    def _retranslate_all(self):
        self.setWindowTitle(i18n.t("app_title"))
        self.header.retranslate()

        self.t1.setText(i18n.t("coords_title"))
        self.lbl_lat.setText(i18n.t("lat"))
        self.lbl_lon.setText(i18n.t("lon"))
        self.apply_btn.setText(i18n.t("apply"))
        self.reset_btn.setText(i18n.t("reset"))
        self.reset_btn.setToolTip(i18n.t("reset_tip"))

        self.t2.setText(i18n.t("search_title"))
        self.search_edit.setPlaceholderText(i18n.t("search_ph"))
        self.hint_label.setText(i18n.t("search_hint"))

        self.t3.setText(i18n.t("sync_title"))
        self.rb_auto.setText(i18n.t("mode_auto"))
        self.rb_ntp.setText(i18n.t("mode_ntp"))
        self.lang_label.setText(i18n.t("language"))
        if self.time_mode == "ntp" and self.ntp_ok:
            self.ntp_status.setText(i18n.t("ntp_ok", ms=self.ntp_offset * 1000))
        elif self.time_mode == "ntp":
            self.ntp_status.setText(i18n.t("ntp_syncing"))
        else:
            self.ntp_status.setText(i18n.t("ntp_off"))

        self.t4.setText(i18n.t("selected_title"))
        if self.selected_lat is None:
            self.click_info.setText(i18n.t("click_map"))

        self.qlbl.setText(i18n.t("quick_select"))
        for btn, ru_name in self._city_buttons:
            btn.setText(i18n.city(ru_name))

        self._update_clock()
        if self.selected_lat is not None:
            self._render_selected_point()

        self.map.update()

    # ------------------------------------------------------------------
    def _on_search_activated(self, name: str):
        self._navigate_to_city(name)

    def _on_search_enter(self):
        text = self.search_edit.text().strip()
        if not text:
            return

        if text in self._city_dict:
            self._navigate_to_city(text)
            return

        ru_key = i18n.city_reverse(text)
        if ru_key and i18n.city(ru_key) in self._city_dict:
            self._navigate_to_city(i18n.city(ru_key))
            return

        text_lower = text.lower()
        matches = [n for n in self._city_dict.keys() if text_lower in n.lower()]

        if not matches:
            self.search_edit.setToolTip(i18n.t("city_not_found"))
            return

        if len(matches) == 1:
            self._navigate_to_city(matches[0])
            return

        self._completer.setCompletionPrefix(text)
        self._completer.complete()
        popup = self._completer.popup()
        if popup is not None and self._completer.completionModel().rowCount() > 0:
            popup.setCurrentIndex(self._completer.completionModel().index(0, 0))

    def _navigate_to_city(self, name: str):
        if name not in self._city_dict:
            return
        lat, lon = self._city_dict[name]
        self._set_location(lat, lon, zoom=4.0)
        self.map.selected_lat = lat
        self.map.selected_lon = lon
        self.map.update()
        self.selected_lat, self.selected_lon = lat, lon
        self._render_selected_point()
        self.search_edit.setText(name)
        self.search_edit.clearFocus()

    # ------------------------------------------------------------------
    def _edit_style(self) -> str:
        return f"""
            QLineEdit, QComboBox {{
                background-color: {COLOR_INPUT_BG.name()};
                color: {COLOR_TEXT.name()};
                border: 1px solid {COLOR_INPUT_BORDER.name()};
                border-radius: 4px;
                padding: 5px 7px;
                selection-background-color: #3a3a3a;
                selection-color: #ffffff;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid #5a5a5a; }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_INPUT_BG.name()};
                color: {COLOR_TEXT.name()};
                selection-background-color: #2e2e2e;
                selection-color: #ffffff;
                border: 1px solid {COLOR_INPUT_BORDER.name()};
            }}
        """

    def _primary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLOR_ACCENT.name()};
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #e0e0e0; }}
            QPushButton:pressed {{ background-color: #c8c8c8; }}
        """

    def _city_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLOR_BTN_BG.name()};
                color: {COLOR_TEXT.name()};
                border: 1px solid {COLOR_INPUT_BORDER.name()};
                border-radius: 4px;
                padding: 5px 4px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_HOVER.name()};
                color: #ffffff;
                border: 1px solid #4a4a4a;
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_PRESSED.name()};
            }}
        """

    # ------------------------------------------------------------------
    def _on_mode_changed(self, button):
        if button == self.rb_ntp:
            self.time_mode = "ntp"
            self.ntp_status.setText(i18n.t("ntp_syncing"))
            self._sync_ntp()
        else:
            self.time_mode = "auto"
            self.ntp_ok = False
            self.ntp_status.setText(i18n.t("ntp_off"))
        self._update_clock()

    def _apply_coords(self):
        try:
            lat = float(self.lat_edit.text().replace(",", "."))
            lon = float(self.lon_edit.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, i18n.t("err_title"), i18n.t("err_numbers"))
            return
        if not (-90.0 <= lat <= 90.0):
            QMessageBox.warning(self, i18n.t("err_title"), i18n.t("err_lat_range"))
            return
        if not (-180.0 <= lon <= 180.0):
            QMessageBox.warning(self, i18n.t("err_title"), i18n.t("err_lon_range"))
            return
        self._set_location(lat, lon)

    def _reset_zoom(self):
        self.map.set_location(self.latitude, self.longitude, zoom=1.0)

    def _set_location(self, lat: float, lon: float, zoom: Optional[float] = None):
        self.latitude = lat
        self.longitude = lon
        self.lat_edit.setText(f"{lat:.4f}")
        self.lon_edit.setText(f"{lon:.4f}")
        self.map.set_location(lat, lon, zoom=zoom)
        self._update_clock()

    def _on_map_click(self, lat: float, lon: float):
        self.selected_lat, self.selected_lon = lat, lon
        self._render_selected_point()

    def _render_selected_point(self):
        if self.selected_lat is None:
            return
        lat, lon = self.selected_lat, self.selected_lon
        off = GHHT_offset_hours(lon)
        bt = self._current_utc() + timedelta(hours=off)
        noon = solar_noon_local(lon)
        self.click_info.setText(
            f"{i18n.t('selected_lat')} {lat:+.3f}°\n"
            f"{i18n.t('selected_lon')} {lon:+.3f}°\n"
            f"{i18n.t('selected_zone')} {format_offset(off)}\n"
            f"{i18n.t('selected_time')} {bt.strftime('%H:%M:%S')}\n"
            f"{i18n.t('selected_noon')} {format_hm(noon)}"
        )

    def _sync_ntp(self):
        if self.time_mode != "ntp":
            return
        result = NTPClient.query("pool.ntp.org", timeout=1.0)
        if result is None:
            self.rb_auto.setChecked(True)
            self.time_mode = "auto"
            self.ntp_ok = False
            self.ntp_status.setText(i18n.t("ntp_unreachable"))
            self._update_clock()
            return
        now_utc = datetime.now(timezone.utc)
        self.ntp_offset = (result - now_utc).total_seconds()
        self.ntp_ok = True
        self.ntp_status.setText(i18n.t("ntp_ok", ms=self.ntp_offset * 1000))

    def _current_utc(self) -> datetime:
        if self.time_mode == "ntp" and self.ntp_ok:
            return datetime.now(timezone.utc) + timedelta(seconds=self.ntp_offset)
        return datetime.now(timezone.utc)

    def _update_clock(self):
        utc_now = self._current_utc()
        off = GHHT_offset_hours(self.longitude)
        bt = utc_now + timedelta(hours=off)
        noon = format_hm(solar_noon_local(self.longitude))

        self.header.update_clock(
            bt.strftime("%H:%M:%S"),
            format_offset(off),
            noon,
        )

        new_zone_lon = GHHT_zone_index(self.longitude) * GHHT_BAND_DEG
        if abs(self.map.active_zone_lon - new_zone_lon) > 1e-6:
            self.map.active_zone_lon = new_zone_lon
            self.map._invalidate_cache()
            self.map.update()

        if self.selected_lat is not None:
            self._render_selected_point()

    def closeEvent(self, event):
        self.clock_timer.stop()
        self.ntp_timer.stop()
        super().closeEvent(event)

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    # Load language from settings.json (default: en)
    settings = load_settings()
    saved_lang = settings.get("lang", DEFAULT_LANG)
    if saved_lang in LANGUAGES:
        i18n.set_lang(saved_lang)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from PyQt6.QtGui import QPalette
    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, COLOR_BG)
    pal.setColor(QPalette.ColorRole.WindowText, COLOR_TEXT)
    pal.setColor(QPalette.ColorRole.Base, COLOR_INPUT_BG)
    pal.setColor(QPalette.ColorRole.AlternateBase, COLOR_PANEL)
    pal.setColor(QPalette.ColorRole.Text, COLOR_TEXT)
    pal.setColor(QPalette.ColorRole.Button, COLOR_BTN_BG)
    pal.setColor(QPalette.ColorRole.ButtonText, COLOR_TEXT)
    pal.setColor(QPalette.ColorRole.ToolTipBase, COLOR_INPUT_BG)
    pal.setColor(QPalette.ColorRole.ToolTipText, COLOR_TEXT)
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()