import chardet

def detect_encoding(file_like) -> str:
    """
    Detect encoding of a file-like object (e.g., from Streamlit uploader).
    Resets file pointer afterward.
    """
    raw_data = file_like.read()
    file_like.seek(0)
    result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'
