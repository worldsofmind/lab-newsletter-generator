import chardet

def detect_encoding(file):
    raw = file.read()
    file.seek(0)
    result = chardet.detect(raw)
    return result['encoding'] if result['encoding'] else 'utf-8'
