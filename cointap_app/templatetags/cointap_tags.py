from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='vnd')
def vnd(value):
    """
    Định dạng số tiền với dấu chấm (.) phân cách hàng nghìn.
    Ví dụ: 2543000 -> 2.543.000
           -50000  -> -50.000
    """
    if value is None or value == '':
        return "0"
    try:
        if isinstance(value, str):
            # Loại bỏ ký tự lạ nếu có
            cleaned = value.replace(',', '').replace('.', '').replace('₫', '').strip()
            num = float(cleaned)
        else:
            num = float(value)
        
        is_negative = num < 0
        abs_int = abs(int(round(num)))
        # Dùng format dấu phẩy chuẩn Python rồi đổi sang dấu chấm kiểu Việt Nam
        formatted = f"{abs_int:,}".replace(",", ".")
        return f"-{formatted}" if is_negative else formatted
    except (ValueError, TypeError):
        return str(value)

