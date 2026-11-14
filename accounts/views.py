from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Xác thực email và password
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')  # Chuyển về trang chủ sau khi đăng nhập
        else:
            messages.error(request, 'Email hoặc mật khẩu không chính xác!')
            return redirect('login')

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công!')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def register(request):
    return render(request, 'accounts/register.html')

def forgotPassword(request):
    return render(request, 'accounts/forgotPassword.html')
