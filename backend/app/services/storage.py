import boto3
import uuid
import os
from datetime import datetime, timedelta
from typing import BinaryIO, Optional, Tuple, List
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError

from app.core.config import settings

class StorageService:
    """
    Service for handling secure file storage operations.
    """
    
    def __init__(self):
        """
        Initialize the storage client connection.
        """
        self.s3 = None
        self.bucket_name = settings.STORAGE_BUCKET_NAME
        
        if all([
            settings.STORAGE_ACCESS_KEY,
            settings.STORAGE_SECRET_KEY,
            settings.STORAGE_REGION,
            settings.STORAGE_ENDPOINT,
            settings.STORAGE_BUCKET_NAME
        ]):
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=settings.STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.STORAGE_SECRET_KEY,
                region_name=settings.STORAGE_REGION,
                endpoint_url=settings.STORAGE_ENDPOINT
            )
    
    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "documents",
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Tuple[str, str]:
        """
        Upload a file to secure storage.
        
        Args:
            file: The file to upload
            folder: The folder to store the file in
            user_id: The ID of the user uploading the file
            metadata: Additional metadata to store with the file
            
        Returns:
            Tuple containing the file key and full URL
        """
        if not self.s3:
            raise HTTPException(
                status_code=500, 
                detail="Storage service not configured properly"
            )
        
        # Create a unique file name
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_uuid = str(uuid.uuid4())
        
        if user_id:
            key = f"{folder}/{user_id}/{timestamp}_{file_uuid}{file_extension}"
        else:
            key = f"{folder}/{timestamp}_{file_uuid}{file_extension}"
        
        # Prepare metadata
        s3_metadata = {}
        if metadata:
            # S3 metadata keys must be lowercase and cannot contain special characters
            s3_metadata = {k.lower().replace("-", "_"): str(v) for k, v in metadata.items()}
        
        # Add some standard metadata
        s3_metadata.update({
            "original_filename": file.filename or "unknown",
            "content_type": file.content_type or "application/octet-stream",
            "upload_timestamp": timestamp
        })
        
        try:
            # Upload to S3
            await self._upload_fileobj(
                file.file, 
                key, 
                file.content_type, 
                s3_metadata
            )
            
            # Generate the URL
            url = f"{settings.STORAGE_ENDPOINT}/{self.bucket_name}/{key}"
            
            return key, url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {str(e)}"
            )
    
    async def _upload_fileobj(
        self, 
        file_obj: BinaryIO, 
        key: str, 
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Upload a file-like object to S3.
        """
        extra_args = {}
        
        if content_type:
            extra_args["ContentType"] = content_type
            
        if metadata:
            extra_args["Metadata"] = metadata
        
        # Add encryption - server-side encryption
        extra_args["ServerSideEncryption"] = "AES256"
        
        try:
            # Reset file pointer to beginning
            file_obj.seek(0)
            
            # Upload to S3
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"S3 upload error: {str(e)}"
            )
    
    async def generate_presigned_url(
        self, 
        key: str, 
        expires_in: int = 3600,
        download_name: Optional[str] = None
    ) -> str:
        """
        Generate a presigned URL for temporary access to a file.
        
        Args:
            key: The S3 key of the file
            expires_in: How long the URL should be valid, in seconds
            download_name: Optional custom filename for download
            
        Returns:
            Presigned URL for accessing the file
        """
        if not self.s3:
            raise HTTPException(
                status_code=500, 
                detail="Storage service not configured properly"
            )
            
        try:
            extra_args = {}
            if download_name:
                extra_args["ResponseContentDisposition"] = f'attachment; filename="{download_name}"'
                
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    **extra_args
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating presigned URL: {str(e)}"
            )
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            key: The S3 key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3:
            raise HTTPException(
                status_code=500, 
                detail="Storage service not configured properly"
            )
            
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file: {str(e)}"
            )
    
    async def list_user_files(
        self, 
        user_id: str,
        folder: str = "documents",
        prefix: Optional[str] = None
    ) -> List[dict]:
        """
        List all files for a specific user.
        
        Args:
            user_id: The ID of the user
            folder: The folder to list files from
            prefix: Additional prefix filter
            
        Returns:
            List of file objects
        """
        if not self.s3:
            raise HTTPException(
                status_code=500, 
                detail="Storage service not configured properly"
            )
            
        prefix_path = f"{folder}/{user_id}/"
        if prefix:
            prefix_path += prefix
            
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix_path
            )
            
            files = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    # Get file metadata
                    obj_response = self.s3.head_object(
                        Bucket=self.bucket_name,
                        Key=obj["Key"]
                    )
                    
                    metadata = obj_response.get("Metadata", {})
                    
                    # Create file object
                    file_obj = {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "original_filename": metadata.get("original_filename", "unknown"),
                        "content_type": metadata.get("content_type", "application/octet-stream"),
                        "upload_timestamp": metadata.get("upload_timestamp")
                    }
                    files.append(file_obj)
                    
            return files
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing files: {str(e)}"
            )