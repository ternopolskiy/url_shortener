"""
API для управления QR-кодами.

Эндпоинты:
- POST   /api/v1/qr          — создать QR-код
- GET    /api/v1/qr          — список QR-кодов пользователя
- GET    /api/v1/qr/{id}     — получить конкретный QR
- PATCH  /api/v1/qr/{id}     — обновить (title)
- DELETE /api/v1/qr/{id}     — удалить QR-код
- POST   /api/v1/qr/preview  — превью без сохранения
- GET    /api/v1/qr/{id}/download/{format}  — скачать PNG или SVG
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import math

from app.database import get_db
from app.models import QRCode, URL, User
from app.schemas import (
    QRCodeCreateRequest,
    QRCodeResponse,
    QRCodeListResponse,
    QRCodeUpdateRequest,
    QRCodePreviewRequest,
    QRCodePreviewResponse,
)
from app.core.dependencies import get_current_user
from app.services.qr_service import (
    generate_qr_image,
    generate_qr_svg,
    validate_logo_base64,
)
import base64

router = APIRouter(prefix="/api/v1/qr", tags=["qr-codes"])


def _generate_default_title(content: str) -> str:
    """Генерирует заголовок по умолчанию для QR-кода."""
    if len(content) > 50:
        content = content[:50] + "..."
    return f"QR: {content}"


def _build_response(qr_code: QRCode, linked_url: URL = None) -> dict:
    """Строит полный ответ с данными привязанной ссылки."""
    data = {
        "id": qr_code.id,
        "content": qr_code.content,
        "title": qr_code.title,
        "url_id": qr_code.url_id,
        "qr_image_base64": qr_code.qr_image_base64,
        "foreground_color": qr_code.foreground_color,
        "background_color": qr_code.background_color,
        "style": qr_code.style,
        "box_size": qr_code.box_size,
        "border_size": qr_code.border_size,
        "error_correction": qr_code.error_correction,
        "logo_base64": qr_code.logo_base64,
        "downloads_count": qr_code.downloads_count,
        "created_at": qr_code.created_at.isoformat() if qr_code.created_at else None,
        "updated_at": qr_code.updated_at.isoformat() if qr_code.updated_at else None,
    }
    
    if linked_url:
        data["linked_short_code"] = linked_url.short_code
        data["linked_clicks"] = linked_url.clicks_count
    
    return data


# ─── СОЗДАНИЕ ────────────────────────────────────────────────────

@router.post("", response_model=QRCodeResponse, status_code=201)
async def create_qr_code(
    data: QRCodeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать новый QR-код.

    Можно привязать к существующей ссылке (url_id) или задать
    произвольный URL в поле content.

    Если url_id указан — content берётся из короткой ссылки автоматически
    (формат: BASE_URL/short_code).
    """
    # Валидация логотипа
    if data.logo_base64:
        if not validate_logo_base64(data.logo_base64):
            raise HTTPException(
                status_code=400,
                detail="Невалидный логотип. Допустимые форматы: PNG, JPG, GIF, WebP. Макс. 500KB.",
            )

    # Если привязка к ссылке — проверяем владение
    linked_url = None
    content = data.content

    if data.url_id:
        linked_url = db.query(URL).filter(
            URL.id == data.url_id,
            URL.user_id == current_user.id,
        ).first()

        if not linked_url:
            raise HTTPException(
                status_code=404,
                detail="Ссылка не найдена или не принадлежит вам",
            )

        # Контент QR = короткая ссылка
        from app.config import settings
        content = f"{settings.BASE_URL}/{linked_url.short_code}"

    # Проверяем лимит QR-кодов (опционально)
    qr_count = db.query(QRCode).filter(
        QRCode.user_id == current_user.id
    ).count()

    if qr_count >= 50:  # Лимит для бесплатного плана
        raise HTTPException(
            status_code=403,
            detail="Достигнут лимит QR-кодов (50). Удалите ненужные.",
        )

    # Генерируем QR-изображение
    try:
        qr_image_base64 = generate_qr_image(
            content=content,
            foreground_color=data.foreground_color,
            background_color=data.background_color,
            style=data.style,
            box_size=data.box_size,
            border_size=data.border_size,
            error_correction=data.error_correction,
            logo_base64=data.logo_base64,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации QR-кода: {str(e)}",
        )

    # Сохраняем в БД
    qr_code = QRCode(
        user_id=current_user.id,
        url_id=data.url_id,
        content=content,
        title=data.title or _generate_default_title(content),
        qr_image_base64=qr_image_base64,
        foreground_color=data.foreground_color,
        background_color=data.background_color,
        style=data.style,
        box_size=data.box_size,
        border_size=data.border_size,
        error_correction=data.error_correction,
        logo_base64=data.logo_base64,
    )

    db.add(qr_code)
    db.commit()
    db.refresh(qr_code)

    return _build_response(qr_code, linked_url)


# ─── ПРЕВЬЮ (без сохранения) ─────────────────────────────────────

@router.post("/preview", response_model=QRCodePreviewResponse)
async def preview_qr_code(
    data: QRCodePreviewRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Сгенерировать превью QR-кода без сохранения в БД.
    Используется для live preview в конструкторе.
    """
    if data.logo_base64 and not validate_logo_base64(data.logo_base64):
        raise HTTPException(status_code=400, detail="Невалидный логотип")

    try:
        qr_image_base64 = generate_qr_image(
            content=data.content,
            foreground_color=data.foreground_color,
            background_color=data.background_color,
            style=data.style,
            box_size=data.box_size,
            border_size=data.border_size,
            error_correction=data.error_correction,
            logo_base64=data.logo_base64,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QRCodePreviewResponse(qr_image_base64=qr_image_base64)


# ─── СПИСОК ─────────────────────────────────────────────────────

@router.get("", response_model=QRCodeListResponse)
async def get_qr_codes(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить список QR-кодов текущего пользователя с пагинацией."""
    query = db.query(QRCode).filter(QRCode.user_id == current_user.id)

    # Поиск по title и content
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (QRCode.title.ilike(search_term)) |
            (QRCode.content.ilike(search_term))
        )

    # Считаем total
    total = query.count()
    pages = math.ceil(total / per_page) if total > 0 else 1

    # Пагинация
    qr_codes = query.order_by(desc(QRCode.created_at)) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    # Собираем ответ с данными привязанных ссылок
    items = []
    for qr in qr_codes:
        linked_url = None
        if qr.url_id:
            linked_url = db.query(URL).filter(URL.id == qr.url_id).first()
        items.append(_build_response(qr, linked_url))

    return QRCodeListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


# ─── ПОЛУЧИТЬ ОДИН ──────────────────────────────────────────────

@router.get("/{qr_id}", response_model=QRCodeResponse)
async def get_qr_code(
    qr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить конкретный QR-код по ID."""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id,
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR-код не найден")

    linked_url = None
    if qr_code.url_id:
        linked_url = db.query(URL).filter(URL.id == qr_code.url_id).first()

    return _build_response(qr_code, linked_url)


# ─── ОБНОВЛЕНИЕ ─────────────────────────────────────────────────

@router.patch("/{qr_id}", response_model=QRCodeResponse)
async def update_qr_code(
    qr_id: int,
    data: QRCodeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить QR-код.
    
    Можно обновить только title. Для изменения дизайна нужно создать новый QR.
    """
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id,
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR-код не найден")

    # Обновляем только title
    if data.title is not None:
        qr_code.title = data.title

    qr_code.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(qr_code)

    linked_url = None
    if qr_code.url_id:
        linked_url = db.query(URL).filter(URL.id == qr_code.url_id).first()

    return _build_response(qr_code, linked_url)


# ─── УДАЛЕНИЕ ───────────────────────────────────────────────────

@router.delete("/{qr_id}", status_code=204)
async def delete_qr_code(
    qr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить QR-код."""
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id,
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR-код не найден")

    db.delete(qr_code)
    db.commit()

    return None


# ─── СКАЧИВАНИЕ ─────────────────────────────────────────────────

@router.get("/{qr_id}/download/{format}")
async def download_qr_code(
    qr_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Скачать QR-код в формате PNG или SVG.
    
    PNG берётся из базы (уже сгенерированный),
    SVG генерируется на лету.
    """
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id,
    ).first()

    if not qr_code:
        raise HTTPException(status_code=404, detail="QR-код не найден")

    # Инкрементируем счётчик скачиваний
    qr_code.downloads_count += 1
    db.commit()

    format = format.lower()

    if format == "png":
        # Декодируем base64 и возвращаем PNG
        image_data = base64.b64decode(qr_code.qr_image_base64)
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="qr_{qr_code.id}.png"'
            },
        )

    elif format == "svg":
        # Генерируем SVG на лету
        svg_content = generate_qr_svg(
            content=qr_code.content,
            foreground_color=qr_code.foreground_color,
            background_color=qr_code.background_color,
            box_size=qr_code.box_size,
            border_size=qr_code.border_size,
            error_correction=qr_code.error_correction,
        )
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f'attachment; filename="qr_{qr_code.id}.svg"'
            },
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат. Доступны: png, svg",
        )
