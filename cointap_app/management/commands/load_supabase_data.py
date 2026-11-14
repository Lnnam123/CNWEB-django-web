from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date
from cointap_app.models import (
    UserAccount, AdminAccount, Wallet, Category, Budget,
    Transaction, Notification, AIConversation, AIChatMessage
)

class Command(BaseCommand):
    help = 'Sao chép và đồng bộ toàn bộ dữ liệu từ Supabase Database vào cơ sở dữ liệu Django'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("==> Đang nạp dữ liệu Supabase vào CoinTap..."))

        # 1. USERS
        users_data = [
            (6, 'Nam', 'nhatnam28062006@gmail.com', 'Lnnam286@', '2026-08-30 16:10:30'),
            (7, 'quan', 'leq118157@gmail.com', '123456', '2026-08-30 18:59:26'),
            (8, 'Tiểu Màn Thầu', 'ggwn021@gmail.com', 'thaoMinh11', '2026-08-31 05:36:14'),
        ]
        for uid, name, email, pwd, created in users_data:
            UserAccount.objects.update_or_create(
                user_id=uid,
                defaults={
                    'full_name': name,
                    'email': email,
                    'password_hash': pwd,
                    'created_at': datetime.fromisoformat(created),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(users_data)} người dùng"))

        # 2. ADMINS
        admins_data = [
            (1, 'admin', 'Lnnam123@', 'admin', 'Super Admin', 'admin@cointap.vn', '2026-09-06 13:08:41', '2026-09-06 14:35:18'),
            (2, 'nhatnam286', 'Lnnam123@', 'Lê Nhật Nam', 'Administrator', 'nhatnam286@cointap.vn', '2026-09-06 13:31:30', '2026-09-06 14:02:26'),
        ]
        for aid, uname, pwd, fname, role, email, c_at, u_at in admins_data:
            AdminAccount.objects.update_or_create(
                id=aid,
                defaults={
                    'username': uname,
                    'password_hash': pwd,
                    'full_name': fname,
                    'role': role,
                    'email': email,
                    'created_at': datetime.fromisoformat(c_at),
                    'updated_at': datetime.fromisoformat(u_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(admins_data)} quản trị viên"))

        # 3. WALLETS
        wallets_data = [
            (1, 6, 'VCB', 'BANK', '2543000.00', 'credit_card', '#10B981', True, '2026-08-30 16:10:30'),
            (2, 7, 'Ví Tiền Mặt', 'CASH', '-100000.00', 'payments', '#10B981', True, '2026-08-30 18:59:26'),
            (3, 7, 'hahaha', 'CASH', '9640000.00', 'savings', '#10B981', True, '2026-08-30 19:00:12'),
            (4, 6, 'Tiền mặt', 'BANK', '0.00', 'account_balance_wallet', '#EF4444', False, '2026-08-30 19:05:03'),
            (5, 8, 'Heo Đất', 'CASH', '3575000.00', 'savings', '#10B981', True, '2026-08-31 05:36:14'),
        ]
        for wid, uid, wname, wtype, bal, icon, color, active, c_at in wallets_data:
            user = UserAccount.objects.get(user_id=uid)
            Wallet.objects.update_or_create(
                wallet_id=wid,
                defaults={
                    'user': user,
                    'wallet_name': wname,
                    'wallet_type': wtype,
                    'balance': Decimal(bal),
                    'icon': icon,
                    'color': color,
                    'is_active': active,
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(wallets_data)} ví tiền"))

        # 4. CATEGORIES
        categories_data = [
            (1, None, 'Ăn uống', 'EXPENSE', 'restaurant', '#F59E0B', True, '2026-08-30 15:55:07'),
            (2, None, 'Di chuyển', 'EXPENSE', 'directions_car', '#004AC6', True, '2026-08-30 15:55:07'),
            (3, None, 'Mua sắm', 'EXPENSE', 'shopping_bag', '#E91E63', True, '2026-08-30 15:55:07'),
            (4, None, 'Lương', 'INCOME', 'attach_money', '#4CAF50', True, '2026-08-30 15:55:07'),
            (5, None, 'Thu nhập phụ', 'INCOME', 'more_time', '#8BC34A', True, '2026-08-30 15:55:07'),
            (6, 6, 'Game', 'EXPENSE', 'sports_esports', '#10B981', True, '2026-08-30 16:15:19'),
            (7, 6, 'Trọ', 'EXPENSE', 'home', '#14B8A6', True, '2026-08-31 19:20:01'),
            (8, 6, 'Khác', 'EXPENSE', 'shopping_cart', '#EC4899', True, '2026-09-05 13:49:19'),
            (9, None, 'Hoá đơn', 'EXPENSE', 'receipt_long', '#06B6D4', True, '2026-09-06 13:19:34'),
        ]
        for cid, uid, name, ctype, icon, color, active, c_at in categories_data:
            user = UserAccount.objects.get(user_id=uid) if uid else None
            Category.objects.update_or_create(
                category_id=cid,
                defaults={
                    'user': user,
                    'name': name,
                    'type': ctype,
                    'icon': icon,
                    'color': color,
                    'is_active': active,
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(categories_data)} danh mục"))

        # 5. BUDGETS
        budgets_data = [
            (12, 6, 1, '1000000.00', '2026-08-01', '2026-08-31', '2026-08-31 08:29:14'),
            (13, 6, 2, '300000.00', '2026-08-01', '2026-08-31', '2026-08-31 08:29:28'),
            (14, 6, 7, '1800000.00', '2026-09-01', '2026-09-30', '2026-08-31 19:21:10'),
        ]
        for bid, uid, cid, amt, s_date, e_date, c_at in budgets_data:
            user = UserAccount.objects.get(user_id=uid)
            category = Category.objects.get(category_id=cid)
            Budget.objects.update_or_create(
                budget_id=bid,
                defaults={
                    'user': user,
                    'category': category,
                    'amount': Decimal(amt),
                    'start_date': date.fromisoformat(s_date),
                    'end_date': date.fromisoformat(e_date),
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(budgets_data)} hạn mức ngân sách"))

        # 6. TRANSACTIONS
        transactions_data = [
            (1, 6, 1, 1, '40000.00', 'EXPENSE', '2026-08-30 23:55:44', 'Phở', '2026-08-30 16:56:13'),
            (2, 6, 1, 6, '85000.00', 'EXPENSE', '2026-08-31 00:28:15', 'Thẻ tháng genshin', '2026-08-30 17:28:50'),
            (3, 6, 1, 6, '200000.00', 'EXPENSE', '2026-08-31 01:48:42', 'Nạp Liên Quân Mobile', '2026-08-30 18:49:21'),
            (4, 7, 2, 1, '100000.00', 'EXPENSE', '2026-08-31 02:00:40', 'Ăn uống', '2026-08-30 19:00:49'),
            (5, 7, 3, 1, '360000.00', 'EXPENSE', '2026-08-31 02:00:58', 'Ăn uống', '2026-08-30 19:01:19'),
            (6, 6, 1, 1, '20000.00', 'EXPENSE', '2026-08-31 02:05:05', 'Mỳ tôm', '2026-08-30 19:05:16'),
            (7, 6, 4, 2, '30000.00', 'EXPENSE', '2026-08-31 02:05:34', 'Grab', '2026-08-30 19:05:57'),
            (8, 8, 5, 1, '25000.00', 'EXPENSE', '2026-08-31 12:37:10', 'mixue', '2026-08-31 05:37:22'),
            (9, 6, 1, 1, '17000.00', 'EXPENSE', '2026-08-31 12:39:48', 'Mixue (Trà Xanh Chanh)', '2026-08-31 05:40:33'),
            (10, 6, 1, 1, '35000.00', 'EXPENSE', '2026-08-31 12:40:35', 'Bún Giò Heo', '2026-08-31 05:40:47'),
            (11, 6, 4, 1, '10000.00', 'EXPENSE', '2026-08-31 14:46:21', 'Sting', '2026-08-31 07:47:05'),
            (12, 6, 1, 4, '300000.00', 'INCOME', '2026-08-31 15:36:10', 'Luong', '2026-08-31 08:36:31'),
            (13, 6, 1, 3, '1000000.00', 'EXPENSE', '2026-08-31 15:50:41', 'Bàn phím cơ', '2026-08-31 08:51:02'),
            (15, 6, 1, 1, '400000.00', 'EXPENSE', '2026-08-31 22:15:42', 'Lẩu Thái', '2026-08-31 15:15:59'),
            (17, 6, 1, 1, '30000.00', 'EXPENSE', '2026-09-01 13:07:24', 'Cơm', '2026-09-01 06:07:46'),
            (18, 6, 1, 1, '10000.00', 'EXPENSE', '2026-09-01 13:07:48', 'Nước', '2026-09-01 06:08:03'),
            (19, 6, 1, 1, '42000.00', 'EXPENSE', '2026-09-01 17:28:29', 'Bún đậu mắm tôm', '2026-09-01 10:28:51'),
            (20, 6, 1, 3, '54000.00', 'EXPENSE', '2026-09-02 12:56:14', 'Nước  + Sunlight + Mỳ tôm', '2026-09-02 05:56:57'),
            (22, 6, 1, 5, '4000000.00', 'INCOME', '2026-09-02 21:46:16', 'tro', '2026-09-02 14:46:34'),
            (23, 6, 1, 7, '1800000.00', 'EXPENSE', '2026-09-02 21:46:36', 'Tiền đóng trọ', '2026-09-02 14:46:52'),
            (24, 6, 1, 1, '127000.00', 'EXPENSE', '2026-09-03 00:58:29', 'Gà ủ muối', '2026-09-02 17:58:45'),
            (25, 6, 1, 1, '70000.00', 'EXPENSE', '2026-09-03 19:38:14', 'Hủ tiếu + nước + bánh', '2026-09-03 12:38:36'),
            (26, 6, 1, 2, '30000.00', 'EXPENSE', '2026-09-05 20:20:45', 'Xăng', '2026-09-05 13:20:58'),
            (27, 6, 1, 8, '50000.00', 'EXPENSE', '2026-09-04 18:00:00', 'Cắt tóc', '2026-09-05 13:48:43'),
            (28, 6, 1, 1, '30000.00', 'EXPENSE', '2026-09-05 19:07:00', 'Hủ tiếu', '2026-09-05 14:15:29'),
            (29, 6, 1, 1, '39000.00', 'EXPENSE', '2026-09-06 07:49:11', 'Soda Dâu Tây', '2026-09-06 00:49:35'),
            (30, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-06 13:25:52', 'cơm', '2026-09-06 06:26:08'),
            (31, 6, 1, 1, '35000.00', 'EXPENSE', '2026-09-06 17:42:13', 'Hủ tiếu Giò', '2026-09-06 10:42:26'),
            (32, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-06 17:42:28', 'Bánh Gạo', '2026-09-06 10:42:39'),
            (33, 6, 1, 3, '35000.00', 'EXPENSE', '2026-09-06 20:05:23', 'Áo mưa', '2026-09-06 13:05:35'),
            (34, 6, 1, 1, '50000.00', 'EXPENSE', '2026-09-07 17:25:08', 'Hủ tiếu', '2026-09-07 10:25:17'),
            (35, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-07 12:00:00', 'Cơm', '2026-09-07 10:25:44'),
        ]
        for tid, uid, wid, cid, amt, ttype, tdate, note, c_at in transactions_data:
            user = UserAccount.objects.get(user_id=uid)
            wallet = Wallet.objects.get(wallet_id=wid)
            category = Category.objects.get(category_id=cid)
            Transaction.objects.update_or_create(
                transaction_id=tid,
                defaults={
                    'user': user,
                    'wallet': wallet,
                    'category': category,
                    'amount': Decimal(amt),
                    'type': ttype,
                    'transaction_date': datetime.fromisoformat(tdate),
                    'note': note,
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(transactions_data)} giao dịch"))

        # 7. NOTIFICATIONS
        notifs_data = [
            (1, 6, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-30 16:10:30'),
            (2, 8, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-31 05:36:14'),
            (3, 6, 'Cập nhật ứng dụng', 'Phiên bản mới 1.3.0 đã sẵn sàng. Cập nhật ngay để trải nghiệm các tính năng mới!', 'SYSTEM', True, '2026-08-31 16:43:55'),
            (4, 6, 'Vượt ngân sách: Ăn uống', 'Bạn đã chi tiêu vượt quá hạn mức ngân sách Ăn uống trong tháng này.', 'WARNING', True, '2026-08-31 18:33:24'),
            (5, 6, 'Ngân sách Trọ sắp hết', 'Bạn đã tiêu vượt quá ngân sách Trọ tháng này. Hãy điều chỉnh chi tiêu!', 'BUDGET_ALERT', True, '2026-09-02 14:58:41'),
            (6, 7, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-30 18:59:26'),
        ]
        for nid, uid, title, content, ntype, read, c_at in notifs_data:
            user = UserAccount.objects.get(user_id=uid)
            Notification.objects.update_or_create(
                notification_id=nid,
                defaults={
                    'user': user,
                    'title': title,
                    'content': content,
                    'type': ntype,
                    'is_read': read,
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(notifs_data)} thông báo"))

        # 8. AI CONVERSATIONS & MESSAGES
        convs_data = [
            ('session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', '2026-09-05 23:26:33', '2026-09-05 23:41:26'),
            ('session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', '2026-09-06 12:49:36', '2026-09-06 12:49:59'),
            ('session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', '2026-09-06 21:46:53', '2026-09-06 23:32:49'),
        ]
        for sid, uid, title, c_at, u_at in convs_data:
            user = UserAccount.objects.get(user_id=uid)
            AIConversation.objects.update_or_create(
                session_id=sid,
                defaults={
                    'user': user,
                    'title': title,
                    'created_at': datetime.fromisoformat(c_at),
                    'updated_at': datetime.fromisoformat(u_at),
                }
            )

        messages_data = [
            (19, 'session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', True, '2026-09-05 23:26:33'),
            (20, 'session_1788625593214', 6, 'Chưa, tổng chi tiêu tháng 9 của bạn **chưa vượt hạn mức** ngân sách! ✅\n\n**Tình hình ngân sách các danh mục:**\n•  **Trọ**: đã chi **1.800.000đ** / **1.800.000đ** (100%) - **An toàn**\n•  **Ăn uống**: đã chi **522.000đ** / **1.000.000đ** (52%) - **An toàn** (còn lại **478.000đ**)\n•  **Di chuyển**: đã chi **30.000đ** / **300.000đ** (10%) - **An toàn** (còn lại **270.000đ**)\n•  **Tổng chi tiêu thực tế tháng này**: **2.243.000đ** (trên tổng thu nhập **4.000.000đ**)', False, '2026-09-05 23:26:58'),
            (21, 'session_1788625593214', 6, 'Xem chi tiết các giao dịch gần đây', True, '2026-09-05 23:41:20'),
            (22, 'session_1788625593214', 6, 'Dưới đây là **danh sách các giao dịch gần đây nhất** của bạn 📋\n\n**Chi tiết các giao dịch gần đây:**\n•  **05/09**: Chi **30.000đ** - Di chuyển (Xăng)\n•  **05/09**: Chi **30.000đ** - Ăn uống (Hu Tieu)\n•  **04/09**: Chi **50.000đ** - Khác (Cat toc)\n•  **03/09**: Chi **70.000đ** - Ăn uống (Hủ tiếu + nước + bánh)\n•  **03/09**: Chi **127.000đ** - Ăn uống (Gà ủ muối)\n•  **02/09**: Chi **1.800.000đ** - Trọ (Tiền đóng trọ)', False, '2026-09-05 23:41:26'),
            (23, 'session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', True, '2026-09-06 12:49:36'),
            (24, 'session_1788673776904', 6, 'Chi tiêu tháng 9 của bạn tăng vọt chủ yếu do khoản chi lớn **1.800.000đ cho Tiền đóng trọ** (chiếm gần 79% tổng chi tiêu tháng) 🏠\n\n**Chi tiết phân tích chi tiêu tháng này:**\n•  **Khoản chi lớn nhất:** Tiền đóng trọ **1.800.000đ** phát sinh vào ngày 02/09.\n•  **Chi tiêu sinh hoạt:** Tổng cộng **482.000đ** cho các nhu cầu hàng ngày, bao gồm **Ăn uống** (**309.000đ**), **Mua sắm** (**93.000đ**), **Khác** (**50.000đ**) và **Di chuyển** (**30.000đ**).', False, '2026-09-06 12:49:59'),
            (25, 'session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', True, '2026-09-06 21:46:53'),
            (26, 'session_1788706013188', 6, 'Để quản lý tài chính an toàn trong 25 ngày còn lại của tháng 9, anh Nam nên chi tiêu tối đa khoảng **104.000đ/ngày** 💡\n\n**Cơ sở tính toán chi tiết:**\n•  **Số dư tài sản hiện tại:** **2.618.000đ** (Ví VCB).\n•  **Thời gian còn lại trong tháng:** **25 ngày** (từ 6/9 đến 30/9).\n•  **Hạn mức theo tổng số dư khả dụng:** Tối đa **104.700đ/ngày**.', False, '2026-09-06 21:47:48'),
            (27, 'session_1788706013188', 6, 'Mẹo cắt giảm các khoản chi vặt không cần thiết', True, '2026-09-06 23:32:01'),
            (28, 'session_1788706013188', 6, 'Chào anh Nam, việc kiểm soát các khoản chi vặt như **đồ uống, ăn vặt và đồ dùng mua đột xuất** sẽ giúp anh tiết kiệm ngay từ **300.000đ - 500.000đ mỗi tháng** 💡\n\n•  **Kiểm soát món ăn kèm và nước uống:** Soda Dâu Tây, Bánh Gạo...\n•  **Áp dụng quy tắc "Dừng 5 giây"**.\n•  **Theo dõi sát hạn mức Ăn uống**.', False, '2026-09-06 23:32:49'),
        ]
        for mid, sid, uid, content, is_u, c_at in messages_data:
            user = UserAccount.objects.get(user_id=uid)
            conv = AIConversation.objects.get(session_id=sid)
            AIChatMessage.objects.update_or_create(
                message_id=mid,
                defaults={
                    'conversation': conv,
                    'user': user,
                    'content': content,
                    'is_user': is_u,
                    'created_at': datetime.fromisoformat(c_at),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Đã nạp {len(convs_data)} phiên AI và {len(messages_data)} tin nhắn thoại"))
        self.stdout.write(self.style.SUCCESS("==> TOÀN BỘ DỮ LIỆU TỪ SUPABASE ĐÃ ĐƯỢC SAO CHÉP THÀNH CÔNG!"))

