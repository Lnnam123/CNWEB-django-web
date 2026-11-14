from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserAccount, Notification

def notifications_list_view(request):
    """
    Trung tâm thông báo & cảnh báo tài chính.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    return render(request, 'cointap/notifications/list.html', {
        'notifications': notifications,
    })


def notification_mark_read(request, notification_id):
    """
    Đánh dấu một thông báo là đã đọc.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    notif = get_object_or_404(Notification, notification_id=notification_id, user=user)
    notif.is_read = True
    notif.save()

    return redirect(request.META.get('HTTP_REFERER', 'notifications_list'))


def notification_mark_all_read(request):
    """
    Đánh dấu tất cả thông báo là đã đọc.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    messages.success(request, "Đã đánh dấu tất cả thông báo là đã đọc.")

    return redirect(request.META.get('HTTP_REFERER', 'notifications_list'))


def notification_delete_view(request, notification_id):
    """
    Xóa một thông báo.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    notif = get_object_or_404(Notification, notification_id=notification_id, user=user)
    notif.delete()
    messages.success(request, "Đã xóa thông báo.")

    return redirect(request.META.get('HTTP_REFERER', 'notifications_list'))

