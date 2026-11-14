import json
import os
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
from .models import Wallet, Category, Budget, Transaction, UserAccount

def get_user_financial_context(user: UserAccount) -> dict:
    """
    Thu thập số liệu tài chính thời gian thực của người dùng để làm ngữ cảnh cho AI.
    """
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # 1. Ví tiền
    wallets = Wallet.objects.filter(user=user, is_active=True)
    total_balance = sum((w.balance for w in wallets), Decimal('0.00'))
    wallets_summary = [f"{w.wallet_name} ({w.get_wallet_type_display()}): {w.balance:,.0f}₫" for w in wallets]

    # 2. Thu nhập & Chi tiêu tháng hiện tại
    tx_month = Transaction.objects.filter(
        user=user,
        transaction_date__year=current_year,
        transaction_date__month=current_month
    )
    month_expense = sum((t.amount for t in tx_month if t.type == 'EXPENSE'), Decimal('0.00'))
    month_income = sum((t.amount for t in tx_month if t.type == 'INCOME'), Decimal('0.00'))
    net_savings = month_income - month_expense

    # 3. Chi tiết chi tiêu theo danh mục tháng này
    category_expenses = {}
    for t in tx_month:
        if t.type == 'EXPENSE' and t.category:
            cat_name = t.category.name
            category_expenses[cat_name] = category_expenses.get(cat_name, Decimal('0.00')) + t.amount

    # 4. Ngân sách
    budgets = Budget.objects.filter(
        user=user,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    )
    budget_reports = []
    for b in budgets:
        cat = b.category
        spent = category_expenses.get(cat.name, Decimal('0.00')) if cat else Decimal('0.00')
        pct = (spent / b.amount * 100) if b.amount > 0 else 0
        remain = b.amount - spent
        status = "Vượt hạn mức ❌" if spent > b.amount else ("Cảnh báo ⚠️" if pct >= 80 else "An toàn ✅")
        budget_reports.append({
            'category': cat.name if cat else "Chung",
            'limit': b.amount,
            'spent': spent,
            'remain': remain,
            'pct': pct,
            'status': status
        })

    # 5. Giao dịch gần nhất (10 giao dịch)
    recent_txs = Transaction.objects.filter(user=user).order_by('-transaction_date')[:10]
    recent_tx_list = []
    for t in recent_txs:
        cat_name = t.category.name if t.category else "Khác"
        sign = "+" if t.type == 'INCOME' else "-"
        recent_tx_list.append(
            f"• {t.transaction_date.strftime('%d/%m')}: {sign}{t.amount:,.0f}₫ - {cat_name} ({t.note or 'Không có ghi chú'})"
        )

    # 6. Tính số ngày còn lại trong tháng
    import calendar
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days_remaining = max(1, days_in_month - now.day)
    safe_daily_spend = (total_balance / Decimal(days_remaining)) if total_balance > 0 else Decimal('0.00')

    return {
        'user_name': user.full_name,
        'current_month': current_month,
        'current_year': current_year,
        'total_balance': total_balance,
        'wallets_summary': wallets_summary,
        'month_expense': month_expense,
        'month_income': month_income,
        'net_savings': net_savings,
        'category_expenses': category_expenses,
        'budget_reports': budget_reports,
        'recent_tx_list': recent_tx_list,
        'days_remaining': days_remaining,
        'safe_daily_spend': safe_daily_spend,
    }


def generate_ai_financial_response(prompt: str, user: UserAccount) -> str:
    """
    Tạo phản hồi tư vấn tài chính thông minh dựa trên dữ liệu người dùng.
    Ưu tiên gọi Google Gemini API nếu có key hợp lệ; nếu gặp lỗi mạng hoặc không có key,
    tự động kích hoạt bộ máy phân tích nội bộ (Rule-based Financial Intelligence Engine).
    """
    ctx = get_user_financial_context(user)
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    # Chuẩn bị system prompt có đầy đủ số liệu tài chính của người dùng
    system_context = f"""
Bạn là CoinTap AI - Trợ lý cố vấn tài chính cá nhân thông minh, am hiểu tài chính, nhiệt tình và thực tế.
Người dùng đang trò chuyện với bạn tên là {ctx['user_name']}.
Dữ liệu tài chính thực tế hiện tại của người dùng trong hệ thống CoinTap:
- Tổng số dư khả dụng trên tất cả các ví: {ctx['total_balance']:,.0f} VNĐ ({', '.join(ctx['wallets_summary']) if ctx['wallets_summary'] else 'Chưa có ví'})
- Thu nhập tháng {ctx['current_month']}: {ctx['month_income']:,.0f} VNĐ
- Chi tiêu tháng {ctx['current_month']}: {ctx['month_expense']:,.0f} VNĐ
- Thặng dư/Tiết kiệm tích lũy tháng này: {ctx['net_savings']:,.0f} VNĐ
- Số ngày còn lại trong tháng: {ctx['days_remaining']} ngày
- Hạn mức chi tiêu an toàn mỗi ngày: {ctx['safe_daily_spend']:,.0f} VNĐ/ngày

Tình hình ngân sách:
{chr(10).join([f"• {b['category']}: Đã chi {b['spent']:,.0f}đ / {b['limit']:,.0f}đ ({b['pct']:.0f}%) - {b['status']}" for b in ctx['budget_reports']]) if ctx['budget_reports'] else 'Chưa thiết lập ngân sách'}

Giao dịch gần nhất:
{chr(10).join(ctx['recent_tx_list']) if ctx['recent_tx_list'] else 'Chưa có giao dịch'}

Hãy trả lời bằng tiếng Việt, ngắn gọn, chuẩn xác, định dạng Markdown rõ ràng với các gạch đầu dòng, số tiền in đậm có đơn vị đ.
Kết bài luôn gợi ý thêm 2-3 câu hỏi hoặc hướng phân tích tiếp theo kèm icon sinh động.
"""

    if api_key and not api_key.startswith('AQ.'):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{system_context}\n\nNgười dùng hỏi: {prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
        except Exception:
            pass

    # Bộ máy phân tích nội bộ (Rule-based Contextual Financial Engine)
    p_lower = prompt.lower()

    if any(k in p_lower for k in ['vượt', 'hạn mức', 'ngân sách', 'hết tiền']):
        over_budgets = [b for b in ctx['budget_reports'] if b['spent'] > b['limit']]
        if over_budgets:
            msg = f"⚠️ Bạn đang có danh mục **vượt hạn mức ngân sách** tháng {ctx['current_month']}:\n\n"
            for b in over_budgets:
                msg += f"• **{b['category']}**: đã tiêu **{b['spent']:,.0f}đ** / **{b['limit']:,.0f}đ** (vượt {(b['spent']-b['limit']):,.0f}đ)\n"
            msg += f"\nTổng chi tiêu thực tế hiện tại: **{ctx['month_expense']:,.0f}đ** trên tổng thu nhập **{ctx['month_income']:,.0f}đ**.\n"
        else:
            msg = f"Hiện tại, tổng chi tiêu tháng {ctx['current_month']} của bạn **chưa vượt hạn mức** ngân sách! ✅\n\n"
            msg += "**Tình hình ngân sách các danh mục:**\n"
            for b in ctx['budget_reports']:
                msg += f"• **{b['category']}**: đã chi **{b['spent']:,.0f}đ** / **{b['limit']:,.0f}đ** ({b['pct']:.0f}%) - **{b['status']}** (còn lại **{b['remain']:,.0f}đ**)\n"
            msg += f"• **Tổng chi tiêu thực tế tháng này**: **{ctx['month_expense']:,.0f}đ** (trên tổng thu nhập **{ctx['month_income']:,.0f}đ**)\n"

        msg += "\nNếu bạn muốn, mình có thể phân tích tiếp:\n"
        msg += "• **dự báo tốc độ chi tiêu** đến cuối tháng\n"
        msg += "• **gợi ý kế hoạch tiết kiệm** từ số tiền dư còn lại\n"
        msg += "• hoặc **xem chi tiết các giao dịch gần đây** 📊"
        return msg

    elif any(k in p_lower for k in ['tăng vọt', 'sao tháng này', 'tại sao', 'nhiều tiền']):
        sorted_cats = sorted(ctx['category_expenses'].items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_cats[0] if sorted_cats else ("Chưa xác định", Decimal('0'))
        top_pct = (top_cat[1] / ctx['month_expense'] * 100) if ctx['month_expense'] > 0 else 0

        msg = f"Chi tiêu tháng {ctx['current_month']} của bạn tăng vọt chủ yếu do khoản chi vào danh mục **{top_cat[0]}** với **{top_cat[1]:,.0f}đ** (chiếm gần {top_pct:.0f}% tổng chi tiêu) 🏠\n\n"
        msg += "**Chi tiết phân tích chi tiêu tháng này:**\n"
        msg += f"• **Khoản chi lớn nhất:** Danh mục {top_cat[0]} với tổng **{top_cat[1]:,.0f}đ**.\n"
        msg += f"• **Tổng chi tiêu hiện tại:** **{ctx['month_expense']:,.0f}đ** trên tổng thu nhập **{ctx['month_income']:,.0f}đ**.\n"
        msg += f"• **Số dư khả dụng hiện tại:** **{ctx['total_balance']:,.0f}đ**.\n\n"
        msg += "Nếu bạn muốn, mình có thể phân tích tiếp:\n"
        msg += f"• **dự báo chi tiêu còn lại trong tháng {ctx['current_month']}** 📊\n"
        msg += "• **chi tiết hạn mức ngân sách các danh mục sinh hoạt**\n"
        msg += f"• hoặc **gợi ý kế hoạch phân bổ số dư {ctx['total_balance']:,.0f}đ hiện tại** 💰"
        return msg

    elif any(k in p_lower for k in ['bao nhiêu tiền', 'tối đa', 'mỗi ngày', 'hạn mức ngày']):
        daily_limit = ctx['safe_daily_spend']
        msg = f"Để quản lý tài chính an toàn trong {ctx['days_remaining']} ngày còn lại của tháng {ctx['current_month']}, {ctx['user_name']} nên chi tiêu tối đa khoảng **{daily_limit:,.0f}đ/ngày** 💡\n\n"
        msg += "**Cơ sở tính toán chi tiết:**\n"
        msg += f"• **Số dư tài sản hiện tại:** **{ctx['total_balance']:,.0f}đ** across các ví.\n"
        msg += f"• **Thời gian còn lại trong tháng:** **{ctx['days_remaining']} ngày**.\n"
        msg += f"• **Hạn mức theo tổng số dư khả dụng:** Tối đa **{daily_limit:,.0f}đ/ngày**.\n"
        msg += f"• **Hạn mức khuyến nghị:** Nếu giữ thặng dư tiết kiệm, bạn nên duy trì mức **{(daily_limit * Decimal('0.7')):,.0f}đ/ngày**.\n\n"
        msg += "Nếu bạn muốn, mình có thể phân tích tiếp:\n"
        msg += "• **gợi ý điều chỉnh hạn mức danh mục cho thực tế hơn**\n"
        msg += "• **lập kế hoạch phân bổ chi tiêu chi tiết theo từng tuần**\n"
        msg += "• hoặc **mẹo cắt giảm các khoản chi vặt không cần thiết** 📊"
        return msg

    elif any(k in p_lower for k in ['chi vặt', 'tiết kiệm', 'cắt giảm', 'mẹo']):
        msg = f"Chào {ctx['user_name']}, việc kiểm soát các khoản chi vặt như **đồ uống, ăn vặt và đồ dùng mua đột xuất** sẽ giúp bạn tiết kiệm ngay từ **300.000đ - 500.000đ mỗi tháng** 💡\n\n"
        msg += "**Các mẹo cắt giảm chi vặt hiệu quả:**\n"
        msg += "• **Kiểm soát món ăn kèm và nước uống:** Các khoản nhỏ như trà sữa, cà phê, soda tuy nhỏ nhưng cộng dồn cả tháng lên đến hàng trăm nghìn đồng.\n"
        msg += "• **Áp dụng quy tắc 'Dừng 5 giây':** Trước khi thanh toán khoản chi ngẫu hứng dưới **50.000đ**, hãy tự hỏi khoản này là 'Thực sự cần' hay chỉ là 'Sở thích bộc phát'.\n"
        msg += "• **Theo dõi sát hạn mức trên CoinTap:** Ghi chép ngay lập tức sau khi thanh toán giúp bạn luôn tỉnh táo trước khi ví cạn tiền.\n\n"
        msg += "Nếu bạn muốn, mình có thể phân tích tiếp:\n"
        msg += "• **tổng số tiền chi cho ăn uống/giải trí** từ đầu tháng đến nay\n"
        msg += f"• **gợi ý hạn mức chi tiêu theo ngày** phù hợp với số dư **{ctx['total_balance']:,.0f}đ** hiện tại\n"
        msg += "• hoặc **dự báo chi tiêu** trong những tuần tiếp theo 📊"
        return msg

    elif any(k in p_lower for k in ['gần đây', 'lịch sử', 'chi tiết giao dịch']):
        msg = f"Dưới đây là **danh sách các giao dịch gần đây nhất** của bạn 📋\n\n**Chi tiết các giao dịch:**\n"
        msg += "\n".join(ctx['recent_tx_list'][:8]) if ctx['recent_tx_list'] else "• Chưa có giao dịch nào được ghi nhận."
        msg += "\n\nNếu bạn muốn, mình có thể phân tích tiếp:\n"
        msg += "• **chi tiết cơ cấu chi tiêu từng danh mục**\n"
        msg += f"• **gợi ý phân bổ số dư còn lại ({ctx['total_balance']:,.0f}đ)**\n"
        msg += "• hoặc **dự báo chi tiêu cho những tuần tiếp theo** 📊"
        return msg

    else:
        # Tổng quát
        msg = f"Chào {ctx['user_name']}! Mình là Trợ lý tài chính CoinTap AI 🤖.\n\n"
        msg += f"Hiện tại bạn đang có tổng tài sản khả dụng là **{ctx['total_balance']:,.0f}đ**.\n"
        msg += f"Tháng {ctx['current_month']} này, bạn đã thu vào **{ctx['month_income']:,.0f}đ** và chi ra **{ctx['month_expense']:,.0f}đ**.\n\n"
        msg += "Bạn có thể hỏi mình bất kỳ câu hỏi nào về tài chính như:\n"
        msg += "• *Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?*\n"
        msg += "• *Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?*\n"
        msg += "• *Sao tháng này chi tiêu của tôi lại tăng vọt?*\n"
        msg += "• *Mẹo cắt giảm các khoản chi vặt không cần thiết*"
        return msg

