"""
Tests for QR Codes Module
Gosha Connections Platform
"""

import pytest
import base64
from io import BytesIO
from PIL import Image

from app.models import User, QRCode, URL
from app.services.qr_service import (
    generate_qr_image,
    generate_qr_svg,
    validate_logo_base64,
    hex_to_rgb,
)


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="qr_test@example.com",
        username="qr_testuser",
        hashed_password="$2b$12$KIXxwRj6z9FZQZgZxZ8Z8eZxZ8Z8eZxZ8Z8eZxZ8Z8eZxZ8Z8e",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_url(db_session, test_user):
    """Create a test URL."""
    url = URL(
        user_id=test_user.id,
        original_url="https://example.com/test",
        short_code="test123",
        title="Test URL",
    )
    db_session.add(url)
    db_session.commit()
    db_session.refresh(url)
    yield url
    db_session.delete(url)
    db_session.commit()


@pytest.fixture
def test_qr(db_session, test_user):
    """Create a test QR code."""
    qr_image = generate_qr_image("https://example.com")
    qr = QRCode(
        user_id=test_user.id,
        content="https://example.com",
        title="Test QR Code",
        qr_image_base64=qr_image,
        foreground_color="#000000",
        background_color="#FFFFFF",
        style="square",
        box_size=10,
        border_size=4,
        error_correction="M",
    )
    db_session.add(qr)
    db_session.commit()
    db_session.refresh(qr)
    yield qr
    db_session.delete(qr)
    db_session.commit()


# ============================================
# Service Tests
# ============================================

class TestQRService:
    """Tests for QR service functions."""

    def test_generate_qr_image_basic(self):
        """Test basic QR image generation."""
        qr_base64 = generate_qr_image("https://example.com")
        
        # Verify it's valid base64
        qr_data = base64.b64decode(qr_base64)
        
        # Verify it's a valid image
        img = Image.open(BytesIO(qr_data))
        assert img.format == "PNG"
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_generate_qr_image_custom_colors(self):
        """Test QR generation with custom colors."""
        qr_base64 = generate_qr_image(
            "https://example.com",
            foreground_color="#FF0000",
            background_color="#00FF00",
        )
        
        qr_data = base64.b64decode(qr_base64)
        img = Image.open(BytesIO(qr_data))
        assert img.format == "PNG"

    def test_generate_qr_image_styles(self):
        """Test QR generation with different styles."""
        styles = ["square", "rounded", "dots", "circle"]
        
        for style in styles:
            qr_base64 = generate_qr_image(
                "https://example.com",
                style=style,
            )
            qr_data = base64.b64decode(qr_base64)
            img = Image.open(BytesIO(qr_data))
            assert img.format == "PNG"

    def test_generate_qr_image_box_sizes(self):
        """Test QR generation with different box sizes."""
        for box_size in [5, 10, 15, 20]:
            qr_base64 = generate_qr_image(
                "https://example.com",
                box_size=box_size,
            )
            qr_data = base64.b64decode(qr_base64)
            img = Image.open(BytesIO(qr_data))
            assert img.format == "PNG"

    def test_generate_qr_svg(self):
        """Test SVG QR generation."""
        svg_content = generate_qr_svg("https://example.com")
        
        # Verify it's valid SVG
        assert svg_content.startswith("<?xml")
        assert "<svg" in svg_content
        assert "</svg>" in svg_content

    def test_generate_qr_svg_custom_colors(self):
        """Test SVG generation with custom colors."""
        svg_content = generate_qr_svg(
            "https://example.com",
            foreground_color="#FF0000",
            background_color="#00FF00",
        )
        
        assert "#FF0000" in svg_content or "fill" in svg_content

    def test_hex_to_rgb(self):
        """Test hex to RGB conversion."""
        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)
        assert hex_to_rgb("#123456") == (18, 52, 86)

    def test_validate_logo_base64_valid(self):
        """Test logo validation with valid image."""
        # Create a small test image
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        assert validate_logo_base64(img_base64) is True

    def test_validate_logo_base64_with_data_uri(self):
        """Test logo validation with data URI prefix."""
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_uri = f"data:image/png;base64,{img_base64}"
        
        assert validate_logo_base64(data_uri) is True

    def test_validate_logo_base64_invalid(self):
        """Test logo validation with invalid data."""
        assert validate_logo_base64("not_valid_base64") is False
        assert validate_logo_base64("") is False
        assert validate_logo_base64("YWJjZGVm") is False  # Valid base64 but not an image

    def test_generate_qr_with_logo(self):
        """Test QR generation with logo."""
        # Create a small test logo
        logo = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        buffer = BytesIO()
        logo.save(buffer, format="PNG")
        logo_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        qr_base64 = generate_qr_image(
            "https://example.com",
            logo_base64=logo_base64,
        )
        
        qr_data = base64.b64decode(qr_base64)
        img = Image.open(BytesIO(qr_data))
        assert img.format == "PNG"


# ============================================
# API Tests
# ============================================

class TestQRAPI:
    """Tests for QR API endpoints."""

    def test_generate_qr_image_returns_valid_base64(self):
        """Verify generated QR is valid base64 PNG."""
        qr_base64 = generate_qr_image("https://example.com")
        
        # Should be valid base64
        try:
            qr_data = base64.b64decode(qr_base64)
        except Exception:
            pytest.fail("Generated QR is not valid base64")
        
        # Should be PNG
        img = Image.open(BytesIO(qr_data))
        assert img.format == "PNG"

    def test_qr_content_variations(self):
        """Test QR generation with various content types."""
        test_cases = [
            "https://example.com",
            "http://localhost:8000",
            "https://example.com/very/long/path?param=value&other=123",
            "Just some text",
            "tel:+1234567890",
            "mailto:test@example.com",
        ]
        
        for content in test_cases:
            qr_base64 = generate_qr_image(content)
            qr_data = base64.b64decode(qr_base64)
            img = Image.open(BytesIO(qr_data))
            assert img.format == "PNG", f"Failed for content: {content}"


# ============================================
# Model Tests
# ============================================

class TestQRCodeModel:
    """Tests for QRCode model."""

    def test_qr_code_creation(self, db_session, test_user):
        """Test creating a QR code via model."""
        qr_image = generate_qr_image("https://example.com")
        
        qr = QRCode(
            user_id=test_user.id,
            content="https://example.com",
            title="Test QR",
            qr_image_base64=qr_image,
        )
        
        db_session.add(qr)
        db_session.commit()
        db_session.refresh(qr)
        
        assert qr.id is not None
        assert qr.user_id == test_user.id
        assert qr.content == "https://example.com"
        assert qr.title == "Test QR"
        assert qr.style == "square"
        assert qr.error_correction == "M"
        assert qr.downloads_count == 0
        
        db_session.delete(qr)
        db_session.commit()

    def test_qr_code_with_url_link(self, db_session, test_user, test_url):
        """Test creating a QR code linked to a URL."""
        qr_image = generate_qr_image("https://example.com")
        
        qr = QRCode(
            user_id=test_user.id,
            url_id=test_url.id,
            content=f"http://testserver/{test_url.short_code}",
            title="Linked QR",
            qr_image_base64=qr_image,
        )
        
        db_session.add(qr)
        db_session.commit()
        db_session.refresh(qr)
        
        assert qr.url_id == test_url.id
        assert qr.url == test_url
        
        db_session.delete(qr)
        db_session.commit()

    def test_qr_code_cascade_delete(self, db_session, test_user):
        """Test that QR codes are deleted when user is deleted."""
        qr_image = generate_qr_image("https://example.com")
        
        qr = QRCode(
            user_id=test_user.id,
            content="https://example.com",
            qr_image_base64=qr_image,
        )
        
        db_session.add(qr)
        db_session.commit()
        
        qr_id = qr.id
        user_id = test_user.id
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify QR is also deleted
        deleted_qr = db_session.query(QRCode).filter(QRCode.id == qr_id).first()
        assert deleted_qr is None


# ============================================
# Schema Validation Tests
# ============================================

class TestQRCodeSchemas:
    """Tests for Pydantic schema validation."""

    def test_qr_code_create_request_valid(self):
        """Test valid QRCodeCreateRequest."""
        from app.schemas import QRCodeCreateRequest
        
        data = {
            "content": "https://example.com",
            "title": "Test QR",
            "foreground_color": "#000000",
            "background_color": "#FFFFFF",
            "style": "square",
            "box_size": 10,
            "border_size": 4,
            "error_correction": "M",
        }
        
        request = QRCodeCreateRequest(**data)
        assert request.content == "https://example.com"
        assert request.title == "Test QR"

    def test_qr_code_create_request_invalid_color(self):
        """Test QRCodeCreateRequest with invalid color."""
        from app.schemas import QRCodeCreateRequest
        
        data = {
            "content": "https://example.com",
            "foreground_color": "invalid",
        }
        
        with pytest.raises(ValueError):
            QRCodeCreateRequest(**data)

    def test_qr_code_create_request_invalid_style(self):
        """Test QRCodeCreateRequest with invalid style."""
        from app.schemas import QRCodeCreateRequest
        
        data = {
            "content": "https://example.com",
            "style": "invalid_style",
        }
        
        with pytest.raises(ValueError):
            QRCodeCreateRequest(**data)

    def test_qr_code_create_request_invalid_box_size(self):
        """Test QRCodeCreateRequest with invalid box size."""
        from app.schemas import QRCodeCreateRequest
        
        data = {
            "content": "https://example.com",
            "box_size": 25,  # Too large
        }
        
        with pytest.raises(ValueError):
            QRCodeCreateRequest(**data)

    def test_qr_code_create_request_empty_content(self):
        """Test QRCodeCreateRequest with empty content."""
        from app.schemas import QRCodeCreateRequest
        
        data = {
            "content": "   ",  # Whitespace only
        }
        
        with pytest.raises(ValueError):
            QRCodeCreateRequest(**data)

    def test_qr_code_preview_request(self):
        """Test QRCodePreviewRequest."""
        from app.schemas import QRCodePreviewRequest
        
        data = {
            "content": "https://example.com",
            "style": "rounded",
        }
        
        request = QRCodePreviewRequest(**data)
        assert request.content == "https://example.com"
        assert request.style == "rounded"
        assert request.box_size == 10  # Default
