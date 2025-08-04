import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
from typing import Dict, List, Optional


def upload_txt_files_to_cloudinary(
    folder_path: str,
    cloud_name: str,
    api_key: str,
    api_secret: str,
    folder_name: Optional[str] = None,
    resource_type: str = "raw"
) -> Dict[str, str]:
    """
    Upload all .txt files from a folder to Cloudinary and return their URLs.
    
    Args:
        folder_path (str): Path to the folder containing .txt files
        cloud_name (str): Cloudinary cloud name
        api_key (str): Cloudinary API key
        api_secret (str): Cloudinary API secret
        folder_name (str, optional): Cloudinary folder name to organize uploads
        resource_type (str): Type of resource ("raw" for text files, "auto" for auto-detection)
    
    Returns:
        Dict[str, str]: Dictionary mapping filename to Cloudinary URL
        
    Raises:
        FileNotFoundError: If the folder path doesn't exist
        Exception: If Cloudinary configuration or upload fails
    """
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    
    # Validate folder path
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    # Find all .txt files
    txt_files = list(folder.glob("*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in {folder_path}")
        return {}
    
    print(f"Found {len(txt_files)} .txt files to upload...")
    
    uploaded_urls = {}
    failed_uploads = []
    
    for txt_file in txt_files:
        try:
            # Prepare upload options
            upload_options = {
                "resource_type": resource_type,
                "use_filename": True,
                "unique_filename": False,
                "overwrite": True
            }
            
            # Add folder if specified
            if folder_name:
                upload_options["folder"] = folder_name
            
            # Upload file
            print(f"Uploading {txt_file.name}...")
            response = cloudinary.uploader.upload(
                str(txt_file),
                **upload_options
            )
            
            # Store the URL
            uploaded_urls[txt_file.name] = response["secure_url"]
            print(f"✓ Successfully uploaded {txt_file.name}")
            
        except Exception as e:
            error_msg = f"Failed to upload {txt_file.name}: {str(e)}"
            print(f"✗ {error_msg}")
            failed_uploads.append(error_msg)
    
    # Summary
    print(f"\nUpload Summary:")
    print(f"Successful uploads: {len(uploaded_urls)}")
    print(f"Failed uploads: {len(failed_uploads)}")
    
    if failed_uploads:
        print("\nFailed uploads:")
        for error in failed_uploads:
            print(f"  - {error}")
    
    return uploaded_urls


def upload_txt_files_with_env(
    folder_path: str,
    folder_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Convenience function that reads Cloudinary credentials from environment variables.
    
    Environment variables required:
    - CLOUDINARY_CLOUD_NAME
    - CLOUDINARY_API_KEY  
    - CLOUDINARY_API_SECRET
    
    Args:
        folder_path (str): Path to the folder containing .txt files
        folder_name (str, optional): Cloudinary folder name to organize uploads
        
    Returns:
        Dict[str, str]: Dictionary mapping filename to Cloudinary URL
    """
    
    # Get credentials from environment variables
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        raise ValueError(
            "Missing Cloudinary credentials. Please set environment variables: "
            "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET"
        )
    
    return upload_txt_files_to_cloudinary(
        folder_path=folder_path,
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        folder_name=folder_name
    )






# Example usage
if __name__ == "__main__":
    # Method 1: Direct credentials
    try:
        output_dir = "crawled_data"
        urls = upload_txt_files_to_cloudinary(
            folder_path=Path(output_dir).resolve(),
            cloud_name="daop9owk3",
            api_key="663575178492181", 
            api_secret="PKtRhurQxgzUgMT8vnMKnKDtQdA",
            folder_name="documents"  # Optional: organize in a folder
        )
        
        print("\nUploaded URLs:")
        for filename, url in urls.items():
            print(f"{filename}: {url}")
            
    except Exception as e:
        print(f"Upload failed: {e}")
    
    # Method 2: Using environment variables
    # First set your environment variables:
    # export CLOUDINARY_CLOUD_NAME="your_cloud_name"
    # export CLOUDINARY_API_KEY="your_api_key"
    # export CLOUDINARY_API_SECRET="your_api_secret"
    
    # try:
    #     urls = upload_txt_files_with_env(
    #         folder_path="./text_files",
    #         folder_name="documents"
    #     )
        
    #     print("\nUploaded URLs:")
    #     for filename, url in urls.items():
    #         print(f"{filename}: {url}")
            
    # except Exception as e:
    #     print(f"Upload failed: {e}")