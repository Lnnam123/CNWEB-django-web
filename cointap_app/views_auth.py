from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import UserAccount, AdminAccount, Wallet, Notification

def login_view(request):
    """
    Trang đăng nhập thống nhất, tự động nhận diện vai trò tài khoản:
    - Nếu là Quản trị viên (Admin) -> Chuyển hướng về Cổng Quản trị (/admin-portal/)
    - Nếu là Người dùng cá nhân (User) -> Chuyển hướng về Dashboard cá nhân (/)
    """
    if request.session.get('user_id'):
        return redirect('dashboard')
    if request.session.get('admin_id'):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            messages.error(request, "Vui lòng nhập đầy đủ tài khoản/email và mật khẩu.")
            return render(request, 'cointap/auth/login.html', {'identifier': identifier})

        # 1. Kiểm tra tài khoản Quản trị viên (AdminAccount) trước
        admin = AdminAccount.objects.filter(username=identifier).first()
        if admin and admin.password_hash == password:
            request.session.flush()
            request.session['admin_id'] = admin.id
            request.session['admin_name'] = admin.full_name
            request.session['admin_role'] = admin.role
            messages.success(request, f"Chào mừng Quản trị viên {admin.full_name} ({admin.role})!")
            return redirect('admin_dashboard')

        # 2. Kiểm tra tài khoản Người dùng cá nhân (UserAccount)
        user = UserAccount.objects.filter(email=identifier).first()
        if not user:
            user = UserAccount.objects.filter(full_name__iexact=identifier).first()

        if user and user.password_hash == password:
            request.session.flush()
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.full_name
            messages.success(request, f"Xin chào {user.full_name}, đăng nhập thành công!")
            return redirect('dashboard')

        # 3. Nếu không trùng khớp bất kỳ tài khoản nào
        messages.error(request, "Tài khoản/email hoặc mật khẩu không chính xác.")
        return render(request, 'cointap/auth/login.html', {'identifier': identifier})

    return render(request, 'cointap/auth/login.html')


def quick_login_view(request, role, target_id):
    """
    Hỗ trợ đăng nhập nhanh 1-click cho giảng viên / người chấm đồ án / kiểm thử.
    """
    if role == 'user':
        user = UserAccount.objects.filter(user_id=target_id).first()
        if user:
            request.session.flush()
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.full_name
            messages.success(request, f"Đã đăng nhập nhanh với tài khoản: {user.full_name}")
            return redirect('dashboard')
    elif role == 'admin':
        admin = AdminAccount.objects.filter(id=target_id).first()
        if admin:
            request.session.flush()
            request.session['admin_id'] = admin.id
            request.session['admin_name'] = admin.full_name
            request.session['admin_role'] = admin.role
            messages.success(request, f"Đã đăng nhập nhanh quản trị viên: {admin.full_name} ({admin.role})")
            return redirect('admin_dashboard')

    messages.error(request, "Tài khoản không tồn tại.")
    return redirect('login')


def register_view(request):
    """
    Trang đăng ký tài khoản người dùng mới. Tự động khởi tạo ví mặc định.
    """
    if request.session.get('user_id'):
        return redirect('dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not full_name or not email or not password:
            messages.error(request, "Vui lòng nhập đầy đủ họ tên, email và mật khẩu.")
            return render(request, 'cointap/auth/register.html')

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return render(request, 'cointap/auth/register.html')

        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, "Địa chỉ email này đã được đăng ký tài khoản.")
            return render(request, 'cointap/auth/register.html')

        # Tạo người dùng mới
        new_user = UserAccount.objects.create(
            full_name=full_name,
            email=email,
            password_hash=password,
            created_at=timezone.now()
        )

        # Tự động tạo Ví Tiền Mặt ban đầu
        Wallet.objects.create(
            user=new_user,
            wallet_name="Ví Tiền Mặt",
            wallet_type="CASH",
            balance=0,
            icon="payments",
            color="#10B981",
            is_active=True
        )

        # Gửi thông báo chào mừng
        Notification.objects.create(
            user=new_user,
            title="Chào mừng bạn đến với CoinTap!",
            content="Tài khoản của bạn đã được khởi tạo thành công. Bắt đầu ghi chép các khoản chi tiêu đầu tiên nhé!",
            type="SYSTEM"
        )

        # Đăng nhập trực tiếp
        request.session['user_id'] = new_user.user_id
        request.session['user_name'] = new_user.full_name
        messages.success(request, "Đăng ký tài khoản thành công! Chào mừng bạn gia nhập CoinTap.")
        return redirect('dashboard')

    return render(request, 'cointap/auth/register.html')


def logout_view(request):
    """
    Đăng xuất khỏi hệ thống và xóa sạch session.
    """
    request.session.flush()
    messages.info(request, "Bạn đã đăng xuất an toàn khỏi CoinTap.")
    return redirect('login')


def profile_view(request):
    """
    Xem và cập nhật thông tin cá nhân và đổi mật khẩu.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            if full_name:
                user.full_name = full_name
            if email and email != user.email:
                if UserAccount.objects.filter(email=email).exclude(user_id=user.user_id).exists():
                    messages.error(request, "Email này đã được sử dụng bởi tài khoản khác.")
                else:
                    user.email = email
            user.save()
            request.session['user_name'] = user.full_name
            messages.success(request, "Đã cập nhật thông tin hồ sơ thành công.")

        elif action == 'change_password':
            old_pwd = request.POST.get('old_password', '').strip()
            new_pwd = request.POST.get('new_password', '').strip()
            confirm_pwd = request.POST.get('confirm_password', '').strip()

            if user.password_hash != old_pwd:
                messages.error(request, "Mật khẩu hiện tại không đúng.")
            elif new_pwd != confirm_pwd:
                messages.error(request, "Mật khẩu xác nhận không khớp.")
            elif len(new_pwd) < 6:
                messages.error(request, "Mật khẩu mới phải có tối thiểu 6 ký tự.")
            else:
                user.password_hash = new_pwd
                user.save()
                messages.success(request, "Đổi mật khẩu thành công!")

    return render(request, 'cointap/auth/profile.html', {
        'user': user,
    })

