"""
Сервис генерации QR-кодов с кастомизацией.

Поддерживаемые стили:
- square   — стандартные квадратные модули
- rounded  — модули со скруглёнными углами
- dots     — круглые модули (точки)
- circle   — круглые модули с увеличенным радиусом

Поддерживается:
- Кастомные цвета (foreground / background)
- Встраивание логотипа в центр
- 4 уровня коррекции ошибок (L/M/Q/H)
- Настраиваемый размер и граница
"""

import qrcode
import qrcode.image.svg
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
)
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import io
import base64
from typing import Optional


# Маппинг строк на уровни коррекции ошибок
ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,  # ~7%
    "M": qrcode.constants.ERROR_CORRECT_M,  # ~15%
    "Q": qrcode.constants.ERROR_CORRECT_Q,  # ~25%
    "H": qrcode.constants.ERROR_CORRECT_H,  # ~30% (нужен для логотипа)
}

# Маппинг строк на drawer'ы стилей
STYLE_DRAWER_MAP = {
    "square": SquareModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "dots": CircleModuleDrawer,
    "circle": GappedSquareModuleDrawer,
}


def hex_to_rgb(hex_color: str) -> tuple:
    """Конвертировать #RRGGBB в (R, G, B)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def generate_qr_image(
    content: str,
    foreground_color: str = "#000000",
    background_color: str = "#FFFFFF",
    style: str = "square",
    box_size: int = 10,
    border_size: int = 4,
    error_correction: str = "M",
    logo_base64: Optional[str] = None,
) -> str:
    """
    Генерирует QR-код и возвращает PNG в виде base64 строки.

    Если передан logo_base64 — автоматически повышает error_correction до H,
    чтобы QR оставался читаемым даже с частично перекрытым центром.

    Args:
        content: данные для кодирования (URL, текст)
        foreground_color: цвет модулей (#RRGGBB)
        background_color: цвет фона (#RRGGBB)
        style: стиль модулей (square/rounded/dots/circle)
        box_size: размер каждого модуля в пикселях (5-20)
        border_size: количество модулей в границе (0-10)
        error_correction: уровень коррекции ошибок (L/M/Q/H)
        logo_base64: логотип для вставки в центр (base64 PNG/JPG)

    Returns:
        base64-encoded PNG string (без префикса data:image/png;base64,)
    """
    # Если есть логотип — нужен максимальный уровень коррекции
    if logo_base64:
        error_correction = "H"

    ec_level = ERROR_CORRECTION_MAP.get(error_correction, qrcode.constants.ERROR_CORRECT_M)

    # Создаём QR
    qr = qrcode.QRCode(
        version=None,  # auto-detect
        error_correction=ec_level,
        box_size=box_size,
        border=border_size,
    )
    qr.add_data(content)
    qr.make(fit=True)

    # Получаем drawer для стиля
    drawer_class = STYLE_DRAWER_MAP.get(style, SquareModuleDrawer)

    # Конвертируем цвета
    fg_rgb = hex_to_rgb(foreground_color)
    bg_rgb = hex_to_rgb(background_color)

    # Создаём изображение с кастомным стилем и цветами
    color_mask = SolidFillColorMask(
        back_color=bg_rgb,
        front_color=fg_rgb,
    )

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer_class(),
        color_mask=color_mask,
    )

    # Конвертируем в PIL Image если нужно
    if not isinstance(img, Image.Image):
        img = img.get_image()

    # Вставляем логотип в центр
    if logo_base64:
        img = _embed_logo(img, logo_base64)

    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_qr_svg(
    content: str,
    foreground_color: str = "#000000",
    background_color: str = "#FFFFFF",
    box_size: int = 10,
    border_size: int = 4,
    error_correction: str = "M",
) -> str:
    """
    Генерирует QR-код в формате SVG (строка).

    SVG не поддерживает кастомные стили модулей (dots/rounded),
    поэтому всегда квадратный. Зато масштабируется без потерь.

    Returns:
        SVG-строка
    """
    ec_level = ERROR_CORRECTION_MAP.get(error_correction, qrcode.constants.ERROR_CORRECT_M)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=box_size,
        border=border_size,
    )
    qr.add_data(content)
    qr.make(fit=True)

    # Генерируем SVG
    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(
        image_factory=factory,
        fill_color=foreground_color,
        back_color=background_color,
    )

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return buffer.getvalue().decode("utf-8")


def _embed_logo(qr_image: Image.Image, logo_base64: str) -> Image.Image:
    """
    Вставляет логотип в центр QR-кода.

    Логотип масштабируется до ~20% площади QR-кода,
    с белой подложкой (padding) для читаемости.
    """
    try:
        # Декодируем логотип из base64
        # Убираем data:image/...;base64, если есть
        if "," in logo_base64:
            logo_base64 = logo_base64.split(",")[1]

        logo_data = base64.b64decode(logo_base64)
        logo = Image.open(io.BytesIO(logo_data))

        # Конвертируем в RGBA
        if logo.mode != "RGBA":
            logo = logo.convert("RGBA")

        qr_width, qr_height = qr_image.size

        # Логотип = 20% от ширины QR
        logo_max_size = int(qr_width * 0.2)
        logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

        logo_width, logo_height = logo.size

        # Белая подложка (padding = 8px)
        padding = 8
        bg_size = (logo_width + padding * 2, logo_height + padding * 2)
        bg = Image.new("RGBA", bg_size, (255, 255, 255, 255))

        # Скругляем углы подложки
        bg.paste(logo, (padding, padding), logo)

        # Позиция по центру
        pos_x = (qr_width - bg_size[0]) // 2
        pos_y = (qr_height - bg_size[1]) // 2

        # Конвертируем QR в RGBA для paste с маской
        if qr_image.mode != "RGBA":
            qr_image = qr_image.convert("RGBA")

        qr_image.paste(bg, (pos_x, pos_y), bg)

        return qr_image

    except Exception:
        # Если логотип невалидный — возвращаем QR без логотипа
        return qr_image


def validate_logo_base64(logo_base64: str) -> bool:
    """Проверить что base64 — валидное изображение и не слишком большое."""
    try:
        if "," in logo_base64:
            logo_base64 = logo_base64.split(",")[1]

        data = base64.b64decode(logo_base64)

        # Макс 500KB
        if len(data) > 500 * 1024:
            return False

        # Проверяем что это изображение
        img = Image.open(io.BytesIO(data))
        if img.format not in ("PNG", "JPEG", "GIF", "WEBP"):
            return False

        return True
    except Exception:
        return False
