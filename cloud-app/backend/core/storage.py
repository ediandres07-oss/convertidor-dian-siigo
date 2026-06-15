import logging
import os
from typing import BinaryIO, Optional
from abc import ABC, abstractmethod

try:
    import boto3
    from botocore.exceptions import ClientError as S3ClientError
except ImportError:
    boto3 = None
    S3ClientError = None

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None

try:
    from google.cloud import storage as gcs
except ImportError:
    gcs = None

from backend.config import settings

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def upload_file(self, file_path: str, file_data: BinaryIO) -> str:
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        pass

    @abstractmethod
    async def list_files(self, prefix: str = "") -> list[str]:
        pass

    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        pass


class S3Storage(StorageBackend):
    """AWS S3 storage backend."""

    def __init__(self):
        if not boto3:
            raise ImportError("boto3 is required for S3 storage")

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL if "localhost" in settings.S3_ENDPOINT_URL else None,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME must be set")

    async def upload_file(self, file_path: str, file_data: BinaryIO) -> str:
        try:
            key = f"{settings.S3_FOLDER}/{file_path}"
            self.s3_client.upload_fileobj(file_data, self.bucket_name, key)
            logger.info(f"File uploaded to S3: {key}")
            return key
        except S3ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise

    async def download_file(self, file_path: str) -> bytes:
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"{settings.S3_FOLDER}/{file_path}"
            )
            return response["Body"].read()
        except S3ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=f"{settings.S3_FOLDER}/{file_path}"
            )
            logger.info(f"File deleted from S3: {file_path}")
            return True
        except S3ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{settings.S3_FOLDER}/{prefix}"
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except S3ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            return []

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": f"{settings.S3_FOLDER}/{file_path}"
                },
                ExpiresIn=expires_in,
            )
            return url
        except S3ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise


class AzureStorage(StorageBackend):
    """Azure Blob Storage backend."""

    def __init__(self):
        if not BlobServiceClient:
            raise ImportError("azure-storage-blob is required for Azure storage")

        self.client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_CONTAINER_NAME
        if not self.container_name:
            raise ValueError("AZURE_CONTAINER_NAME must be set")

    async def upload_file(self, file_path: str, file_data: BinaryIO) -> str:
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(file_path)
            blob_client.upload_blob(file_data, overwrite=True)
            logger.info(f"File uploaded to Azure: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error uploading file to Azure: {e}")
            raise

    async def download_file(self, file_path: str) -> bytes:
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(file_path)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading file from Azure: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(file_path)
            blob_client.delete_blob()
            logger.info(f"File deleted from Azure: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from Azure: {e}")
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        try:
            container_client = self.client.get_container_client(self.container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Error listing files from Azure: {e}")
            return []

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        container_client = self.client.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client(file_path)
        return blob_client.url


class GCSStorage(StorageBackend):
    """Google Cloud Storage backend."""

    def __init__(self):
        if not gcs:
            raise ImportError("google-cloud-storage is required for GCS storage")

        self.client = gcs.Client(project=settings.GCP_PROJECT_ID)
        self.bucket = self.client.bucket(settings.GCP_BUCKET_NAME)
        if not settings.GCP_BUCKET_NAME:
            raise ValueError("GCP_BUCKET_NAME must be set")

    async def upload_file(self, file_path: str, file_data: BinaryIO) -> str:
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_file(file_data)
            logger.info(f"File uploaded to GCS: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {e}")
            raise

    async def download_file(self, file_path: str) -> bytes:
        try:
            blob = self.bucket.blob(file_path)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Error downloading file from GCS: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            logger.info(f"File deleted from GCS: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from GCS: {e}")
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        try:
            return [blob.name for blob in self.bucket.list_blobs(prefix=prefix)]
        except Exception as e:
            logger.error(f"Error listing files from GCS: {e}")
            return []

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        blob = self.bucket.blob(file_path)
        url = blob.generate_signed_url(version="v4", expiration=expires_in)
        return url


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    async def upload_file(self, file_path: str, file_data: BinaryIO) -> str:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(file_data.read())
            logger.info(f"File uploaded locally: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error uploading file locally: {e}")
            raise

    async def download_file(self, file_path: str) -> bytes:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            with open(full_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error downloading file locally: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            os.remove(full_path)
            logger.info(f"File deleted locally: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file locally: {e}")
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        try:
            full_path = os.path.join(self.base_dir, prefix)
            files = []
            for root, dirs, filenames in os.walk(full_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), self.base_dir)
                    files.append(rel_path)
            return files
        except Exception as e:
            logger.error(f"Error listing files locally: {e}")
            return []

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        return f"/files/{file_path}"


def get_storage() -> StorageBackend:
    """Factory function to get appropriate storage backend."""
    if settings.S3_BUCKET_NAME and settings.AWS_ACCESS_KEY_ID:
        return S3Storage()
    elif settings.AZURE_STORAGE_CONNECTION_STRING:
        return AzureStorage()
    elif settings.GCP_BUCKET_NAME:
        return GCSStorage()
    else:
        return LocalStorage(settings.UPLOAD_DIR)
