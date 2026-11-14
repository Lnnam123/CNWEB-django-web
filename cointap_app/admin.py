from django.contrib import admin
from .models import (
    UserAccount, AdminAccount, Wallet, Category,
    Transaction, Budget, Notification, AIConversation, AIChatMessage
)

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'email', 'created_at')
    search_fields = ('full_name', 'email')
    ordering = ('-created_at',)

@admin.register(AdminAccount)
class AdminAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'full_name', 'role', 'created_at')
    search_fields = ('username', 'full_name')
    list_filter = ('role',)
    ordering = ('id',)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet_id', 'wallet_name', 'user', 'wallet_type', 'balance', 'is_active')
    list_filter = ('wallet_type', 'is_active')
    search_fields = ('wallet_name', 'user__full_name', 'user__email')
    ordering = ('user', '-balance')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'type', 'user', 'icon', 'color', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'user__full_name')
    ordering = ('type', 'name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'type', 'amount', 'wallet', 'category', 'transaction_date')
    list_filter = ('type', 'transaction_date')
    search_fields = ('note', 'user__full_name', 'wallet__wallet_name', 'category__name')
    ordering = ('-transaction_date',)
    date_hierarchy = 'transaction_date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('budget_id', 'user', 'category', 'amount', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('user__full_name', 'category__name')
    ordering = ('-start_date',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'user', 'title', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('title', 'content', 'user__full_name')
    ordering = ('-created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'title', 'created_at', 'updated_at')
    search_fields = ('session_id', 'title', 'user__full_name')
    ordering = ('-updated_at',)

@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'conversation', 'user', 'is_user', 'created_at')
    list_filter = ('is_user',)
    search_fields = ('content', 'conversation__title', 'user__full_name')
    ordering = ('-created_at',)
