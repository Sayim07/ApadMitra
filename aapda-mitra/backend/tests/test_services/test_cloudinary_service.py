import pytest
from unittest.mock import patch
from services.cloudinary_service import cloudinary_service


mock_result = {
    "public_id": "aapda-mitra/incidents/123/abc",
    "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/aapda-mitra/incidents/123/abc.jpg",
    "resource_type": "image",
    "format": "jpg",
    "bytes": 204800,
    "created_at": "2026-05-09T14:30:00Z"
}


@pytest.mark.asyncio
async def test_upload_image_returns_secure_url():
    with patch("services.cloudinary_service.cloudinary.uploader.upload", return_value=mock_result):
        result = await cloudinary_service.upload_incident_media(
            b"fake_image_bytes", "flood.jpg", "incident-123"
        )
    assert result["secure_url"].startswith("https://res.cloudinary.com")
    assert result["resource_type"] == "image"


@pytest.mark.asyncio
async def test_upload_video_sets_resource_type_video():
    with patch("services.cloudinary_service.cloudinary.uploader.upload", return_value={**mock_result, "resource_type": "video"}):
        result = await cloudinary_service.upload_incident_media(
            b"fake_video_bytes", "flood_video.mp4", "incident-123", media_type="video"
        )
    assert result["resource_type"] == "video"


def test_thumbnail_url_returns_cloudinary_url():
    url = cloudinary_service.get_thumbnail_url("aapda-mitra/incidents/123/abc")
    assert "cloudinary.com" in url
    assert "c_fill" in url or "w_200" in url
