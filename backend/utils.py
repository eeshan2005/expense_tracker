import os
import uuid
from fastapi import UploadFile
from datetime import datetime
import pytesseract
from PIL import Image
import io

# Configure upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file and return the file path"""
    # Generate a unique filename
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        content = await upload_file.read()
        f.write(content)
    
    return file_path


def extract_text_from_image(file_path: str) -> str:
    """Extract text from an image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def parse_receipt_text(text: str) -> dict:
    """Parse receipt text to extract amount, date, and merchant"""
    # This is a simple implementation and might need to be improved
    # for better accuracy in a production environment
    lines = text.split('\n')
    amount = None
    date = None
    merchant = None
    
    # Try to find the total amount
    for line in lines:
        line = line.lower()
        if 'total' in line and not amount:
            # Extract numbers from the line
            import re
            numbers = re.findall(r'\d+\.\d+', line)
            if numbers:
                amount = float(numbers[-1])  # Assume the last number is the total
    
    # Try to find the date
    for line in lines:
        # Look for common date formats
        import re
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{2,4}'  # MM.DD.YYYY or DD.MM.YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match and not date:
                date_str = match.group(0)
                try:
                    # Try to parse the date
                    from dateutil import parser
                    date = parser.parse(date_str)
                    break
                except:
                    continue
    
    # Try to find the merchant name (usually at the top of the receipt)
    if lines and not merchant:
        # Skip empty lines at the beginning
        start_idx = 0
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        
        if start_idx < len(lines):
            merchant = lines[start_idx].strip()
    
    return {
        "amount": amount,
        "date": date.isoformat() if date else None,
        "merchant": merchant
    }


def format_currency(amount: float) -> str:
    """Format a currency amount"""
    return f"${amount:.2f}"


def calculate_progress(current: float, target: float) -> float:
    """Calculate progress percentage"""
    if target == 0:
        return 0
    return min(100, (current / target) * 100)