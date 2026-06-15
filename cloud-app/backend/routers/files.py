import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.session import get_db
from backend.schemas.common import Message
from backend.models.user import User
from backend.core.storage import get_storage
from backend.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_file(filename: str, file_size: int) -> None:
    """Validate file extension and size."""
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB",
        )

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}",
        )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file to cloud storage."""
    try:
        # Read file content
        content = await file.read()

        # Validate file
        validate_file(file.filename, len(content))

        # Generate file path
        file_ext = file.filename.rsplit(".", 1)[-1]
        file_path = f"user-{current_user.id}/{file.filename}"

        # Upload to storage
        storage = get_storage()
        await storage.upload_file(file_path, file.file)

        # Get file URL
        file_url = await storage.get_file_url(file_path)

        logger.info(f"File uploaded: {file_path} by user {current_user.id}")

        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_url": file_url,
            "size": len(content),
            "content_type": file.content_type,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file",
        )


@router.get("/download/{file_path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user),
):
    """Download file from cloud storage."""
    try:
        # Validate file access
        if not file_path.startswith(f"user-{current_user.id}/") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download this file",
            )

        # Download file
        storage = get_storage()
        file_data = await storage.download_file(file_path)

        logger.info(f"File downloaded: {file_path} by user {current_user.id}")

        return FileResponse(
            iter([file_data]),
            filename=file_path.split("/")[-1],
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file",
        )


@router.delete("/{file_path}", response_model=Message)
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user),
):
    """Delete file from cloud storage."""
    try:
        # Validate file access
        if not file_path.startswith(f"user-{current_user.id}/") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file",
            )

        # Delete file
        storage = get_storage()
        success = await storage.delete_file(file_path)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting file",
            )

        logger.info(f"File deleted: {file_path} by user {current_user.id}")
        return Message(message="File deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file",
        )


@router.get("/{file_path}/url")
async def get_file_url(
    file_path: str,
    expires_in: int = 3600,
    current_user: User = Depends(get_current_user),
):
    """Get signed URL for file (valid for expires_in seconds)."""
    try:
        # Validate file access
        if not file_path.startswith(f"user-{current_user.id}/") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file",
            )

        # Get signed URL
        storage = get_storage()
        url = await storage.get_file_url(file_path, expires_in)

        return {
            "url": url,
            "expires_in": expires_in,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating file URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating file URL",
        )


@router.get("")
async def list_user_files(
    current_user: User = Depends(get_current_user),
):
    """List files uploaded by current user."""
    try:
        storage = get_storage()
        prefix = f"user-{current_user.id}/"
        files = await storage.list_files(prefix)

        return {
            "files": files,
            "total": len(files),
        }

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing files",
        )
