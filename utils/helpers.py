import random
import string
import re
from datetime import datetime

def generate_invoice_number():
    """Generate unique invoice number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INV-{timestamp}-{random_chars}"

def format_currency(amount, symbol='₹'):
    """Format amount as currency"""
    try:
        return f"{symbol} {float(amount):,.2f}"
    except:
        return f"{symbol} 0.00"

def validate_email(email):
    """Basic email validation"""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Basic phone validation"""
    if not phone:
        return False
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    return len(phone) == 10

def validate_barcode(barcode):
    """Validate barcode format (EAN-13, UPC, etc.)"""
    if not barcode:
        return False
    # Remove any non-digit characters
    barcode = re.sub(r'\D', '', barcode)
    # Check length (usually 8, 12, 13, or 14 digits)
    return len(barcode) in [8, 12, 13, 14]

def calculate_tax(amount, tax_rate=0.10):
    """Calculate tax amount"""
    try:
        return float(amount) * tax_rate
    except:
        return 0

def calculate_discount(amount, discount_percent):
    """Calculate discount amount"""
    try:
        return float(amount) * (float(discount_percent) / 100)
    except:
        return 0

def get_current_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_current_date():
    """Get current date"""
    return datetime.now().strftime('%Y-%m-%d')

def format_date(date_obj, format='%d/%m/%Y'):
    """Format date object"""
    if date_obj:
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
            except:
                return date_obj
        return date_obj.strftime(format)
    return ''

def generate_barcode():
    """Generate a random barcode (for testing)"""
    # Generate a random 13-digit EAN-13 like barcode
    prefix = '890'  # India prefix
    middle = ''.join(random.choices(string.digits, k=9))
    barcode = prefix + middle
    # Simple checksum (not real EAN, just for testing)
    return barcode

def parse_barcode(barcode):
    """Parse barcode to extract product code"""
    if not barcode:
        return None
    # Remove any non-digit characters
    return re.sub(r'\D', '', barcode)

def calculate_profit_margin(cost, selling):
    """Calculate profit margin percentage"""
    try:
        cost = float(cost)
        selling = float(selling)
        if cost > 0:
            return ((selling - cost) / cost) * 100
        return 0
    except:
        return 0

def get_readable_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def slugify(text):
    """Convert text to URL-friendly slug"""
    if not text:
        return ''
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

def truncate(text, length=50):
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length-3] + '...'

def time_ago(timestamp):
    """Get human readable time difference"""
    if not timestamp:
        return 'Never'
    
    now = datetime.now()
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'Just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 2592000:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return timestamp.strftime('%d/%m/%Y')
