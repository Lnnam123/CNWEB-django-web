from django.urls import path
from . import (
    views_auth,
    views_dashboard,
    views_wallets,
    views_transactions,
    views_budgets,
    views_reports,
    views_assistant,
    views_notifications,
    views_admin,
)

urlpatterns = [
    # 1. Trang chủ / Dashboard người dùng
    path('', views_dashboard.dashboard_view, name='dashboard'),

    # 2. Xác thực tài khoản
    path('login/', views_auth.login_view, name='login'),
    path('login/quick/<str:role>/<int:target_id>/', views_auth.quick_login_view, name='quick_login'),
    path('register/', views_auth.register_view, name='register'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('profile/', views_auth.profile_view, name='profile'),

    # 3. Quản lý Ví tiền (Wallets)
    path('wallets/', views_wallets.wallets_list_view, name='wallets_list'),
    path('wallets/create/', views_wallets.wallet_create_view, name='wallet_create'),
    path('wallets/<int:wallet_id>/edit/', views_wallets.wallet_edit_view, name='wallet_edit'),
    path('wallets/<int:wallet_id>/delete/', views_wallets.wallet_delete_view, name='wallet_delete'),
    path('wallets/transfer/', views_wallets.wallet_transfer_view, name='wallet_transfer'),

    # 4. Giao dịch Thu - Chi (Transactions)
    path('transactions/', views_transactions.transactions_list_view, name='transactions_list'),
    path('transactions/create/', views_transactions.transaction_create_view, name='transaction_create'),
    path('transactions/<int:transaction_id>/edit/', views_transactions.transaction_edit_view, name='transaction_edit'),
    path('transactions/<int:transaction_id>/delete/', views_transactions.transaction_delete_view, name='transaction_delete'),
    path('transactions/export-csv/', views_transactions.transactions_export_csv, name='transactions_export_csv'),

    # 5. Hạn mức Ngân sách (Budgets)
    path('budgets/', views_budgets.budgets_list_view, name='budgets_list'),
    path('budgets/create/', views_budgets.budget_create_view, name='budget_create'),
    path('budgets/<int:budget_id>/edit/', views_budgets.budget_edit_view, name='budget_edit'),
    path('budgets/<int:budget_id>/delete/', views_budgets.budget_delete_view, name='budget_delete'),

    # 6. Danh mục (Categories)
    path('categories/', views_budgets.categories_list_view, name='categories_list'),
    path('categories/create/', views_budgets.category_create_view, name='category_create'),
    path('categories/<int:category_id>/delete/', views_budgets.category_delete_view, name='category_delete'),

    # 7. Báo cáo & Thống kê tài chính (Reports)
    path('reports/', views_reports.reports_view, name='reports'),

    # 8. Trợ lý Cố vấn AI (CoinTap AI Assistant)
    path('ai-assistant/', views_assistant.ai_assistant_view, name='ai_assistant'),
    path('ai-assistant/new/', views_assistant.ai_new_session_view, name='ai_new_session'),
    path('ai-assistant/<str:session_id>/delete/', views_assistant.ai_delete_session_view, name='ai_delete_session'),
    path('api/ai-chat/', views_assistant.ai_chat_api, name='ai_chat_api'),

    # 9. Trung tâm Thông báo (Notifications)
    path('notifications/', views_notifications.notifications_list_view, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views_notifications.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views_notifications.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views_notifications.notification_delete_view, name='notification_delete'),

    # 10. Cổng Quản Trị Hệ Thống (Admin Portal)
    path('admin-portal/', views_admin.admin_dashboard_view, name='admin_dashboard'),
    path('admin-portal/users/', views_admin.admin_users_view, name='admin_users'),
    path('admin-portal/users/<int:user_id>/delete/', views_admin.admin_user_delete_view, name='admin_user_delete'),
    path('admin-portal/admins/', views_admin.admin_admins_view, name='admin_admins'),
    path('admin-portal/admins/<int:admin_id>/delete/', views_admin.admin_admin_delete_view, name='admin_admin_delete'),
    path('admin-portal/categories/', views_admin.admin_categories_view, name='admin_categories'),
    path('admin-portal/categories/<int:category_id>/delete/', views_admin.admin_category_delete_view, name='admin_category_delete'),
    path('admin-portal/ai-logs/', views_admin.admin_ai_logs_view, name='admin_ai_logs'),
    path('admin-portal/broadcast/', views_admin.admin_broadcast_view, name='admin_broadcast'),
]

