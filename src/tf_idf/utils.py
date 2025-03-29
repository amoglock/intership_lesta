def check_valid_file_content(file_content: str) -> bool:
    """Checks if the file content type is strictly 'text/plain'.

    Args:
        file_content (str):  The content type string to validate (e.g., from UploadFile.content_type)

    Returns:
        bool: True if the content type is exactly 'text/plain', False otherwise.
    """
    return file_content == 'text/plain'