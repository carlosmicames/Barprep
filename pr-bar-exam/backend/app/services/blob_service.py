"""
Vercel Blob Storage service for handling file uploads.
"""
import os
from typing import BinaryIO, Dict
import httpx
from app.core.config import settings


class BlobService:
    """Service for interacting with Vercel Blob Storage."""

    def __init__(self):
        self.blob_read_write_token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not self.blob_read_write_token:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable not set")

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str = "application/pdf"
    ) -> Dict[str, str]:
        """
        Upload a file to Vercel Blob Storage.

        Args:
            file: File-like object to upload
            filename: Name for the file in storage
            content_type: MIME type of the file

        Returns:
            Dict containing url, downloadUrl, and pathname
        """
        async with httpx.AsyncClient() as client:
            # Read file content
            file_content = file.read()

            # Upload to Vercel Blob
            response = await client.put(
                f"https://blob.vercel-storage.com/{filename}",
                content=file_content,
                headers={
                    "authorization": f"Bearer {self.blob_read_write_token}",
                    "x-content-type": content_type,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Failed to upload to Blob Storage: {response.text}")

            return response.json()

    async def delete_file(self, url: str) -> bool:
        """
        Delete a file from Vercel Blob Storage.

        Args:
            url: The URL of the file to delete

        Returns:
            True if successful
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers={
                    "authorization": f"Bearer {self.blob_read_write_token}",
                },
            )

            return response.status_code == 200

    async def get_file_url(self, pathname: str) -> str:
        """
        Get the download URL for a file.

        Args:
            pathname: Path of the file in Blob Storage

        Returns:
            Download URL
        """
        return f"https://blob.vercel-storage.com/{pathname}"


# Global blob service instance
blob_service = BlobService() if os.getenv("BLOB_READ_WRITE_TOKEN") else None
