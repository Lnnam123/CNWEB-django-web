from .models import UserAccount, AdminAccount, Notification, Wallet

def cointap_context(request):
    """
    Context processor cung cấp thông tin người dùng / admin, 
    thông báo chưa đọc và danh sách ví trên toàn bộ giao diện template.
    """
    user_id = request.session.get('user_id')
    admin_id = request.session.get('admin_id')
    
    current_user = None
    current_admin = None
    unread_notifications_count = 0
    recent_notifications = []
    user_wallets = []
    
    if user_id:
        try:
            current_user = UserAccount.objects.get(user_id=user_id)
            unread_notifications_count = Notification.objects.filter(user=current_user, is_read=False).count()
            recent_notifications = Notification.objects.filter(user=current_user).order_by('-created_at')[:5]
            user_wallets = Wallet.objects.filter(user=current_user, is_active=True).order_by('-balance')
        except UserAccount.DoesNotExist:
            request.session.pop('user_id', None)
            
    if admin_id:
        try:
            current_admin = AdminAccount.objects.get(id=admin_id)
        except AdminAccount.DoesNotExist:
            request.session.pop('admin_id', None)
            
    return {
        'current_user': current_user,
        'current_admin': current_admin,
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
        'user_wallets': user_wallets,
    }

