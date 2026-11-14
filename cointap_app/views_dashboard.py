from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
import json
from datetime import timedelta, datetime
from .models import UserAccount, Wallet, Category, Transaction, Budget

def dashboard_view(request):
    """
    Trang Tổng quan Dashboard người dùng cá nhân (Financial Pulse).
    Hiển thị tổng tài sản, dòng tiền tháng, trạng thái ngân sách và biểu đồ tài chính.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        if request.session.get('admin_id'):
            return redirect('admin_dashboard')
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # 1. Danh sách ví tiền
    wallets = Wallet.objects.filter(user=user, is_active=True).order_by('-balance')
    total_balance = sum((w.balance for w in wallets), Decimal('0.00'))

    # 2. Thu nhập và Chi tiêu tháng này
    current_month_txs = Transaction.objects.filter(
        user=user,
        transaction_date__year=current_year,
        transaction_date__month=current_month
    )
    month_income = sum((t.amount for t in current_month_txs if t.type == 'INCOME'), Decimal('0.00'))
    month_expense = sum((t.amount for t in current_month_txs if t.type == 'EXPENSE'), Decimal('0.00'))
    net_savings = month_income - month_expense
    savings_rate = (net_savings / month_income * 100) if month_income > 0 else 0

    # 3. Thu nhập và Chi tiêu tháng trước (để so sánh)
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    last_month_txs = Transaction.objects.filter(
        user=user,
        transaction_date__year=last_month_year,
        transaction_date__month=last_month
    )
    last_month_expense = sum((t.amount for t in last_month_txs if t.type == 'EXPENSE'), Decimal('0.00'))
    expense_diff_pct = 0
    if last_month_expense > 0:
        expense_diff_pct = ((month_expense - last_month_expense) / last_month_expense) * 100

    # 4. Giao dịch gần đây (8 giao dịch)
    recent_transactions = Transaction.objects.filter(user=user).select_related('wallet', 'category').order_by('-transaction_date')[:8]

    # 5. Tình trạng Ngân sách các danh mục
    budgets = Budget.objects.filter(
        user=user,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    ).select_related('category')
    
    budget_cards = []
    for b in budgets:
        # Tính tổng chi cho danh mục này trong khoảng thời gian ngân sách
        spent = Transaction.objects.filter(
            user=user,
            category=b.category,
            type='EXPENSE',
            transaction_date__date__gte=b.start_date,
            transaction_date__date__lte=b.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        pct = float((spent / b.amount) * 100) if b.amount > 0 else 0.0
        remaining = b.amount - spent
        
        # Phân loại trạng thái ngân sách theo thiết kế
        if pct >= 100:
            status_color = 'danger'
            status_text = 'Vượt hạn mức'
        elif pct >= 80:
            status_color = 'warning'
            status_text = 'Cảnh báo > 80%'
        else:
            status_color = 'success'
            status_text = 'An toàn'

        budget_cards.append({
            'budget': b,
            'category': b.category,
            'spent': spent,
            'limit': b.amount,
            'remaining': remaining,
            'percentage': min(pct, 100.0),
            'raw_percentage': pct,
            'status_color': status_color,
            'status_text': status_text,
        })

    # 6. Dữ liệu Biểu đồ Dòng tiền 7 ngày gần nhất
    day_labels = []
    income_series = []
    expense_series = []
    for i in range(6, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        day_str = target_date.strftime('%d/%m')
        day_labels.append(day_str)

        day_txs = Transaction.objects.filter(
            user=user,
            transaction_date__date=target_date
        )
        d_inc = float(sum((t.amount for t in day_txs if t.type == 'INCOME'), Decimal('0.00')))
        d_exp = float(sum((t.amount for t in day_txs if t.type == 'EXPENSE'), Decimal('0.00')))
        income_series.append(d_inc)
        expense_series.append(d_exp)

    # 7. Dữ liệu Biểu đồ Tỷ trọng Chi tiêu theo Danh mục (Donut Chart)
    cat_expense_dict = {}
    for t in current_month_txs:
        if t.type == 'EXPENSE':
            c_name = t.category.name if t.category else 'Khác'
            cat_expense_dict[c_name] = cat_expense_dict.get(c_name, Decimal('0.00')) + t.amount

    category_donut_labels = list(cat_expense_dict.keys())
    category_donut_data = [float(val) for val in cat_expense_dict.values()]

    # Danh mục dùng cho Modal thêm nhanh giao dịch
    categories_expense = Category.objects.filter(Q(user=user) | Q(user__isnull=True), type='EXPENSE', is_active=True)
    categories_income = Category.objects.filter(Q(user=user) | Q(user__isnull=True), type='INCOME', is_active=True)

    context = {
        'total_balance': total_balance,
        'month_income': month_income,
        'month_expense': month_expense,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'expense_diff_pct': expense_diff_pct,
        'wallets': wallets,
        'recent_transactions': recent_transactions,
        'budget_cards': budget_cards,
        'categories_expense': categories_expense,
        'categories_income': categories_income,
        # Chart JSON
        'chart_days_json': json.dumps(day_labels),
        'chart_income_json': json.dumps(income_series),
        'chart_expense_json': json.dumps(expense_series),
        'donut_labels_json': json.dumps(category_donut_labels),
        'donut_data_json': json.dumps(category_donut_data),
    }

    return render(request, 'cointap/finance/dashboard.html', context)

