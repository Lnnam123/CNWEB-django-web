from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date, datetime
from .models import UserAccount, Budget, Category, Transaction

def budgets_list_view(request):
    """
    Quản lý hạn mức ngân sách chi tiêu theo danh mục.
    Tự động tính toán số tiền đã chi, số tiền còn lại và tỷ lệ phần trăm tiêu thụ.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    now = timezone.now()

    budgets = Budget.objects.filter(user=user).select_related('category').order_by('-created_at')

    budget_items = []
    total_budget_limit = Decimal('0.00')
    total_budget_spent = Decimal('0.00')

    for b in budgets:
        # Tính số tiền đã chi trong khoảng thời gian của ngân sách
        spent = Transaction.objects.filter(
            user=user,
            category=b.category,
            type='EXPENSE',
            transaction_date__date__gte=b.start_date,
            transaction_date__date__lte=b.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_budget_limit += b.amount
        total_budget_spent += spent

        pct = float((spent / b.amount) * 100) if b.amount > 0 else 0.0
        remaining = b.amount - spent

        # Tính số ngày còn lại trong kỳ ngân sách
        days_total = max(1, (b.end_date - b.start_date).days + 1)
        days_left = max(0, (b.end_date - now.date()).days + 1)
        daily_safe = (remaining / Decimal(days_left)) if (days_left > 0 and remaining > 0) else Decimal('0.00')

        if pct >= 100:
            badge_class = 'danger'
            badge_text = 'Vượt hạn mức'
        elif pct >= 80:
            badge_class = 'warning'
            badge_text = 'Cảnh báo nguy cơ'
        else:
            badge_class = 'success'
            badge_text = 'An toàn'

        budget_items.append({
            'budget': b,
            'category': b.category,
            'spent': spent,
            'limit': b.amount,
            'remaining': remaining,
            'percentage': min(pct, 100.0),
            'raw_percentage': pct,
            'days_left': days_left,
            'daily_safe': daily_safe,
            'badge_class': badge_class,
            'badge_text': badge_text,
        })

    # Danh mục chưa được đặt ngân sách
    expense_categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True), type='EXPENSE', is_active=True)

    return render(request, 'cointap/finance/budgets.html', {
        'budget_items': budget_items,
        'total_budget_limit': total_budget_limit,
        'total_budget_spent': total_budget_spent,
        'total_budget_remaining': max(Decimal('0.00'), total_budget_limit - total_budget_spent),
        'expense_categories': expense_categories,
    })


def budget_create_view(request):
    """
    Thêm mới một hạn mức ngân sách chi tiêu.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        amount_raw = request.POST.get('amount', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        start_date_raw = request.POST.get('start_date')
        end_date_raw = request.POST.get('end_date')

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError()
            start_date = date.fromisoformat(start_date_raw)
            end_date = date.fromisoformat(end_date_raw)
            if start_date > end_date:
                messages.error(request, "Ngày bắt đầu không được lớn hơn ngày kết thúc.")
                return redirect('budgets_list')
        except Exception:
            messages.error(request, "Vui lòng nhập số tiền và khoảng thời gian hợp lệ.")
            return redirect('budgets_list')

        category = Category.objects.filter(category_id=category_id).first()

        Budget.objects.create(
            user=user,
            category=category,
            amount=amount,
            start_date=start_date,
            end_date=end_date
        )

        messages.success(request, f"Đã thiết lập hạn mức ngân sách {amount:,.0f}₫ cho {category.name if category else 'danh mục'}.")
        return redirect('budgets_list')

    return redirect('budgets_list')


def budget_edit_view(request, budget_id):
    """
    Chỉnh sửa hạn mức ngân sách.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    budget = get_object_or_404(Budget, budget_id=budget_id, user=user)

    if request.method == 'POST':
        amount_raw = request.POST.get('amount', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        start_date_raw = request.POST.get('start_date')
        end_date_raw = request.POST.get('end_date')

        try:
            budget.amount = Decimal(amount_raw)
            if start_date_raw:
                budget.start_date = date.fromisoformat(start_date_raw)
            if end_date_raw:
                budget.end_date = date.fromisoformat(end_date_raw)
            budget.save()
            messages.success(request, "Đã cập nhật ngân sách thành công.")
        except Exception:
            messages.error(request, "Dữ liệu chỉnh sửa không hợp lệ.")

    return redirect('budgets_list')


def budget_delete_view(request, budget_id):
    """
    Xóa hạn mức ngân sách.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    budget = get_object_or_404(Budget, budget_id=budget_id, user=user)
    budget.delete()
    messages.success(request, "Đã xóa kế hoạch ngân sách thành công.")
    return redirect('budgets_list')


def categories_list_view(request):
    """
    Quản lý danh mục thu/chi của người dùng và xem danh mục hệ thống.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    system_categories = Category.objects.filter(user__isnull=True, is_active=True)
    user_categories = Category.objects.filter(user=user)

    return render(request, 'cointap/finance/categories.html', {
        'system_categories': system_categories,
        'user_categories': user_categories,
    })


def category_create_view(request):
    """
    Tạo danh mục mới riêng cho người dùng cá nhân.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        cat_type = request.POST.get('type', 'EXPENSE')
        icon = request.POST.get('icon', 'category')
        color = request.POST.get('color', '#6366F1')

        if not name:
            messages.error(request, "Tên danh mục không được để trống.")
            return redirect('categories_list')

        Category.objects.create(
            user=user,
            name=name,
            type=cat_type,
            icon=icon,
            color=color,
            is_active=True
        )
        messages.success(request, f"Đã thêm danh mục mới: '{name}'")
        return redirect('categories_list')

    return redirect('categories_list')


def category_delete_view(request, category_id):
    """
    Xóa danh mục riêng của người dùng.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    cat = get_object_or_404(Category, category_id=category_id, user=user)

    # Kiểm tra xem danh mục đã phát sinh giao dịch chưa
    if Transaction.objects.filter(category=cat).exists():
        messages.error(request, "Không thể xóa danh mục đã phát sinh giao dịch. Bạn có thể ẩn danh mục này.")
        return redirect('categories_list')

    cat_name = cat.name
    cat.delete()
    messages.success(request, f"Đã xóa danh mục '{cat_name}'.")
    return redirect('categories_list')

