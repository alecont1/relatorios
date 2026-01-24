import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_generate_upload_url(mock_settings, mock_boto_client):
    """Test presigned upload URL generation with correct parameters."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.generate_presigned_url.return_value = "https://presigned-upload-url"

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # Generate upload URL
    url, key = service.generate_upload_url("tenant-123", "photo.jpg")

    # Verify URL returned
    assert url == "https://presigned-upload-url"

    # Verify object key format
    assert "tenant-123/photos/" in key
    assert key.endswith(".jpg")

    # Verify presigned URL was called correctly
    mock_client.generate_presigned_url.assert_called_once()
    call_args = mock_client.generate_presigned_url.call_args
    assert call_args[0][0] == "put_object"
    assert call_args[1]["Params"]["Bucket"] == "test-bucket"
    assert call_args[1]["Params"]["Key"] == key
    assert call_args[1]["Params"]["ContentType"] == "image/jpeg"
    assert call_args[1]["ExpiresIn"] == 3600


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_generate_download_url(mock_settings, mock_boto_client):
    """Test presigned download URL generation."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.generate_presigned_url.return_value = "https://presigned-download-url"

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # Generate download URL
    url = service.generate_download_url("tenant-123/photos/test.jpg")

    # Verify URL returned
    assert url == "https://presigned-download-url"

    # Verify get_object was used
    mock_client.generate_presigned_url.assert_called_once()
    call_args = mock_client.generate_presigned_url.call_args
    assert call_args[0][0] == "get_object"
    assert call_args[1]["Params"]["Bucket"] == "test-bucket"
    assert call_args[1]["Params"]["Key"] == "tenant-123/photos/test.jpg"
    assert call_args[1]["ExpiresIn"] == 3600


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_delete_object(mock_settings, mock_boto_client):
    """Test object deletion with correct bucket and key."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # Delete object
    service.delete_object("tenant-123/photos/test.jpg")

    # Verify delete_object was called correctly
    mock_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="tenant-123/photos/test.jpg"
    )


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_list_objects(mock_settings, mock_boto_client):
    """Test list objects with prefix and response parsing."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "tenant-123/photos/photo1.jpg",
                "Size": 1024,
                "LastModified": datetime(2024, 1, 15, 10, 30, 0)
            },
            {
                "Key": "tenant-123/photos/photo2.jpg",
                "Size": 2048,
                "LastModified": datetime(2024, 1, 15, 11, 45, 0)
            }
        ]
    }

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # List objects
    objects = service.list_objects("tenant-123/photos/", max_keys=50)

    # Verify list_objects_v2 was called correctly
    mock_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket",
        Prefix="tenant-123/photos/",
        MaxKeys=50
    )

    # Verify response parsing
    assert len(objects) == 2
    assert objects[0]["key"] == "tenant-123/photos/photo1.jpg"
    assert objects[0]["size"] == 1024
    assert objects[0]["last_modified"] == "2024-01-15T10:30:00"
    assert objects[1]["key"] == "tenant-123/photos/photo2.jpg"
    assert objects[1]["size"] == 2048
    assert objects[1]["last_modified"] == "2024-01-15T11:45:00"


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_upload_url_uses_content_type(mock_settings, mock_boto_client):
    """Test that ContentType parameter is passed through correctly."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.generate_presigned_url.return_value = "https://presigned-url"

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # Generate upload URL with custom content type
    url, key = service.generate_upload_url("tenant-123", "photo.png", content_type="image/png")

    # Verify ContentType was passed
    call_args = mock_client.generate_presigned_url.call_args
    assert call_args[1]["Params"]["ContentType"] == "image/png"


@patch("app.services.storage.boto3.client")
@patch("app.services.storage.settings")
def test_object_key_format(mock_settings, mock_boto_client):
    """Test that object keys follow {tenant_id}/photos/{uuid}.{ext} pattern."""
    # Mock settings
    mock_settings.r2_endpoint_url = "https://test.r2.cloudflarestorage.com"
    mock_settings.r2_access_key_id = "test-key"
    mock_settings.r2_secret_access_key = "test-secret"
    mock_settings.r2_bucket_name = "test-bucket"

    # Mock boto3 client
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.generate_presigned_url.return_value = "https://presigned-url"

    # Import and create service
    from app.services.storage import StorageService
    service = StorageService()

    # Test with different filenames and extensions
    test_cases = [
        ("tenant-abc", "image.jpg", ".jpg"),
        ("tenant-xyz", "document.pdf", ".pdf"),
        ("tenant-123", "photo.png", ".png"),
        ("tenant-456", "noextension", ".jpg"),  # Default to .jpg
    ]

    for tenant_id, filename, expected_ext in test_cases:
        url, key = service.generate_upload_url(tenant_id, filename)

        # Verify format: {tenant_id}/photos/{uuid}.{ext}
        assert key.startswith(f"{tenant_id}/photos/")
        assert key.endswith(expected_ext)

        # Verify UUID is in the middle (36 chars + 1 for dot + ext length)
        parts = key.split("/")
        assert len(parts) == 3
        assert parts[0] == tenant_id
        assert parts[1] == "photos"

        # UUID part should be valid format (with extension)
        uuid_part = parts[2]
        assert len(uuid_part.split(".")) == 2  # Should have exactly one dot
