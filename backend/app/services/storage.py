import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from app.core.config import settings
import uuid
from pathlib import Path
from typing import BinaryIO, Optional


class StorageService:
    """
    Cloudflare R2 storage service using S3-compatible API.

    Falls back to local filesystem storage when R2 credentials are not configured.
    """

    def __init__(self):
        self._client = None
        self._bucket = settings.r2_bucket_name
        self._use_r2 = bool(
            settings.r2_endpoint_url
            and settings.r2_access_key_id
            and settings.r2_secret_access_key
        )
        self._local_storage_path = Path("uploads")

        if self._use_r2:
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
        else:
            # Create local storage directory
            self._local_storage_path.mkdir(parents=True, exist_ok=True)

    @property
    def is_cloud_storage(self) -> bool:
        """Check if using cloud storage (R2)."""
        return self._use_r2

    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename preserving extension."""
        ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "jpg"
        return f"{uuid.uuid4()}.{ext}"

    def upload_photo(
        self,
        file: BinaryIO,
        tenant_id: str,
        report_id: str,
        response_id: str,
        original_filename: str = "photo.jpg",
        content_type: str = "image/jpeg",
    ) -> tuple[str, str]:
        """
        Upload a photo file directly.

        Args:
            file: File-like object with photo data
            tenant_id: Tenant UUID
            report_id: Report UUID
            response_id: Checklist response UUID
            original_filename: Original filename for extension detection
            content_type: MIME type of the file

        Returns:
            Tuple of (url, storage_path)
        """
        filename = self._generate_filename(original_filename)
        path = f"{tenant_id}/reports/{report_id}/{response_id}/{filename}"

        if self._use_r2:
            return self._upload_to_r2(file, path, content_type)
        else:
            return self._upload_to_local(file, path)

    def _upload_to_r2(
        self, file: BinaryIO, path: str, content_type: str
    ) -> tuple[str, str]:
        """Upload file to Cloudflare R2."""
        try:
            self._client.upload_fileobj(
                file,
                self._bucket,
                path,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "public, max-age=31536000",
                },
            )
            # Build public URL
            url = f"{settings.r2_public_url}/{path}"
            return url, path
        except ClientError as e:
            raise StorageError(f"Failed to upload to R2: {e}")

    def _upload_to_local(self, file: BinaryIO, path: str) -> tuple[str, str]:
        """Upload file to local filesystem."""
        full_path = self._local_storage_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            while chunk := file.read(8192):
                f.write(chunk)

        # Return URL that can be served by the app
        url = f"/uploads/{path}"
        return url, path

    def generate_upload_url(
        self,
        tenant_id: str,
        filename: str,
        content_type: str = "image/jpeg",
        expires_in: int = 3600,
    ) -> tuple[str, str]:
        """Generate presigned URL for upload. Returns (url, object_key)."""
        if not self._use_r2:
            # Local storage doesn't support presigned URLs
            return "", ""

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
        if not self._use_r2:
            # Local storage uses direct URL
            return f"/uploads/{object_key}"

        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )

    def delete_object(self, object_key: str) -> bool:
        """Delete an object from storage. Returns True if deleted."""
        if self._use_r2:
            try:
                self._client.delete_object(
                    Bucket=self._bucket,
                    Key=object_key,
                )
                return True
            except ClientError:
                return False
        else:
            # Local storage
            full_path = self._local_storage_path / object_key
            try:
                full_path.unlink()
                return True
            except FileNotFoundError:
                return False

    def list_objects(
        self,
        prefix: str,
        max_keys: int = 100,
    ) -> list[dict]:
        """List objects with given prefix. Returns list of {key, size, last_modified}."""
        if not self._use_r2:
            # Local storage listing
            results = []
            local_prefix = self._local_storage_path / prefix
            if local_prefix.exists():
                for f in local_prefix.rglob("*"):
                    if f.is_file():
                        stat = f.stat()
                        results.append({
                            "key": str(f.relative_to(self._local_storage_path)),
                            "size": stat.st_size,
                            "last_modified": stat.st_mtime,
                        })
            return results[:max_keys]

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


class StorageError(Exception):
    """Storage operation error."""
    pass


# Singleton instance (lazy)
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
