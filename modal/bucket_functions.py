import supabase
import os 
from dotenv import load_dotenv
import tempfile
from supabase import create_client, Client

load_dotenv()

supabase = supabase.create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def connect_to_supabase():
    """Establish connection to Supabase client"""
    load_dotenv()
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase


client=connect_to_supabase()
def get_relavant_bucket(bucket_name: str="rawdata"):
    """Get Supabase storage bucket by name"""
    return supabase.storage.from_(bucket_name)

def upload_to_bucket(bucket_name: str, file_base_path: str, content, file_name: str) -> bool:
    """
    Upload content to a Supabase storage bucket
    
    Args:
        bucket_name: Name of the bucket to upload to
        file_base_path: Base path within the bucket
        content: Either a file path (str) or the content to upload (str/bytes)
        file_name: Name of the file to be stored
        
    Returns:
        bool: True if upload succeeded, False if it failed
    """
    bucket = get_relavant_bucket(bucket_name)
    print(bucket)
    file_path = file_base_path + '/' + file_name
    
    try:
        if isinstance(content, str) and os.path.isfile(content):
            print("running case 1")
            with open(content, 'rb') as f:
                bucket.upload(path=file_path, file=f, 
                             file_options={"content-type": "text/markdown"})
            return True
            
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            if isinstance(content, str):
                content = content.encode('utf-8')
            print("running case 2")
            temp_file.write(content)
            temp_file.flush()
        
        with open(temp_file.name, 'rb') as f:
            bucket.upload(path=file_path, file=f,
                         file_options={"content-type": "text/markdown"})
        
        return True
            
    except Exception as e:
        print(f"Error uploading to bucket: {e}")
        return False
        
    finally:
        # Clean up temp file if it exists
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
            except:
                pass

def get_markdown_from_bucket(bucket_name: str, file_base_path: str, file_name: str) -> str:
    """
    Retrieve markdown content from a Supabase storage bucket
    
    Args:
        bucket_name: Name of the bucket to retrieve from
        file_base_path: Base path within the bucket
        file_name: Name of the file to retrieve
        
    Returns:
        str: The markdown content as a string, or empty string if retrieval failed
    """
    bucket = get_relavant_bucket(bucket_name)
    file_path = file_base_path + '/' + file_name
    
    try:
        # Create a temporary file to store the downloaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Download the file from bucket to temp file
            with open(temp_file.name, 'wb') as f:
                response = bucket.download(path=file_path)
                f.write(response)
            
            # Read the content from temp file
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return content
            
    except Exception as e:
        print(f"Error retrieving from bucket: {e}")
        return ""
        
    finally:
        # Clean up temp file if it exists
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
            except:
                pass





