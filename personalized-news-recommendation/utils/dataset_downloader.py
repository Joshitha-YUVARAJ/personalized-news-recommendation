#!/usr/bin/env python3
"""
Dataset downloader for MIND dataset in Azure Container Apps
Downloads the dataset from Azure Files if not present locally
"""

import os
import requests
import tempfile
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_from_azure_files(target_dir="/app/dataset"):
    """
    Download MIND dataset from Azure Files using REST API
    
    Args:
        target_dir (str): Directory to extract dataset to
        
    Returns:
        str: Path to the extracted dataset directory
    """
    dataset_path = os.path.join(target_dir, "MINDsmall_train")
    
    # Check if dataset already exists
    if os.path.exists(os.path.join(dataset_path, "news.tsv")) and \
       os.path.exists(os.path.join(dataset_path, "behaviors.tsv")):
        logger.info(f"Dataset already exists at {dataset_path}")
        return dataset_path
    
    # Get Azure storage credentials from environment
    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    storage_key = os.getenv("AZURE_STORAGE_KEY")
    
    if not storage_account or not storage_key:
        logger.warning("Azure storage credentials not found, using sample dataset")
        return create_sample_fallback(dataset_path)
    
    # Create target directory
    os.makedirs(dataset_path, exist_ok=True)
    
    logger.info(f"Downloading dataset from Azure Files storage account: {storage_account}")
    
    # Azure Files REST API base URL
    base_url = f"https://{storage_account}.file.core.windows.net/dataset/MINDsmall_train"
    
    files_to_download = [
        "news.tsv",
        "behaviors.tsv", 
        "entity_embedding.vec",
        "relation_embedding.vec"
    ]
    
    try:
        from azure.storage.fileshare import ShareFileClient
        
        for filename in files_to_download:
            logger.info(f"Downloading {filename}...")
            
            file_client = ShareFileClient(
                account_url=f"https://{storage_account}.file.core.windows.net",
                share_name="dataset",
                file_path=f"MINDsmall_train/{filename}",
                credential=storage_key
            )
            
            local_file_path = os.path.join(dataset_path, filename)
            with open(local_file_path, "wb") as file_handle:
                data = file_client.download_file()
                data.readinto(file_handle)
            
            logger.info(f"Downloaded {filename} successfully")
        
        logger.info(f"All dataset files downloaded to {dataset_path}")
        return dataset_path
        
    except ImportError:
        logger.warning("Azure storage library not available, using sample dataset")
        return create_sample_fallback(dataset_path)
    except Exception as e:
        logger.error(f"Failed to download from Azure Files: {e}")
        logger.info("Falling back to sample dataset")
        return create_sample_fallback(dataset_path)

def create_sample_fallback(dataset_path):
    """Create sample dataset as fallback"""
    try:
        from utils.dataset_loader import create_sample_dataset
        create_sample_dataset(dataset_path)
        logger.info(f"Sample dataset created at {dataset_path}")
        return dataset_path
    except Exception as e:
        logger.error(f"Failed to create sample dataset: {e}")
        raise

def download_and_extract_dataset(target_dir="/app/dataset"):
    """
    Download MIND dataset from Azure Files or create sample data
    
    Args:
        target_dir (str): Directory to extract dataset to
        
    Returns:
        str: Path to the extracted dataset directory
    """
    return download_from_azure_files(target_dir)

def ensure_dataset_available():
    """
    Ensure dataset is available for the application
    
    Returns:
        str: Path to dataset directory
    """
    # Check environment variable for dataset directory
    dataset_dir = os.getenv("DATASET_DIR", "/app/dataset")
    
    # Try to download/create dataset
    try:
        return download_and_extract_dataset(dataset_dir)
    except Exception as e:
        logger.error(f"Failed to ensure dataset availability: {e}")
        # Fall back to using dataset_loader sample data
        from utils.dataset_loader import ensure_dataset_exists
        return ensure_dataset_exists()

if __name__ == "__main__":
    # CLI usage
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "/app/dataset"
    result = download_and_extract_dataset(target)
    print(f"Dataset available at: {result}")