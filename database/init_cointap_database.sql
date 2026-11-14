-- ============================================================================
-- COINTAP - EXPENSE MANAGEMENT & FINANCIAL AI ASSISTANT
-- Production PostgreSQL Database Initializer (Tương thích 100% Supabase & Linux Server)
-- Được trích xuất và tinh chỉnh hoàn chỉnh cho máy chủ Linux độc lập (Self-hosted)
-- ============================================================================

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

-- ============================================================================
-- 1. BẢNG USERS (Người dùng ứng dụng)
-- ============================================================================
DROP TABLE IF EXISTS "notifications" CASCADE;
DROP TABLE IF EXISTS "ai_chat_messages" CASCADE;
DROP TABLE IF EXISTS "ai_conversations" CASCADE;
DROP TABLE IF EXISTS "transactions" CASCADE;
DROP TABLE IF EXISTS "budgets" CASCADE;
DROP TABLE IF EXISTS "categories" CASCADE;
DROP TABLE IF EXISTS "wallets" CASCADE;
DROP TABLE IF EXISTS "admins" CASCADE;
DROP TABLE IF EXISTS "users" CASCADE;

CREATE TABLE "users" (
    "user_id" SERIAL PRIMARY KEY,
    "full_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. BẢNG ADMINS (Quản trị viên hệ thống)
-- ============================================================================
CREATE TABLE "admins" (
    "id" SERIAL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "role" VARCHAR(50) DEFAULT 'Administrator',
    "email" VARCHAR(150),
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 3. BẢNG WALLETS (Ví tiền / Tài khoản nguồn)
-- ============================================================================
CREATE TABLE "wallets" (
    "wallet_id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "wallet_name" VARCHAR(100) NOT NULL,
    "wallet_type" VARCHAR(50) DEFAULT 'CASH',
    "balance" NUMERIC(15, 2) DEFAULT 0.00,
    "icon" VARCHAR(50) DEFAULT 'account_balance_wallet',
    "color" VARCHAR(20) DEFAULT '#10B981',
    "is_active" BOOLEAN DEFAULT true,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. BẢNG CATEGORIES (Danh mục Thu - Chi)
-- ============================================================================
CREATE TABLE "categories" (
    "category_id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "name" VARCHAR(100) NOT NULL,
    "type" VARCHAR(20) NOT NULL, -- 'EXPENSE' hoặc 'INCOME'
    "icon" VARCHAR(50) DEFAULT 'category',
    "color" VARCHAR(20) DEFAULT '#6366F1',
    "is_active" BOOLEAN DEFAULT true,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. BẢNG BUDGETS (Kế hoạch ngân sách hạn mức)
-- ============================================================================
CREATE TABLE "budgets" (
    "budget_id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "category_id" INTEGER REFERENCES "categories"("category_id") ON DELETE CASCADE,
    "amount" NUMERIC(15, 2) NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. BẢNG TRANSACTIONS (Nhật ký giao dịch tài chính)
-- ============================================================================
CREATE TABLE "transactions" (
    "transaction_id" SERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "wallet_id" INTEGER REFERENCES "wallets"("wallet_id") ON DELETE CASCADE,
    "category_id" INTEGER REFERENCES "categories"("category_id") ON DELETE RESTRICT,
    "amount" NUMERIC(15, 2) NOT NULL,
    "type" VARCHAR(20) NOT NULL, -- 'EXPENSE' hoặc 'INCOME'
    "transaction_date" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "note" TEXT,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. BẢNG NOTIFICATIONS (Thông báo đẩy & Cảnh báo vượt ngân sách)
-- ============================================================================
CREATE TABLE "notifications" (
    "notification_id" BIGSERIAL PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "type" TEXT NOT NULL, -- 'SYSTEM', 'WARNING', 'BUDGET_ALERT'
    "is_read" BOOLEAN DEFAULT false,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 8. BẢNG AI_CONVERSATIONS & AI_CHAT_MESSAGES (Trợ lý tài chính AI)
-- ============================================================================
CREATE TABLE "ai_conversations" (
    "session_id" TEXT PRIMARY KEY,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "title" TEXT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE "ai_chat_messages" (
    "message_id" BIGSERIAL PRIMARY KEY,
    "session_id" TEXT REFERENCES "ai_conversations"("session_id") ON DELETE CASCADE,
    "user_id" INTEGER REFERENCES "users"("user_id") ON DELETE CASCADE,
    "content" TEXT NOT NULL,
    "is_user" BOOLEAN DEFAULT true NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 9. TRIGGER CẬP NHẬT TỰ ĐỘNG SỐ DƯ VÍ KHI THÊM/SỬA/XÓA GIAO DỊCH
-- ============================================================================
CREATE OR REPLACE FUNCTION update_wallet_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Xử lý khi XÓA giao dịch (DELETE)
    IF TG_OP = 'DELETE' THEN
        IF OLD.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE wallet_id = OLD.wallet_id;
        ELSIF OLD.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance + OLD.amount WHERE wallet_id = OLD.wallet_id;
        END IF;
        RETURN OLD;
    END IF;

    -- Xử lý khi SỬA giao dịch (UPDATE)
    IF TG_OP = 'UPDATE' THEN
        -- Hoàn lại tiền giao dịch cũ
        IF OLD.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE wallet_id = OLD.wallet_id;
        ELSIF OLD.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance + OLD.amount WHERE wallet_id = OLD.wallet_id;
        END IF;
        -- Áp dụng tiền giao dịch mới
        IF NEW.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance + NEW.amount WHERE wallet_id = NEW.wallet_id;
        ELSIF NEW.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance - NEW.amount WHERE wallet_id = NEW.wallet_id;
        END IF;
        RETURN NEW;
    END IF;

    -- Xử lý khi THÊM MỚI giao dịch (INSERT)
    IF TG_OP = 'INSERT' THEN
        IF NEW.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance + NEW.amount WHERE wallet_id = NEW.wallet_id;
        ELSIF NEW.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance - NEW.amount WHERE wallet_id = NEW.wallet_id;
        END IF;
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_wallet_balance_insert ON transactions;
CREATE TRIGGER trg_wallet_balance_insert
AFTER INSERT ON transactions
FOR EACH ROW EXECUTE FUNCTION update_wallet_balance();

DROP TRIGGER IF EXISTS trg_wallet_balance_update ON transactions;
CREATE TRIGGER trg_wallet_balance_update
AFTER UPDATE ON transactions
FOR EACH ROW EXECUTE FUNCTION update_wallet_balance();

DROP TRIGGER IF EXISTS trg_wallet_balance_delete ON transactions;
CREATE TRIGGER trg_wallet_balance_delete
AFTER DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION update_wallet_balance();

-- Tạm thời vô hiệu hoá trigger khi nạp dữ liệu ban đầu từ Supabase (để số dư ví giữ nguyên đúng thực tế)
ALTER TABLE transactions DISABLE TRIGGER trg_wallet_balance_insert;

-- ============================================================================
-- 10. DỮ LIỆU SAO CHÉP TOÀN BỘ TỪ SUPABASE
-- ============================================================================

-- Dữ liệu users
INSERT INTO "users" ("user_id", "full_name", "email", "password_hash", "created_at") VALUES 
(6, 'Nam', 'nhatnam28062006@gmail.com', 'Lnnam286@', '2026-08-30 16:10:30'),
(7, 'quan', 'leq118157@gmail.com', '123456', '2026-08-30 18:59:26'),
(8, 'Tiểu Màn Thầu', 'ggwn021@gmail.com', 'thaoMinh11', '2026-08-31 05:36:14');

-- Dữ liệu admins
INSERT INTO "admins" ("id", "username", "password_hash", "full_name", "role", "email", "created_at", "updated_at") VALUES 
(1, 'admin', 'Lnnam123@', 'admin', 'Super Admin', 'admin@cointap.vn', '2026-09-06 13:08:41+07', '2026-09-06 14:35:18+07'),
(2, 'nhatnam286', 'Lnnam123@', 'Lê Nhật Nam', 'Administrator', 'nhatnam286@cointap.vn', '2026-09-06 13:31:30+07', '2026-09-06 14:02:26+07');

-- Dữ liệu wallets
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES 
(1, 6, 'VCB', 'BANK', 2543000.00, 'credit_card', '#10B981', true, '2026-08-30 16:10:30'),
(2, 7, 'Ví Tiền Mặt', 'CASH', -100000.00, 'payments', '#10B981', true, '2026-08-30 18:59:26'),
(3, 7, 'hahaha', 'CASH', 9640000.00, 'savings', '#10B981', true, '2026-08-30 19:00:12'),
(4, 6, 'Tiền mặt', 'BANK', 0.00, 'account_balance_wallet', '#EF4444', false, '2026-08-30 19:05:03'),
(5, 8, 'Heo Đất', 'CASH', 3575000.00, 'savings', '#10B981', true, '2026-08-31 05:36:14');

-- Dữ liệu categories
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES 
(1, NULL, 'Ăn uống', 'EXPENSE', 'restaurant', '#F59E0B', true, '2026-08-30 15:55:07'),
(2, NULL, 'Di chuyển', 'EXPENSE', 'directions_car', '#004AC6', true, '2026-08-30 15:55:07'),
(3, NULL, 'Mua sắm', 'EXPENSE', 'shopping_bag', '#E91E63', true, '2026-08-30 15:55:07'),
(4, NULL, 'Lương', 'INCOME', 'attach_money', '#4CAF50', true, '2026-08-30 15:55:07'),
(5, NULL, 'Thu nhập phụ', 'INCOME', 'more_time', '#8BC34A', true, '2026-08-30 15:55:07'),
(6, 6, 'Game', 'EXPENSE', 'sports_esports', '#10B981', true, '2026-08-30 16:15:19'),
(7, 6, 'Trọ', 'EXPENSE', 'home', '#14B8A6', true, '2026-08-31 19:20:01'),
(8, 6, 'Khác', 'EXPENSE', 'shopping_cart', '#EC4899', true, '2026-09-05 13:49:19'),
(9, NULL, 'Hoá đơn', 'EXPENSE', 'receipt_long', '#06B6D4', true, '2026-09-06 13:19:34');

-- Dữ liệu budgets
INSERT INTO "budgets" ("budget_id", "user_id", "amount", "start_date", "end_date", "created_at", "category_id") VALUES 
(12, 6, 1000000.00, '2026-08-01', '2026-08-31', '2026-08-31 08:29:14', 1),
(13, 6, 300000.00, '2026-08-01', '2026-08-31', '2026-08-31 08:29:28', 2),
(14, 6, 1800000.00, '2026-09-01', '2026-09-30', '2026-08-31 19:21:10', 7);

-- Dữ liệu transactions
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES 
(1, 6, 1, 1, 40000.00, 'EXPENSE', '2026-08-30 23:55:44', 'Phở', '2026-08-30 16:56:13'),
(2, 6, 1, 6, 85000.00, 'EXPENSE', '2026-08-31 00:28:15', 'Thẻ tháng genshin', '2026-08-30 17:28:50'),
(3, 6, 1, 6, 200000.00, 'EXPENSE', '2026-08-31 01:48:42', 'Nạp Liên Quân Mobile', '2026-08-30 18:49:21'),
(4, 7, 2, 1, 100000.00, 'EXPENSE', '2026-08-31 02:00:40', 'Ăn uống', '2026-08-30 19:00:49'),
(5, 7, 3, 1, 360000.00, 'EXPENSE', '2026-08-31 02:00:58', 'Ăn uống', '2026-08-30 19:01:19'),
(6, 6, 1, 1, 20000.00, 'EXPENSE', '2026-08-31 02:05:05', 'Mỳ tôm', '2026-08-30 19:05:16'),
(7, 6, 4, 2, 30000.00, 'EXPENSE', '2026-08-31 02:05:34', 'Grab', '2026-08-30 19:05:57'),
(8, 8, 5, 1, 25000.00, 'EXPENSE', '2026-08-31 12:37:10', 'mixue', '2026-08-31 05:37:22'),
(9, 6, 1, 1, 17000.00, 'EXPENSE', '2026-08-31 12:39:48', 'Mixue (Trà Xanh Chanh)', '2026-08-31 05:40:33'),
(10, 6, 1, 1, 35000.00, 'EXPENSE', '2026-08-31 12:40:35', 'Bún Giò Heo', '2026-08-31 05:40:47'),
(11, 6, 4, 1, 10000.00, 'EXPENSE', '2026-08-31 14:46:21', 'Sting', '2026-08-31 07:47:05'),
(12, 6, 1, 4, 300000.00, 'INCOME', '2026-08-31 15:36:10', 'Luong', '2026-08-31 08:36:31'),
(13, 6, 1, 3, 1000000.00, 'EXPENSE', '2026-08-31 15:50:41', 'Bàn phím cơ', '2026-08-31 08:51:02'),
(15, 6, 1, 1, 400000.00, 'EXPENSE', '2026-08-31 22:15:42', 'Lẩu Thái', '2026-08-31 15:15:59'),
(17, 6, 1, 1, 30000.00, 'EXPENSE', '2026-09-01 13:07:24', 'Cơm', '2026-09-01 06:07:46'),
(18, 6, 1, 1, 10000.00, 'EXPENSE', '2026-09-01 13:07:48', 'Nước', '2026-09-01 06:08:03'),
(19, 6, 1, 1, 42000.00, 'EXPENSE', '2026-09-01 17:28:29', 'Bún đậu mắm tôm', '2026-09-01 10:28:51'),
(20, 6, 1, 3, 54000.00, 'EXPENSE', '2026-09-02 12:56:14', 'Nước  + Sunlight + Mỳ tôm', '2026-09-02 05:56:57'),
(22, 6, 1, 5, 4000000.00, 'INCOME', '2026-09-02 21:46:16', 'tro', '2026-09-02 14:46:34'),
(23, 6, 1, 7, 1800000.00, 'EXPENSE', '2026-09-02 21:46:36', 'Tiền đóng trọ', '2026-09-02 14:46:52'),
(24, 6, 1, 1, 127000.00, 'EXPENSE', '2026-09-03 00:58:29', 'Gà ủ muối', '2026-09-02 17:58:45'),
(25, 6, 1, 1, 70000.00, 'EXPENSE', '2026-09-03 19:38:14', 'Hủ tiếu + nước + bánh', '2026-09-03 12:38:36'),
(26, 6, 1, 2, 30000.00, 'EXPENSE', '2026-09-05 20:20:45', 'Xăng', '2026-09-05 13:20:58'),
(27, 6, 1, 8, 50000.00, 'EXPENSE', '2026-09-04 18:00:00', 'Cắt tóc', '2026-09-05 13:48:43'),
(28, 6, 1, 1, 30000.00, 'EXPENSE', '2026-09-05 19:07:00', 'Hủ tiếu', '2026-09-05 14:15:29'),
(29, 6, 1, 1, 39000.00, 'EXPENSE', '2026-09-06 07:49:11', 'Soda Dâu Tây', '2026-09-06 00:49:35'),
(30, 6, 1, 1, 25000.00, 'EXPENSE', '2026-09-06 13:25:52', 'cơm', '2026-09-06 06:26:08'),
(31, 6, 1, 1, 35000.00, 'EXPENSE', '2026-09-06 17:42:13', 'Hủ tiếu Giò', '2026-09-06 10:42:26'),
(32, 6, 1, 1, 25000.00, 'EXPENSE', '2026-09-06 17:42:28', 'Bánh Gạo', '2026-09-06 10:42:39'),
(33, 6, 1, 3, 35000.00, 'EXPENSE', '2026-09-06 20:05:23', 'Áo mưa', '2026-09-06 13:05:35'),
(34, 6, 1, 1, 50000.00, 'EXPENSE', '2026-09-07 17:25:08', 'Hủ tiếu', '2026-09-07 10:25:17'),
(35, 6, 1, 1, 25000.00, 'EXPENSE', '2026-09-07 12:00:00', 'Cơm', '2026-09-07 10:25:44');

-- Kích hoạt lại Trigger sau khi nạp xong dữ liệu gốc
ALTER TABLE transactions ENABLE TRIGGER trg_wallet_balance_insert;

-- Dữ liệu notifications
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES 
(1, 6, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', true, '2026-08-30 16:10:30+07'),
(2, 8, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', true, '2026-08-31 05:36:14+07'),
(3, 6, 'Cập nhật ứng dụng', 'Phiên bản mới 1.3.0 đã sẵn sàng. Cập nhật ngay để trải nghiệm các tính năng mới!', 'SYSTEM', true, '2026-08-31 16:43:55+07'),
(4, 6, 'Vượt ngân sách: Ăn uống', 'Bạn đã chi tiêu vượt quá hạn mức ngân sách Ăn uống trong tháng này.', 'WARNING', true, '2026-08-31 18:33:24+07'),
(5, 6, 'Ngân sách Trọ sắp hết', 'Bạn đã tiêu vượt quá ngân sách Trọ tháng này. Hãy điều chỉnh chi tiêu!', 'BUDGET_ALERT', true, '2026-09-02 14:58:41+07'),
(6, 7, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', true, '2026-08-30 18:59:26+07');

-- Dữ liệu ai_conversations
INSERT INTO "ai_conversations" ("session_id", "user_id", "title", "created_at", "updated_at") VALUES 
('session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', '2026-09-05 23:26:33+07', '2026-09-05 23:41:26+07'),
('session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', '2026-09-06 12:49:36+07', '2026-09-06 12:49:59+07'),
('session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', '2026-09-06 21:46:53+07', '2026-09-06 23:32:49+07');

-- Dữ liệu ai_chat_messages
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES 
(19, 'session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', true, '2026-09-05 23:26:33+07'),
(20, 'session_1788625593214', 6, 'Chưa, tổng chi tiêu tháng 9 của bạn **chưa vượt hạn mức** ngân sách! ✅\n\n**Tình hình ngân sách các danh mục:**\n•  **Trọ**: đã chi **1.800.000đ** / **1.800.000đ** (100%) - **An toàn**\n•  **Ăn uống**: đã chi **522.000đ** / **1.000.000đ** (52%) - **An toàn** (còn lại **478.000đ**)\n•  **Di chuyển**: đã chi **30.000đ** / **300.000đ** (10%) - **An toàn** (còn lại **270.000đ**)\n•  **Tổng chi tiêu thực tế tháng này**: **2.243.000đ** (trên tổng thu nhập **4.000.000đ**)\n\nNếu bạn muốn, mình có thể phân tích tiếp:\n•  **dự báo tốc độ chi tiêu danh mục Ăn uống** đến cuối tháng\n•  **gợi ý kế hoạch tiết kiệm** từ số tiền dư còn lại\n•  hoặc **xem chi tiết các giao dịch gần đây** 📊', false, '2026-09-05 23:26:58+07'),
(21, 'session_1788625593214', 6, 'Xem chi tiết các giao dịch gần đây', true, '2026-09-05 23:41:20+07'),
(22, 'session_1788625593214', 6, 'Dưới đây là **danh sách các giao dịch gần đây nhất** của bạn 📋\n\n**Chi tiết các giao dịch gần đây:**\n•  **05/09**: Chi **30.000đ** - Di chuyển (Xăng)\n•  **05/09**: Chi **30.000đ** - Ăn uống (Hu Tieu)\n•  **04/09**: Chi **50.000đ** - Khác (Cat toc)\n•  **03/09**: Chi **70.000đ** - Ăn uống (Hủ tiếu + nước + bánh)\n•  **03/09**: Chi **127.000đ** - Ăn uống (Gà ủ muối)\n•  **02/09**: Chi **1.800.000đ** - Trọ (Tiền đóng trọ)\n•  **02/09**: Thu **+4.000.000đ** - Thu nhập phụ (tro)\n•  **02/09**: Chi **54.000đ** - Mua sắm (Nước + Sunlight + Mỳ tôm)\n•  **01/09**: Chi **42.000đ** - Ăn uống (Bún đậu mắm tôm)\n•  **01/09**: Chi **10.000đ** - Ăn uống (Nước)\n•  **01/09**: Chi **30.000đ** - Ăn uống (Cơm)\n•  **31/08**: Chi **400.000đ** - Ăn uống (Lẩu Thái)', false, '2026-09-05 23:41:26+07'),
(23, 'session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', true, '2026-09-06 12:49:36+07'),
(24, 'session_1788673776904', 6, 'Chi tiêu tháng 9 của bạn tăng vọt chủ yếu do khoản chi lớn **1.800.000đ cho Tiền đóng trọ** (chiếm gần 79% tổng chi tiêu tháng) 🏠\n\n**Chi tiết phân tích chi tiêu tháng này:**\n•  **Khoản chi lớn nhất:** Tiền đóng trọ **1.800.000đ** phát sinh vào ngày 02/09.\n•  **Chi tiêu sinh hoạt:** Tổng cộng **482.000đ** cho các nhu cầu hàng ngày, bao gồm **Ăn uống** (**309.000đ**), **Mua sắm** (**93.000đ**), **Khác** (**50.000đ**) và **Di chuyển** (**30.000đ**).\n•  **Tổng chi tiêu hiện tại:** **2.282.000đ** trên tổng thu nhập **4.000.000đ**.', false, '2026-09-06 12:49:59+07'),
(25, 'session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', true, '2026-09-06 21:46:53+07'),
(26, 'session_1788706013188', 6, 'Để quản lý tài chính an toàn trong 25 ngày còn lại của tháng 9, anh Nam nên chi tiêu tối đa khoảng **104.000đ/ngày** 💡\n\n**Cơ sở tính toán chi tiết:**\n•  **Số dư tài sản hiện tại:** **2.618.000đ** (Ví VCB).\n•  **Thời gian còn lại trong tháng:** **25 ngày** (từ 6/9 đến 30/9).\n•  **Hạn mức theo tổng số dư khả dụng:** Tối đa **104.700đ/ngày**.\n•  **Hạn mức khuyến nghị:** Duy trì mức **64.000đ/ngày** để giữ khoản tích lũy an toàn.', false, '2026-09-06 21:47:48+07'),
(27, 'session_1788706013188', 6, 'Mẹo cắt giảm các khoản chi vặt không cần thiết', true, '2026-09-06 23:32:01+07'),
(28, 'session_1788706013188', 6, 'Chào anh Nam, việc kiểm soát các khoản chi vặt như **đồ uống, ăn vặt và đồ dùng mua đột xuất** sẽ giúp anh tiết kiệm ngay từ **300.000đ - 500.000đ mỗi tháng** 💡\n\n**Các mẹo cắt giảm chi vặt hiệu quả:**\n•  **Kiểm soát món ăn kèm và nước uống:** Soda Dâu Tây (39.000đ), Bánh Gạo (25.000đ) khi cộng dồn chiếm tỷ trọng đáng kể.\n•  **Áp dụng quy tắc "Dừng 5 giây":** Tự hỏi bản thân khoản này là "Thực sự cần" hay chỉ là "Sở thích bộc phát".\n•  **Theo dõi sát hạn mức Ăn uống:** Danh mục Ăn uống đã chi 52% hạn mức.', false, '2026-09-06 23:32:49+07');

-- ============================================================================
-- 11. ĐỒNG BỘ AUTO-INCREMENT SEQUENCES CHO CÁC BẢNG TRÊN LINUX POSTGRESQL
-- ============================================================================
SELECT setval('users_user_id_seq', COALESCE((SELECT MAX(user_id) FROM users), 1), true);
SELECT setval('admins_id_seq', COALESCE((SELECT MAX(id) FROM admins), 1), true);
SELECT setval('wallets_wallet_id_seq', COALESCE((SELECT MAX(wallet_id) FROM wallets), 1), true);
SELECT setval('categories_category_id_seq', COALESCE((SELECT MAX(category_id) FROM categories), 1), true);
SELECT setval('budgets_budget_id_seq', COALESCE((SELECT MAX(budget_id) FROM budgets), 1), true);
SELECT setval('transactions_transaction_id_seq', COALESCE((SELECT MAX(transaction_id) FROM transactions), 1), true);
SELECT setval('notifications_notification_id_seq', COALESCE((SELECT MAX(notification_id) FROM notifications), 1), true);
SELECT setval('ai_chat_messages_message_id_seq', COALESCE((SELECT MAX(message_id) FROM ai_chat_messages), 1), true);

-- HOÀN TẤT KHỞI TẠO CSDL COINTAP

