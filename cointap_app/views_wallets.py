from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import UserAccount, Wallet, Transaction, Category

def wallets_list_view(request):
    """
    Quản lý danh sách các ví tiền của người dùng.
    Hỗ trợ thêm ví, sửa ví, chuyển khoản giữa các ví.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    wallets = Wallet.objects.filter(user=user).order_by('-is_active', '-balance')
    total_balance = sum((w.balance for w in wallets if w.is_active), Decimal('0.00'))

    return render(request, 'cointap/finance/wallets.html', {
        'wallets': wallets,
        'total_balance': total_balance,
    })


def wallet_create_view(request):
    """
    Thêm mới một ví tiền hoặc tài khoản ngân hàng.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        wallet_name = request.POST.get('wallet_name', '').strip()
        wallet_type = request.POST.get('wallet_type', 'CASH')
        initial_balance = request.POST.get('balance', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        icon = request.POST.get('icon', 'account_balance_wallet')
        color = request.POST.get('color', '#10B981')

        try:
            balance_val = Decimal(initial_balance)
        except Exception:
            balance_val = Decimal('0.00')

        if not wallet_name:
            messages.error(request, "Vui lòng nhập tên ví.")
            return redirect('wallets_list')

        new_wallet = Wallet.objects.create(
            user=user,
            wallet_name=wallet_name,
            wallet_type=wallet_type,
            balance=balance_val,
            icon=icon,
            color=color,
            is_active=True
        )

        # Nếu có số dư ban đầu > 0, tạo giao dịch ghi nhận số dư ban đầu
        if balance_val > 0:
            income_cat = Category.objects.filter(type='INCOME', name__icontains='khác').first()
            if not income_cat:
                income_cat = Category.objects.filter(type='INCOME').first()
            Transaction.objects.create(
                user=user,
                wallet=new_wallet,
                category=income_cat,
                amount=balance_val,
                type='INCOME',
                transaction_date=timezone.now(),
                note=f"Khởi tạo số dư ban đầu cho ví {wallet_name}"
            )

        messages.success(request, f"Đã tạo thành công ví '{wallet_name}'!")
        return redirect('wallets_list')

    return redirect('wallets_list')


def wallet_edit_view(request, wallet_id):
    """
    Cập nhật thông tin ví tiền (tên, loại ví, màu sắc, icon, trạng thái).
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    wallet = get_object_or_404(Wallet, wallet_id=wallet_id, user=user)

    if request.method == 'POST':
        wallet_name = request.POST.get('wallet_name', '').strip()
        wallet_type = request.POST.get('wallet_type', wallet.wallet_type)
        icon = request.POST.get('icon', wallet.icon)
        color = request.POST.get('color', wallet.color)
        is_active = request.POST.get('is_active') == 'on'

        if wallet_name:
            wallet.wallet_name = wallet_name
        wallet.wallet_type = wallet_type
        wallet.icon = icon
        wallet.color = color
        wallet.is_active = is_active
        wallet.save()

        messages.success(request, f"Đã cập nhật thông tin ví '{wallet.wallet_name}'.")
        return redirect('wallets_list')

    return redirect('wallets_list')


def wallet_delete_view(request, wallet_id):
    """
    Xóa hoặc chuyển ví sang trạng thái lưu trữ / ngừng hoạt động.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    wallet = get_object_or_404(Wallet, wallet_id=wallet_id, user=user)

    # Đảm bảo người dùng luôn có ít nhất 1 ví
    if Wallet.objects.filter(user=user, is_active=True).count() <= 1 and wallet.is_active:
        messages.error(request, "Bạn phải giữ lại ít nhất một ví tiền đang hoạt động.")
        return redirect('wallets_list')

    wallet_name = wallet.wallet_name
    wallet.delete()
    messages.success(request, f"Đã xóa vĩnh viễn ví '{wallet_name}'.")
    return redirect('wallets_list')


def wallet_transfer_view(request):
    """
    Chuyển tiền giữa 2 ví khác nhau của người dùng.
    Tự động ghi nhận giao dịch xuất tiền ở ví nguồn và nhận tiền ở ví đích.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        source_id = request.POST.get('source_wallet_id')
        target_id = request.POST.get('target_wallet_id')
        amount_raw = request.POST.get('amount', '0').replace('.', '').replace(',', '').replace('₫', '').strip()
        note = request.POST.get('note', '').strip()

        if source_id == target_id:
            messages.error(request, "Ví nguồn và ví đích không được trùng nhau.")
            return redirect('wallets_list')

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError()
        except Exception:
            messages.error(request, "Số tiền chuyển phải lớn hơn 0.")
            return redirect('wallets_list')

        source_wallet = get_object_or_404(Wallet, wallet_id=source_id, user=user)
        target_wallet = get_object_or_404(Wallet, wallet_id=target_id, user=user)

        # Trừ tiền ví nguồn và cộng tiền ví đích
        source_wallet.balance -= amount
        source_wallet.save()

        target_wallet.balance += amount
        target_wallet.save()

        # Tìm danh mục chuyển khoản hoặc danh mục mặc định
        transfer_cat_exp = Category.objects.filter(type='EXPENSE', name__icontains='chuyển').first() or Category.objects.filter(type='EXPENSE').first()
        transfer_cat_inc = Category.objects.filter(type='INCOME', name__icontains='chuyển').first() or Category.objects.filter(type='INCOME').first()

        now = timezone.now()
        transfer_note = note if note else f"Chuyển tiền từ {source_wallet.wallet_name} sang {target_wallet.wallet_name}"

        # Giao dịch trừ tiền ví nguồn
        Transaction.objects.create(
            user=user,
            wallet=source_wallet,
            category=transfer_cat_exp,
            amount=amount,
            type='EXPENSE',
            transaction_date=now,
            note=f"[Chuyển đi] {transfer_note}"
        )

        # Giao dịch cộng tiền ví đích
        Transaction.objects.create(
            user=user,
            wallet=target_wallet,
            category=transfer_cat_inc,
            amount=amount,
            type='INCOME',
            transaction_date=now,
            note=f"[Nhận về] {transfer_note}"
        )

        messages.success(request, f"Đã chuyển {amount:,.0f}₫ từ ví '{source_wallet.wallet_name}' sang ví '{target_wallet.wallet_name}' thành công!")
        return redirect('wallets_list')

    return redirect('wallets_list')

