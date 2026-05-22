try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
except Exception:  # pragma: no cover - allow tests to run without cloudinary installed
    cloudinary = None

from config.settings import settings
import uuid
from datetime import datetime

if cloudinary is not None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
else:
    # Provide a lightweight stub so tests and environments without cloudinary can import
    class _StubUploader:
        def upload(self, *args, **kwargs):
            raise RuntimeError("cloudinary not installed")

    class _StubAPI:
        def delete_resources(self, *args, **kwargs):
            return {}

        def resources_by_tag(self, *args, **kwargs):
            return {"resources": []}

    class _StubCloudinaryImage:
        def __init__(self, public_id):
            self.public_id = public_id

        def build_url(self, **kwargs):
            # simple generated URL for tests
            size = kwargs.get("width") or kwargs.get("height") or "auto"
            return f"https://res.cloudinary.com/demo/{self.public_id}/w_{size}"

    class _StubCloudinary:
        uploader = _StubUploader()
        api = _StubAPI()
        CloudinaryImage = _StubCloudinaryImage

    cloudinary = _StubCloudinary()


class CloudinaryService:

    async def upload_incident_media(
        self,
        file_bytes: bytes,
        filename: str,
        incident_id: str,
        media_type: str = "image"  # "image" | "video"
    ) -> dict:
        """
        Upload a citizen-submitted photo or video to Cloudinary.
        Returns: { public_id, secure_url, resource_type, format, created_at }
        """
        folder = f"aapda-mitra/incidents/{incident_id}"
        public_id = f"{folder}/{uuid.uuid4().hex}"

        result = cloudinary.uploader.upload(
            file_bytes,
            public_id=public_id,
            resource_type=media_type,       # "image" or "video"
            folder=folder,
            tags=["aapda-mitra", incident_id],
            context=f"incident_id={incident_id}|uploaded_at={datetime.utcnow().isoformat()}",
            overwrite=False,
            # Auto-moderate uploaded content
            moderation="manual" if media_type == "video" else None,
        )
        return {
            "public_id": result["public_id"],
            "secure_url": result["secure_url"],
            "resource_type": result.get("resource_type", "image"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at"),
        }

    async def upload_multiple(
        self,
        files: list[tuple[bytes, str]],  # list of (file_bytes, filename)
        incident_id: str
    ) -> list[dict]:
        """Upload multiple files for one incident. Returns list of upload results."""
        results = []
        for file_bytes, filename in files:
            ext = filename.rsplit(".", 1)[-1].lower()
            media_type = "video" if ext in ["mp4", "mov", "avi", "webm"] else "image"
            result = await self.upload_incident_media(
                file_bytes, filename, incident_id, media_type
            )
            results.append(result)
        return results

    def get_optimized_url(
        self,
        public_id: str,
        width: int = 800,
        quality: str = "auto"
    ) -> str:
        """
        Return a transformed/optimized Cloudinary URL.
        Use for displaying thumbnails on dashboard.
        """
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=width,
            crop="scale",
            quality=quality,
            fetch_format="auto",
            secure=True
        )

    def get_thumbnail_url(self, public_id: str, size: int = 200) -> str:
        """Return a square thumbnail URL for incident media grid."""
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=size,
            height=size,
            crop="fill",
            gravity="auto",
            quality="auto",
            fetch_format="auto",
            secure=True
        )

    async def delete_incident_media(self, public_ids: list[str]) -> dict:
        """Delete all media for an incident (cleanup after 90 days or on fake detection)."""
        if not public_ids:
            return {}
        result = cloudinary.api.delete_resources(
            public_ids,
            resource_type="image"
        )
        # Also delete videos if any
        cloudinary.api.delete_resources(
            public_ids,
            resource_type="video"
        )
        return result

    async def get_incident_media(self, incident_id: str) -> list[dict]:
        """List all uploaded media for a specific incident using tags."""
        result = cloudinary.api.resources_by_tag(
            incident_id,
            resource_type="image",
            max_results=20
        )
        images = result.get("resources", [])

        video_result = cloudinary.api.resources_by_tag(
            incident_id,
            resource_type="video",
            max_results=10
        )
        videos = video_result.get("resources", [])

        return images + videos


# Singleton
cloudinary_service = CloudinaryService()
