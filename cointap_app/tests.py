from django.test import TestCase, Client
from decimal import Decimal
from cointap_app.models import UserAccount, AdminAccount, Wallet, Category, Transaction, Budget
from cointap_app.services_ai import generate_ai_financial_response
from cointap_app.templatetags.cointap_tags import vnd

class CoinTapTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserAccount.objects.create(
            full_name="Nguyễn Văn A",
            email="testuser@cointap.vn",
            password_hash="password123"
        )
        self.admin = AdminAccount.objects.create(
            username="testadmin",
            password_hash="admin123",
            full_name="Admin Test",
            role="Super Admin"
        )
        self.wallet1 = Wallet.objects.create(
            user=self.user,
            wallet_name="Ví Tiền Mặt",
            wallet_type="CASH",
            balance=Decimal('1000000.00'),
            is_active=True
        )
        self.wallet2 = Wallet.objects.create(
            user=self.user,
            wallet_name="Ví Ngân Hàng",
            wallet_type="BANK",
            balance=Decimal('500000.00'),
            is_active=True
        )
        self.cat_expense = Category.objects.create(
            name="Ăn uống",
            type="EXPENSE",
            icon="restaurant"
        )
        self.cat_income = Category.objects.create(
            name="Lương",
            type="INCOME",
            icon="attach_money"
        )

    def test_login_flow(self):
        # 1. Đăng nhập Người dùng -> trỏ về trang Dashboard người dùng (/)
        resp = self.client.post('/login/', {
            'identifier': 'testuser@cointap.vn',
            'password': 'password123'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')
        self.assertEqual(self.client.session.get('user_id'), self.user.user_id)

    def test_admin_login_flow(self):
        # 2. Đăng nhập Quản trị viên -> trỏ về trang Quản trị (/admin-portal/)
        resp = self.client.post('/login/', {
            'identifier': 'testadmin',
            'password': 'admin123'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/admin-portal/')
        self.assertEqual(self.client.session.get('admin_id'), self.admin.id)

    def test_wallet_transfer(self):
        # Thiết lập session
        session = self.client.session
        session['user_id'] = self.user.user_id
        session.save()

        # Chuyển 200,000₫ từ ví 1 sang ví 2
        resp = self.client.post('/wallets/transfer/', {
            'source_wallet_id': self.wallet1.wallet_id,
            'target_wallet_id': self.wallet2.wallet_id,
            'amount': '200000',
            'note': 'Chuyển tiền tiết kiệm'
        })
        self.assertEqual(resp.status_code, 302)

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('800000.00'))
        self.assertEqual(self.wallet2.balance, Decimal('700000.00'))

    def test_transaction_creation_and_balance_update(self):
        session = self.client.session
        session['user_id'] = self.user.user_id
        session.save()

        # Tạo giao dịch chi tiêu 150,000₫
        resp = self.client.post('/transactions/create/', {
            'type': 'EXPENSE',
            'amount': '150000',
            'wallet_id': self.wallet1.wallet_id,
            'category_id': self.cat_expense.category_id,
            'note': 'Ăn tối lẩu'
        })
        self.assertEqual(resp.status_code, 302)

        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('850000.00'))

    def test_ai_advisor_generation(self):
        response_text = generate_ai_financial_response("Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?", self.user)
        self.assertIn("Nguyễn Văn A", response_text)
        self.assertIn("ngày", response_text)

    def test_admin_portal_access(self):
        session = self.client.session
        session['admin_id'] = self.admin.id
        session['admin_name'] = self.admin.full_name
        session['admin_role'] = self.admin.role
        session.save()

        resp = self.client.get('/admin-portal/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dashboard Quản Trị Hệ Thống")

    def test_vnd_formatting_filter(self):
        self.assertEqual(vnd(2543000), "2.543.000")
        self.assertEqual(vnd(-50000), "-50.000")
        self.assertEqual(vnd(4314000), "4.314.000")
        self.assertEqual(vnd("1000000"), "1.000.000")
        self.assertEqual(vnd(0), "0")

    def test_transaction_creation_with_dot_input(self):
        session = self.client.session
        session['user_id'] = self.user.user_id
        session.save()

        # Người dùng nhập số tiền có dấu chấm phân cách hàng nghìn (50.000)
        resp = self.client.post('/transactions/create/', {
            'type': 'EXPENSE',
            'amount': '50.000',
            'wallet_id': self.wallet1.wallet_id,
            'category_id': self.cat_expense.category_id,
            'note': 'Ăn phở'
        })
        self.assertEqual(resp.status_code, 302)

        self.wallet1.refresh_from_db()
        # Số dư ban đầu 1.000.000 - 50.000 = 950.000 (không phải 999.950)
        self.assertEqual(self.wallet1.balance, Decimal('950000.00'))
