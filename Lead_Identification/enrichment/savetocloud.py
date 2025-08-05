import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
from typing import Dict, List, Optional


def delete_all_files_in_folder(folder_path):
    """
    Deletes all files in the specified folder (not including subfolders).
    
    Parameters:
    - folder_path (str): The path to the folder where files should be deleted.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")



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






# Example usage
def saveContentToCloudinary():
    # Method 1: Direct credentials
    try:
        input_dir = "crawled_data"
        urls = upload_txt_files_to_cloudinary(
            folder_path=Path(input_dir).resolve(),
            cloud_name="daop9owk3",
            api_key="663575178492181", 
            api_secret="PKtRhurQxgzUgMT8vnMKnKDtQdA",
            folder_name="documents"  # Optional: organize in a folder
        )
        
        print("\nUploaded URLs:")
        for filename, url in urls.items():
            print(f"{filename}: {url}")

        print("lretour kima howa")
        print(urls)

        delete_all_files_in_folder(input_dir)

        return urls
            
    except Exception as e:
        print(f"Upload failed: {e}")
    
