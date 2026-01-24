import boto3
from botocore.config import Config as BotoConfig
from app.core.config import settings
import uuid
from typing import Optional


class StorageService:
    """Cloudflare R2 storage service using S3-compatible API."""

    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
            config=BotoConfig(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )
        self._bucket = settings.r2_bucket_name

    def generate_upload_url(
        self,
        tenant_id: str,
        filename: str,
        content_type: str = "image/jpeg",
        expires_in: int = 3600,
    ) -> tuple[str, str]:
        """Generate presigned URL for upload. Returns (url, object_key)."""
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
        object_key = f"{tenant_id}/photos/{uuid.uuid4()}.{ext}"

        url = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return url, object_key

    def generate_download_url(
        self,
        object_key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate presigned URL for download."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )

    def delete_object(self, object_key: str) -> None:
        """Delete an object from storage."""
        self._client.delete_object(
            Bucket=self._bucket,
            Key=object_key,
        )

    def list_objects(
        self,
        prefix: str,
        max_keys: int = 100,
    ) -> list[dict]:
        """List objects with given prefix. Returns list of {key, size, last_modified}."""
        response = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )
        contents = response.get("Contents", [])
        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in contents
        ]


# Singleton instance (lazy)
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
