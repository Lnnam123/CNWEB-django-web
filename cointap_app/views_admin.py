from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
import json
from .models import (
    AdminAccount, UserAccount, Wallet, Category, Transaction,
    Notification, AIConversation, AIChatMessage
)

def admin_required(view_func):
    """
    Decorator kiểm tra quyền Quản trị viên (Admin).
    """
    def wrapper(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        if not admin_id:
            messages.error(request, "Vui lòng đăng nhập với tài khoản Quản trị viên để truy cập cổng này.")
            return redirect('/login/?role=admin')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard_view(request):
    """
    Trang Quản trị Hệ thống CoinTap (Admin Portal).
    Thống kê tổng quan KPI toàn sàn: người dùng, ví tiền, giao dịch và trợ lý AI.
    """
    admin_id = request.session.get('admin_id')
    current_admin = AdminAccount.objects.get(id=admin_id)

    total_users_count = UserAccount.objects.count()
    total_wallets_count = Wallet.objects.count()
    total_transactions_count = Transaction.objects.count()
    total_admins_count = AdminAccount.objects.count()

    # Tổng tài sản lưu chuyển trên toàn hệ thống
    total_system_cash = Wallet.objects.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

    # Dòng tiền tổng thu và tổng chi hệ thống
    total_system_income = Transaction.objects.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_system_expense = Transaction.objects.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # 10 giao dịch gần đây nhất trên toàn hệ thống
    recent_transactions = Transaction.objects.select_related('user', 'wallet', 'category').order_by('-transaction_date')[:10]

    # Danh mục phổ biến nhất
    category_stats = Category.objects.annotate(tx_count=Count('transactions')).order_by('-tx_count')[:6]
    cat_names = [c.name for c in category_stats]
    cat_counts = [c.tx_count for c in category_stats]

    context = {
        'current_admin': current_admin,
        'total_users_count': total_users_count,
        'total_wallets_count': total_wallets_count,
        'total_transactions_count': total_transactions_count,
        'total_admins_count': total_admins_count,
        'total_system_cash': total_system_cash,
        'total_system_income': total_system_income,
        'total_system_expense': total_system_expense,
        'recent_transactions': recent_transactions,
        'cat_names_json': json.dumps(cat_names),
        'cat_counts_json': json.dumps(cat_counts),
    }

    return render(request, 'cointap/admin/dashboard.html', context)


@admin_required
def admin_users_view(request):
    """
    Quản lý danh sách Người dùng di động / web.
    Xem chi tiết các ví tiền, số dư tài sản và nhật ký giao dịch của từng người dùng.
    """
    users = UserAccount.objects.annotate(
        wallet_count=Count('wallets', distinct=True),
        tx_count=Count('transactions', distinct=True)
    ).order_by('-created_at')

    # Tính tổng tài sản cho từng user
    user_list = []
    for u in users:
        u_wallets = Wallet.objects.filter(user=u)
        u_balance = sum((w.balance for w in u_wallets), Decimal('0.00'))
        u_recent_tx = Transaction.objects.filter(user=u).select_related('wallet', 'category').order_by('-transaction_date')[:5]
        user_list.append({
            'user': u,
            'wallets': u_wallets,
            'total_balance': u_balance,
            'recent_transactions': u_recent_tx,
        })

    return render(request, 'cointap/admin/users.html', {
        'user_list': user_list,
    })


@admin_required
def admin_user_delete_view(request, user_id):
    """
    Xóa tài khoản người dùng và toàn bộ dữ liệu liên quan.
    """
    user = get_object_or_404(UserAccount, user_id=user_id)
    name = user.full_name
    user.delete()
    messages.success(request, f"Đã xóa vĩnh viễn tài khoản người dùng '{name}'.")
    return redirect('admin_users')


@admin_required
def admin_admins_view(request):
    """
    Quản lý danh sách Quản trị viên hệ thống (Super Admin & Administrator).
    """
    admins = AdminAccount.objects.all().order_by('id')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        role = request.POST.get('role', 'Administrator')
        email = request.POST.get('email', '').strip()

        if not username or not password or not full_name:
            messages.error(request, "Vui lòng nhập đầy đủ tên đăng nhập, mật khẩu và họ tên.")
            return redirect('admin_admins')

        if AdminAccount.objects.filter(username=username).exists():
            messages.error(request, f"Tên đăng nhập '{username}' đã được sử dụng.")
            return redirect('admin_admins')

        AdminAccount.objects.create(
            username=username,
            password_hash=password,
            full_name=full_name,
            role=role,
            email=email
        )
        messages.success(request, f"Đã cấp tài khoản quản trị viên mới: {username} ({role}).")
        return redirect('admin_admins')

    return render(request, 'cointap/admin/admins.html', {
        'admins': admins,
    })


@admin_required
def admin_admin_delete_view(request, admin_id):
    """
    Xóa tài khoản quản trị viên.
    """
    current_admin_id = request.session.get('admin_id')
    if current_admin_id == admin_id:
        messages.error(request, "Bạn không thể tự xóa tài khoản của chính mình.")
        return redirect('admin_admins')

    admin = get_object_or_404(AdminAccount, id=admin_id)
    uname = admin.username
    admin.delete()
    messages.success(request, f"Đã xóa quản trị viên '{uname}'.")
    return redirect('admin_admins')


@admin_required
def admin_categories_view(request):
    """
    Quản lý Danh mục Mẫu dùng chung toàn hệ thống (user_id = NULL).
    """
    system_categories = Category.objects.filter(user__isnull=True).order_by('type', 'name')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            name = request.POST.get('name', '').strip()
            cat_type = request.POST.get('type', 'EXPENSE')
            icon = request.POST.get('icon', 'category')
            color = request.POST.get('color', '#6366F1')

            if not name:
                messages.error(request, "Tên danh mục không được để trống.")
                return redirect('admin_categories')

            Category.objects.create(
                user=None,
                name=name,
                type=cat_type,
                icon=icon,
                color=color,
                is_active=True
            )
            messages.success(request, f"Đã thêm danh mục hệ thống: '{name}'")

        elif action == 'edit':
            cat_id = request.POST.get('category_id')
            cat = get_object_or_404(Category, category_id=cat_id, user__isnull=True)
            cat.name = request.POST.get('name', cat.name)
            cat.icon = request.POST.get('icon', cat.icon)
            cat.color = request.POST.get('color', cat.color)
            cat.save()
            messages.success(request, f"Đã cập nhật danh mục '{cat.name}'.")

        return redirect('admin_categories')

    return render(request, 'cointap/admin/categories.html', {
        'system_categories': system_categories,
    })


@admin_required
def admin_category_delete_view(request, category_id):
    """
    Xóa danh mục hệ thống.
    """
    cat = get_object_or_404(Category, category_id=category_id, user__isnull=True)
    cat_name = cat.name
    cat.delete()
    messages.success(request, f"Đã xóa danh mục hệ thống '{cat_name}'.")
    return redirect('admin_categories')


@admin_required
def admin_ai_logs_view(request):
    """
    Giám sát và thanh tra các phiên trò chuyện của người dùng với Gemini AI.
    """
    conversations = AIConversation.objects.select_related('user').order_by('-updated_at')

    # Xem chi tiết một phiên
    session_id = request.GET.get('session')
    active_conv = None
    messages_list = []

    if session_id:
        active_conv = AIConversation.objects.filter(session_id=session_id).select_related('user').first()
        if active_conv:
            messages_list = active_conv.messages.all().order_by('created_at')

    return render(request, 'cointap/admin/ai_logs.html', {
        'conversations': conversations,
        'active_conv': active_conv,
        'messages_list': messages_list,
    })


@admin_required
def admin_broadcast_view(request):
    """
    Phát thông báo đẩy toàn hệ thống tới tất cả người dùng.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        notif_type = request.POST.get('type', 'SYSTEM')

        if not title or not content:
            messages.error(request, "Vui lòng nhập đầy đủ tiêu đề và nội dung thông báo.")
            return redirect('admin_broadcast')

        users = UserAccount.objects.all()
        created_count = 0
        now = timezone.now()

        for u in users:
            Notification.objects.create(
                user=u,
                title=title,
                content=content,
                type=notif_type,
                is_read=False,
                created_at=now
            )
            created_count += 1

        messages.success(request, f"Đã phát thông báo thành công tới tất cả {created_count} người dùng trên hệ thống!")
        return redirect('admin_broadcast')

    # Danh sách các thông báo gần nhất
    recent_broadcasts = Notification.objects.select_related('user').order_by('-created_at')[:15]

    return render(request, 'cointap/admin/broadcast.html', {
        'recent_broadcasts': recent_broadcasts,
    })

