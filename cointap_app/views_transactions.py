from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q, Sum
from decimal import Decimal
import csv
from datetime import datetime
from .models import UserAccount, Wallet, Category, Transaction, Budget, Notification

def transactions_list_view(request):
    """
    Sổ cái lịch sử giao dịch toàn diện.
    Hỗ trợ tìm kiếm, lọc theo loại giao dịch, theo ví, danh mục và xuất CSV.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    tx_query = Transaction.objects.filter(user=user).select_related('wallet', 'category').order_by('-transaction_date')

    # Bộ lọc
    q_search = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', 'ALL')
    filter_wallet = request.GET.get('wallet', '')
    filter_category = request.GET.get('category', '')
    filter_month = request.GET.get('month', '')

    if q_search:
        tx_query = tx_query.filter(Q(note__icontains=q_search) | Q(category__name__icontains=q_search))
    if filter_type in ('EXPENSE', 'INCOME'):
        tx_query = tx_query.filter(type=filter_type)
    if filter_wallet:
        tx_query = tx_query.filter(wallet_id=filter_wallet)
    if filter_category:
        tx_query = tx_query.filter(category_id=filter_category)
    if filter_month:
        try:
            year, month = map(int, filter_month.split('-'))
            tx_query = tx_query.filter(transaction_date__year=year, transaction_date__month=month)
        except Exception:
            pass

    # Tổng số tiền sau lọc
    total_income = sum((t.amount for t in tx_query if t.type == 'INCOME'), Decimal('0.00'))
    total_expense = sum((t.amount for t in tx_query if t.type == 'EXPENSE'), Decimal('0.00'))

    # Phân trang: 15 giao dịch mỗi trang
    paginator = Paginator(tx_query, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Dữ liệu hỗ trợ form lọc & modal
    wallets = Wallet.objects.filter(user=user, is_active=True)
    categories_expense = Category.objects.filter(Q(user=user) | Q(user__isnull=True), type='EXPENSE', is_active=True)
    categories_income = Category.objects.filter(Q(user=user) | Q(user__isnull=True), type='INCOME', is_active=True)
    all_categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True), is_active=True)

    return render(request, 'cointap/finance/transactions.html', {
        'page_obj': page_obj,
        'wallets': wallets,
        'categories_expense': categories_expense,
        'categories_income': categories_income,
        'all_categories': all_categories,
        'total_income': total_income,
        'total_expense': total_expense,
        'q_search': q_search,
        'filter_type': filter_type,
        'filter_wallet': filter_wallet,
        'filter_category': filter_category,
        'filter_month': filter_month,
    })


def transaction_create_view(request):
    """
    Thêm một giao dịch thu hoặc chi mới.
    Tự động cập nhật số dư ví và kích hoạt cảnh báo ngân sách nếu chi tiêu vượt mức.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        tx_type = request.POST.get('type', 'EXPENSE')
        amount_raw = request.POST.get('amount', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        wallet_id = request.POST.get('wallet_id')
        category_id = request.POST.get('category_id')
        note = request.POST.get('note', '').strip()
        tx_date_raw = request.POST.get('transaction_date')

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError()
        except Exception:
            messages.error(request, "Số tiền giao dịch không hợp lệ.")
            return redirect(request.META.get('HTTP_REFERER', 'transactions_list'))

        wallet = get_object_or_404(Wallet, wallet_id=wallet_id, user=user)
        category = Category.objects.filter(category_id=category_id).first()

        tx_date = timezone.now()
        if tx_date_raw:
            try:
                tx_date = datetime.fromisoformat(tx_date_raw)
                if timezone.is_naive(tx_date):
                    tx_date = timezone.make_aware(tx_date)
            except Exception:
                pass

        # Tạo giao dịch
        new_tx = Transaction.objects.create(
            user=user,
            wallet=wallet,
            category=category,
            amount=amount,
            type=tx_type,
            transaction_date=tx_date,
            note=note
        )

        # Cập nhật số dư ví
        if tx_type == 'INCOME':
            wallet.balance += amount
        else:
            wallet.balance -= amount
        wallet.save()

        # Kiểm tra ngân sách cho danh mục chi tiêu này
        if tx_type == 'EXPENSE' and category:
            budget = Budget.objects.filter(
                user=user,
                category=category,
                start_date__lte=tx_date.date(),
                end_date__gte=tx_date.date()
            ).first()

            if budget:
                # Tính tổng chi hiện tại
                total_spent = Transaction.objects.filter(
                    user=user,
                    category=category,
                    type='EXPENSE',
                    transaction_date__date__gte=budget.start_date,
                    transaction_date__date__lte=budget.end_date
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

                if total_spent > budget.amount:
                    Notification.objects.create(
                        user=user,
                        title=f"Vượt ngân sách: {category.name}",
                        content=f"Bạn vừa chi thêm {amount:,.0f}₫ cho {category.name}. Tổng chi hiện tại ({total_spent:,.0f}₫) đã vượt quá hạn mức ngân sách ({budget.amount:,.0f}₫)!",
                        type="BUDGET_ALERT"
                    )

        messages.success(request, f"Đã lưu giao dịch {('+' if tx_type == 'INCOME' else '-')}{amount:,.0f}₫ thành công.")
        return redirect(request.META.get('HTTP_REFERER', 'transactions_list'))

    return redirect('transactions_list')


def transaction_edit_view(request, transaction_id):
    """
    Chỉnh sửa giao dịch và hoàn trả/áp dụng lại số dư ví chính xác.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    tx = get_object_or_404(Transaction, transaction_id=transaction_id, user=user)

    if request.method == 'POST':
        new_amount_raw = request.POST.get('amount', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        new_wallet_id = request.POST.get('wallet_id')
        new_category_id = request.POST.get('category_id')
        new_note = request.POST.get('note', '').strip()
        new_type = request.POST.get('type', tx.type)
        tx_date_raw = request.POST.get('transaction_date')

        try:
            new_amount = Decimal(new_amount_raw)
        except Exception:
            messages.error(request, "Số tiền không hợp lệ.")
            return redirect('transactions_list')

        # 1. Hoàn lại số dư ví cũ
        old_wallet = tx.wallet
        if tx.type == 'INCOME':
            old_wallet.balance -= tx.amount
        else:
            old_wallet.balance += tx.amount
        old_wallet.save()

        # 2. Cập nhật giao dịch
        new_wallet = get_object_or_404(Wallet, wallet_id=new_wallet_id, user=user)
        tx.wallet = new_wallet
        tx.category = Category.objects.filter(category_id=new_category_id).first()
        tx.amount = new_amount
        tx.type = new_type
        tx.note = new_note
        if tx_date_raw:
            try:
                tx_date = datetime.fromisoformat(tx_date_raw)
                if timezone.is_naive(tx_date):
                    tx_date = timezone.make_aware(tx_date)
                tx.transaction_date = tx_date
            except Exception:
                pass
        tx.save()

        # 3. Trừ/Cộng tiền cho ví mới
        new_wallet.refresh_from_db()
        if new_type == 'INCOME':
            new_wallet.balance += new_amount
        else:
            new_wallet.balance -= new_amount
        new_wallet.save()

        messages.success(request, "Đã cập nhật giao dịch thành công.")
        return redirect('transactions_list')

    return redirect('transactions_list')


def transaction_delete_view(request, transaction_id):
    """
    Xóa giao dịch và hoàn lại số tiền vào ví.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    tx = get_object_or_404(Transaction, transaction_id=transaction_id, user=user)

    wallet = tx.wallet
    amount = tx.amount
    t_type = tx.type

    # Hoàn tiền lại ví
    if t_type == 'INCOME':
        wallet.balance -= amount
    else:
        wallet.balance += amount
    wallet.save()

    tx.delete()
    messages.success(request, f"Đã xóa giao dịch {amount:,.0f}₫ và điều chỉnh lại số dư ví.")
    return redirect(request.META.get('HTTP_REFERER', 'transactions_list'))


def transactions_export_csv(request):
    """
    Xuất danh sách giao dịch ra file CSV tương thích Excel / Google Sheets.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    transactions = Transaction.objects.filter(user=user).select_related('wallet', 'category').order_by('-transaction_date')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="CoinTap_GiaoDich_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Mã GD', 'Thời gian', 'Loại', 'Số tiền (VNĐ)', 'Danh mục', 'Ví nguồn', 'Ghi chú'])

    for t in transactions:
        writer.writerow([
            t.transaction_id,
            t.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Khoản thu' if t.type == 'INCOME' else 'Khoản chi',
            float(t.amount),
            t.category.name if t.category else '',
            t.wallet.wallet_name if t.wallet else '',
            t.note or ''
        ])

    return response

