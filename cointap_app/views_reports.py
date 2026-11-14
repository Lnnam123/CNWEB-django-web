from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import json
import calendar
from datetime import datetime, timedelta
from .models import UserAccount, Transaction, Category, Wallet

def reports_view(request):
    """
    Báo cáo thống kê tài chính và phân tích chuyên sâu.
    Trực quan hóa thu nhập, chi tiêu, xu hướng và cơ cấu chi tiêu.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    now = timezone.now()

    # Chọn tháng/năm báo cáo (mặc định tháng hiện tại)
    selected_month_str = request.GET.get('month', now.strftime('%Y-%m'))
    try:
        sel_year, sel_month = map(int, selected_month_str.split('-'))
    except Exception:
        sel_year, sel_month = now.year, now.month
        selected_month_str = now.strftime('%Y-%m')

    # Lấy giao dịch trong tháng đã chọn
    month_txs = Transaction.objects.filter(
        user=user,
        transaction_date__year=sel_year,
        transaction_date__month=sel_month
    ).select_related('category', 'wallet')

    total_income = sum((t.amount for t in month_txs if t.type == 'INCOME'), Decimal('0.00'))
    total_expense = sum((t.amount for t in month_txs if t.type == 'EXPENSE'), Decimal('0.00'))
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    # Số ngày trong tháng đã chọn
    num_days = calendar.monthrange(sel_year, sel_month)[1]
    days_passed = now.day if (sel_year == now.year and sel_month == now.month) else num_days
    avg_daily_expense = (total_expense / Decimal(max(1, days_passed))) if total_expense > 0 else Decimal('0.00')

    # Cơ cấu chi tiêu theo danh mục (Donut Chart)
    cat_expense_dict = {}
    for t in month_txs:
        if t.type == 'EXPENSE':
            c_name = t.category.name if t.category else 'Khác'
            cat_expense_dict[c_name] = cat_expense_dict.get(c_name, Decimal('0.00')) + t.amount

    # Sắp xếp top danh mục chi nhiều nhất
    top_categories = sorted(cat_expense_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    top_categories_list = []
    for c_name, amt in top_categories:
        pct = (amt / total_expense * 100) if total_expense > 0 else 0
        top_categories_list.append({
            'name': c_name,
            'amount': amt,
            'percentage': pct
        })

    expense_donut_labels = list(cat_expense_dict.keys())
    expense_donut_data = [float(v) for v in cat_expense_dict.values()]

    # Cơ cấu thu nhập theo danh mục
    cat_income_dict = {}
    for t in month_txs:
        if t.type == 'INCOME':
            c_name = t.category.name if t.category else 'Khác'
            cat_income_dict[c_name] = cat_income_dict.get(c_name, Decimal('0.00')) + t.amount
    income_donut_labels = list(cat_income_dict.keys())
    income_donut_data = [float(v) for v in cat_income_dict.values()]

    # Biểu đồ xu hướng 6 tháng gần nhất (Bar Chart)
    six_months_labels = []
    six_months_income = []
    six_months_expense = []

    for i in range(5, -1, -1):
        # Tính tháng lùi
        m = sel_month - i
        y = sel_year
        while m <= 0:
            m += 12
            y -= 1
        month_label = f"T{m}/{str(y)[2:]}"
        six_months_labels.append(month_label)

        sub_txs = Transaction.objects.filter(user=user, transaction_date__year=y, transaction_date__month=m)
        inc = float(sum((t.amount for t in sub_txs if t.type == 'INCOME'), Decimal('0.00')))
        exp = float(sum((t.amount for t in sub_txs if t.type == 'EXPENSE'), Decimal('0.00')))
        six_months_income.append(inc)
        six_months_expense.append(exp)

    # Đánh giá sức khỏe tài chính
    if savings_rate >= 30:
        health_status = "Rất tốt"
        health_color = "success"
        health_tip = "Bạn đang duy trì tỷ lệ tích lũy xuất sắc trên 30%! Hãy tiếp tục chuyển phần dư vào quỹ tiết kiệm hoặc đầu tư."
    elif savings_rate > 0:
        health_status = "Ổn định"
        health_color = "info"
        health_tip = "Dòng tiền dương nhưng tỷ lệ tích lũy còn khiêm tốn. Cắt giảm bớt các khoản chi vặt có thể giúp tăng thặng dư."
    else:
        health_status = "Cần chấn chỉnh"
        health_color = "danger"
        health_tip = "Chi tiêu đang vượt quá thu nhập tháng này! Hãy rà soát lại các khoản chi lớn và giới hạn ngân sách ngay."

    context = {
        'selected_month_str': selected_month_str,
        'sel_year': sel_year,
        'sel_month': sel_month,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'avg_daily_expense': avg_daily_expense,
        'top_categories_list': top_categories_list,
        'health_status': health_status,
        'health_color': health_color,
        'health_tip': health_tip,
        'expense_donut_labels_json': json.dumps(expense_donut_labels),
        'expense_donut_data_json': json.dumps(expense_donut_data),
        'income_donut_labels_json': json.dumps(income_donut_labels),
        'income_donut_data_json': json.dumps(income_donut_data),
        'six_months_labels_json': json.dumps(six_months_labels),
        'six_months_income_json': json.dumps(six_months_income),
        'six_months_expense_json': json.dumps(six_months_expense),
    }

    return render(request, 'cointap/finance/reports.html', context)

