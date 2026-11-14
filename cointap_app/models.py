from django.db import models
from django.utils import timezone
from decimal import Decimal

class UserAccount(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class AdminAccount(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='Administrator')
    email = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'admins'
        verbose_name = 'Quản trị viên'
        verbose_name_plural = 'Quản trị viên'

    def __str__(self):
        return f"{self.username} - {self.role}"


class Wallet(models.Model):
    WALLET_TYPES = [
        ('CASH', 'Tiền mặt'),
        ('BANK', 'Tài khoản ngân hàng'),
        ('E_WALLET', 'Ví điện tử'),
        ('SAVINGS', 'Tiết kiệm / Heo đất'),
        ('CREDIT', 'Thẻ tín dụng'),
    ]

    wallet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='wallets')
    wallet_name = models.CharField(max_length=100)
    wallet_type = models.CharField(max_length=50, choices=WALLET_TYPES, default='CASH')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    icon = models.CharField(max_length=50, default='account_balance_wallet')
    color = models.CharField(max_length=20, default='#10B981')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'wallets'
        verbose_name = 'Ví tiền'
        verbose_name_plural = 'Ví tiền'

    def __str__(self):
        return f"{self.wallet_name} - {self.balance:,.0f}₫"


class Category(models.Model):
    CATEGORY_TYPES = [
        ('EXPENSE', 'Khoản chi'),
        ('INCOME', 'Khoản thu'),
    ]

    category_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='category')
    color = models.CharField(max_length=20, default='#6366F1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'

    def __str__(self):
        prefix = '[-] ' if self.type == 'EXPENSE' else '[+] '
        return f"{prefix}{self.name}"


class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id', null=True, blank=True, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'budgets'
        verbose_name = 'Ngân sách'
        verbose_name_plural = 'Ngân sách'

    def __str__(self):
        cat_name = self.category.name if self.category else "Chung"
        return f"Ngân sách {cat_name}: {self.amount:,.0f}₫"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('EXPENSE', 'Khoản chi'),
        ('INCOME', 'Khoản thu'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, db_column='wallet_id', related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='category_id', null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-transaction_id']
        verbose_name = 'Giao dịch'
        verbose_name_plural = 'Giao dịch'

    def __str__(self):
        sign = '+' if self.type == 'INCOME' else '-'
        return f"{sign}{self.amount:,.0f}₫ - {self.note or (self.category.name if self.category else 'Giao dịch')}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('SYSTEM', 'Hệ thống'),
        ('WARNING', 'Cảnh báo'),
        ('BUDGET_ALERT', 'Cảnh báo ngân sách'),
    ]

    notification_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='notifications')
    title = models.TextField()
    content = models.TextField()
    type = models.TextField(choices=NOTIFICATION_TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'

    def __str__(self):
        return f"[{self.type}] {self.title}"


class AIConversation(models.Model):
    session_id = models.CharField(max_length=120, primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='ai_conversations')
    title = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-updated_at']
        verbose_name = 'Cuộc trò chuyện AI'
        verbose_name_plural = 'Cuộc trò chuyện AI'

    def __str__(self):
        return f"{self.title[:40]}..."


class AIChatMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, db_column='session_id', related_name='messages')
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, db_column='user_id', related_name='ai_messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_chat_messages'
        ordering = ['created_at']
        verbose_name = 'Tin nhắn AI'
        verbose_name_plural = 'Tin nhắn AI'

    def __str__(self):
        role = "User" if self.is_user else "Gemini AI"
        return f"[{role}] {self.content[:30]}..."
