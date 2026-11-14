-- ============================================================
-- SUPABASE DATABASE DUMP
-- Host: db.yribnkvfvpysievnhmwr.supabase.co
-- Database: postgres
-- Date: 2026-09-07 20:46:20
-- ============================================================

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- ------------------------------------------------------------
-- Cấu trúc bảng `users`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "users" CASCADE;
CREATE TABLE "users" (
    "user_id" INTEGER DEFAULT nextval('users_user_id_seq'::regclass) NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("user_id")
);

-- Dữ liệu bảng `users`
INSERT INTO "users" ("user_id", "full_name", "email", "password_hash", "created_at") VALUES (7, 'quan', 'leq118157@gmail.com', '123456', '2026-08-30 18:59:26');
INSERT INTO "users" ("user_id", "full_name", "email", "password_hash", "created_at") VALUES (8, 'Tiểu Màn Thầu', 'ggwn021@gmail.com', 'thaoMinh11', '2026-08-31 05:36:14');
INSERT INTO "users" ("user_id", "full_name", "email", "password_hash", "created_at") VALUES (6, 'Nam', 'nhatnam28062006@gmail.com', 'Lnnam286@', '2026-08-30 16:10:30');

-- ------------------------------------------------------------
-- Cấu trúc bảng `admins`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "admins" CASCADE;
CREATE TABLE "admins" (
    "id" INTEGER DEFAULT nextval('admins_id_seq'::regclass) NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "role" VARCHAR(50) DEFAULT 'Administrator'::character varying,
    "email" VARCHAR(150),
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT now(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY ("id")
);

-- Dữ liệu bảng `admins`
INSERT INTO "admins" ("id", "username", "password_hash", "full_name", "role", "email", "created_at", "updated_at") VALUES (2, 'nhatnam286', 'Lnnam123@', 'Lê Nhật Nam', 'Administrator', 'nhatnam286@cointap.vn', '2026-09-06 13:31:30', '2026-09-06 14:02:26');
INSERT INTO "admins" ("id", "username", "password_hash", "full_name", "role", "email", "created_at", "updated_at") VALUES (1, 'admin', 'Lnnam123@', 'admin', 'Super Admin', 'admin@cointap.vn', '2026-09-06 13:08:41', '2026-09-06 14:35:18');

-- ------------------------------------------------------------
-- Cấu trúc bảng `wallets`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "wallets" CASCADE;
CREATE TABLE "wallets" (
    "wallet_id" INTEGER DEFAULT nextval('wallets_wallet_id_seq'::regclass) NOT NULL,
    "user_id" INTEGER,
    "wallet_name" VARCHAR(100) NOT NULL,
    "wallet_type" VARCHAR(50) DEFAULT 'CASH'::character varying,
    "balance" NUMERIC(15, 2) DEFAULT 0.00,
    "icon" VARCHAR(50) DEFAULT 'account_balance_wallet'::character varying,
    "color" VARCHAR(20) DEFAULT '#000000'::character varying,
    "is_active" BOOLEAN DEFAULT true,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("wallet_id")
);

-- Dữ liệu bảng `wallets`
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES (2, 7, 'Ví Tiền Mặt', 'CASH', '-100000.00', 'payments', '#10B981', True, '2026-08-30 18:59:26');
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES (3, 7, 'hahaha', 'CASH', '9640000.00', 'savings', '#10B981', True, '2026-08-30 19:00:12');
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES (5, 8, 'Heo Đất', 'CASH', '3575000.00', 'savings', '#10B981', True, '2026-08-31 05:36:14');
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES (1, 6, 'VCB', 'BANK', '2543000.00', 'credit_card', '#10B981', True, '2026-08-30 16:10:30');
INSERT INTO "wallets" ("wallet_id", "user_id", "wallet_name", "wallet_type", "balance", "icon", "color", "is_active", "created_at") VALUES (4, 6, 'Tiền mặt', 'BANK', '0.00', 'account_balance_wallet', '#EF4444', False, '2026-08-30 19:05:03');

-- ------------------------------------------------------------
-- Cấu trúc bảng `categories`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "categories" CASCADE;
CREATE TABLE "categories" (
    "category_id" INTEGER DEFAULT nextval('categories_category_id_seq'::regclass) NOT NULL,
    "user_id" INTEGER,
    "name" VARCHAR(100) NOT NULL,
    "type" VARCHAR(20) NOT NULL,
    "icon" VARCHAR(50) DEFAULT 'category'::character varying,
    "color" VARCHAR(20) DEFAULT '#000000'::character varying,
    "is_active" BOOLEAN DEFAULT true,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("category_id")
);

-- Dữ liệu bảng `categories`
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (3, NULL, 'Mua sắm', 'EXPENSE', 'shopping_bag', '#E91E63', True, '2026-08-30 15:55:07');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (4, NULL, 'Lương', 'INCOME', 'attach_money', '#4CAF50', True, '2026-08-30 15:55:07');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (5, NULL, 'Thu nhập phụ', 'INCOME', 'more_time', '#8BC34A', True, '2026-08-30 15:55:07');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (1, NULL, 'Ăn uống', 'EXPENSE', 'restaurant', '#F59E0B', True, '2026-08-30 15:55:07');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (2, NULL, 'Di chuyển', 'EXPENSE', 'directions_car', '#004AC6', True, '2026-08-30 15:55:07');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (6, 6, 'Game', 'EXPENSE', 'sports_esports', '#10B981', True, '2026-08-30 16:15:19');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (7, 6, 'Trọ', 'EXPENSE', 'home', '#14B8A6', True, '2026-08-31 19:20:01');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (8, 6, 'Khác', 'EXPENSE', 'shopping_cart', '#EC4899', True, '2026-09-05 13:49:19');
INSERT INTO "categories" ("category_id", "user_id", "name", "type", "icon", "color", "is_active", "created_at") VALUES (9, NULL, 'Hoá đơn', 'EXPENSE', 'receipt_long', '#06B6D4', True, '2026-09-06 13:19:34');

-- ------------------------------------------------------------
-- Cấu trúc bảng `budgets`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "budgets" CASCADE;
CREATE TABLE "budgets" (
    "budget_id" INTEGER DEFAULT nextval('budgets_budget_id_seq'::regclass) NOT NULL,
    "user_id" INTEGER,
    "amount" NUMERIC(15, 2) NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "category_id" INTEGER,
    PRIMARY KEY ("budget_id")
);

-- Dữ liệu bảng `budgets`
INSERT INTO "budgets" ("budget_id", "user_id", "amount", "start_date", "end_date", "created_at", "category_id") VALUES (13, 6, '300000.00', '2026-08-01', '2026-08-31', '2026-08-31 08:29:28', 2);
INSERT INTO "budgets" ("budget_id", "user_id", "amount", "start_date", "end_date", "created_at", "category_id") VALUES (12, 6, '1000000.00', '2026-08-01', '2026-08-31', '2026-08-31 08:29:14', 1);
INSERT INTO "budgets" ("budget_id", "user_id", "amount", "start_date", "end_date", "created_at", "category_id") VALUES (14, 6, '1800000.00', '2026-09-01', '2026-09-30', '2026-08-31 19:21:10', 7);

-- ------------------------------------------------------------
-- Cấu trúc bảng `transactions`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "transactions" CASCADE;
CREATE TABLE "transactions" (
    "transaction_id" INTEGER DEFAULT nextval('transactions_transaction_id_seq'::regclass) NOT NULL,
    "user_id" INTEGER,
    "wallet_id" INTEGER,
    "category_id" INTEGER,
    "amount" NUMERIC(15, 2) NOT NULL,
    "type" VARCHAR(20) NOT NULL,
    "transaction_date" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "note" TEXT,
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("transaction_id")
);

-- Dữ liệu bảng `transactions`
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (1, 6, 1, 1, '40000.00', 'EXPENSE', '2026-08-30 23:55:44', 'Phở', '2026-08-30 16:56:13');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (2, 6, 1, 6, '85000.00', 'EXPENSE', '2026-08-31 00:28:15', 'Thẻ tháng genshin', '2026-08-30 17:28:50');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (3, 6, 1, 6, '200000.00', 'EXPENSE', '2026-08-31 01:48:42', 'Nạp Liên Quân Mobile', '2026-08-30 18:49:21');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (4, 7, 2, 1, '100000.00', 'EXPENSE', '2026-08-31 02:00:40', 'Ăn uống', '2026-08-30 19:00:49');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (5, 7, 3, 1, '360000.00', 'EXPENSE', '2026-08-31 02:00:58', 'Ăn uống', '2026-08-30 19:01:19');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (6, 6, 1, 1, '20000.00', 'EXPENSE', '2026-08-31 02:05:05', 'Mỳ tôm', '2026-08-30 19:05:16');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (7, 6, 4, 2, '30000.00', 'EXPENSE', '2026-08-31 02:05:34', 'Grab', '2026-08-30 19:05:57');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (8, 8, 5, 1, '25000.00', 'EXPENSE', '2026-08-31 12:37:10', 'mixue', '2026-08-31 05:37:22');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (9, 6, 1, 1, '17000.00', 'EXPENSE', '2026-08-31 12:39:48', 'Mixue (Trà Xanh Chanh)', '2026-08-31 05:40:33');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (10, 6, 1, 1, '35000.00', 'EXPENSE', '2026-08-31 12:40:35', 'Bún Giò Heo', '2026-08-31 05:40:47');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (12, 6, 1, 4, '300000.00', 'INCOME', '2026-08-31 15:36:10', 'Luong', '2026-08-31 08:36:31');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (13, 6, 1, 3, '1000000.00', 'EXPENSE', '2026-08-31 15:50:41', 'Bàn phím cơ', '2026-08-31 08:51:02');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (11, 6, 4, 1, '10000.00', 'EXPENSE', '2026-08-31 14:46:21', 'Sting', '2026-08-31 07:47:05');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (15, 6, 1, 1, '400000.00', 'EXPENSE', '2026-08-31 22:15:42', 'Lẩu Thái', '2026-08-31 15:15:59');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (17, 6, 1, 1, '30000.00', 'EXPENSE', '2026-09-01 13:07:24', 'Cơm', '2026-09-01 06:07:46');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (18, 6, 1, 1, '10000.00', 'EXPENSE', '2026-09-01 13:07:48', 'Nước', '2026-09-01 06:08:03');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (19, 6, 1, 1, '42000.00', 'EXPENSE', '2026-09-01 17:28:29', 'Bún đậu mắm tôm', '2026-09-01 10:28:51');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (20, 6, 1, 3, '54000.00', 'EXPENSE', '2026-09-02 12:56:14', 'Nước  + Sunlight + Mỳ tôm', '2026-09-02 05:56:57');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (22, 6, 1, 5, '4000000.00', 'INCOME', '2026-09-02 21:46:16', 'tro', '2026-09-02 14:46:34');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (23, 6, 1, 7, '1800000.00', 'EXPENSE', '2026-09-02 21:46:36', 'Tiền đóng trọ', '2026-09-02 14:46:52');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (24, 6, 1, 1, '127000.00', 'EXPENSE', '2026-09-03 00:58:29', 'Gà ủ muối', '2026-09-02 17:58:45');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (25, 6, 1, 1, '70000.00', 'EXPENSE', '2026-09-03 19:38:14', 'Hủ tiếu + nước + bánh', '2026-09-03 12:38:36');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (26, 6, 1, 2, '30000.00', 'EXPENSE', '2026-09-05 20:20:45', 'Xăng', '2026-09-05 13:20:58');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (28, 6, 1, 1, '30000.00', 'EXPENSE', '2026-09-05 19:07:00', 'Hủ tiếu', '2026-09-05 14:15:29');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (27, 6, 1, 8, '50000.00', 'EXPENSE', '2026-09-04 18:00:00', 'Cắt tóc', '2026-09-05 13:48:43');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (30, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-06 13:25:52', 'cơm', '2026-09-06 06:26:08');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (31, 6, 1, 1, '35000.00', 'EXPENSE', '2026-09-06 17:42:13', 'Hủ tiếu Giò', '2026-09-06 10:42:26');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (32, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-06 17:42:28', 'Bánh Gạo', '2026-09-06 10:42:39');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (33, 6, 1, 3, '35000.00', 'EXPENSE', '2026-09-06 20:05:23', 'Áo mưa', '2026-09-06 13:05:35');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (29, 6, 1, 1, '39000.00', 'EXPENSE', '2026-09-06 07:49:11', 'Soda Dâu Tây', '2026-09-06 00:49:35');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (34, 6, 1, 1, '50000.00', 'EXPENSE', '2026-09-07 17:25:08', 'Hủ tiếu', '2026-09-07 10:25:17');
INSERT INTO "transactions" ("transaction_id", "user_id", "wallet_id", "category_id", "amount", "type", "transaction_date", "note", "created_at") VALUES (35, 6, 1, 1, '25000.00', 'EXPENSE', '2026-09-07 12:00:00', 'Cơm', '2026-09-07 10:25:44');

-- ------------------------------------------------------------
-- Cấu trúc bảng `notifications`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "notifications" CASCADE;
CREATE TABLE "notifications" (
    "notification_id" BIGINT NOT NULL,
    "user_id" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "is_read" BOOLEAN DEFAULT false,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY ("notification_id")
);

-- Dữ liệu bảng `notifications`
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (1, 6, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-30 16:10:30');
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (3, 6, 'Cập nhật ứng dụng', 'Phiên bản mới 1.3.0 đã sẵn sàng. Cập nhật ngay để trải nghiệm các tính năng mới!', 'SYSTEM', True, '2026-08-31 16:43:55');
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (4, 6, 'Vượt ngân sách: Ăn uống', 'Bạn đã chi tiêu vượt quá hạn mức ngân sách Ăn uống trong tháng này.', 'WARNING', True, '2026-08-31 18:33:24');
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (5, 6, 'Ngân sách Trọ sắp hết', 'Bạn đã tiêu vượt quá ngân sách Trọ tháng này. Hãy điều chỉnh chi tiêu!', 'BUDGET_ALERT', True, '2026-09-02 14:58:41');
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (2, 8, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-31 05:36:14');
INSERT INTO "notifications" ("notification_id", "user_id", "title", "content", "type", "is_read", "created_at") VALUES (6, 7, 'Chào mừng!', 'Chào mừng bạn đến với Cointap.', 'SYSTEM', True, '2026-08-30 18:59:26');

-- ------------------------------------------------------------
-- Cấu trúc bảng `ai_conversations`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "ai_conversations" CASCADE;
CREATE TABLE "ai_conversations" (
    "session_id" TEXT NOT NULL,
    "user_id" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT now(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY ("session_id")
);

-- Dữ liệu bảng `ai_conversations`
INSERT INTO "ai_conversations" ("session_id", "user_id", "title", "created_at", "updated_at") VALUES ('session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', '2026-09-05 23:26:33', '2026-09-05 23:41:26');
INSERT INTO "ai_conversations" ("session_id", "user_id", "title", "created_at", "updated_at") VALUES ('session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', '2026-09-06 12:49:36', '2026-09-06 12:49:59');
INSERT INTO "ai_conversations" ("session_id", "user_id", "title", "created_at", "updated_at") VALUES ('session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', '2026-09-06 21:46:53', '2026-09-06 23:32:49');

-- ------------------------------------------------------------
-- Cấu trúc bảng `ai_chat_messages`
-- ------------------------------------------------------------
DROP TABLE IF EXISTS "ai_chat_messages" CASCADE;
CREATE TABLE "ai_chat_messages" (
    "message_id" BIGINT DEFAULT nextval('ai_chat_messages_message_id_seq'::regclass) NOT NULL,
    "session_id" TEXT NOT NULL,
    "user_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "is_user" BOOLEAN DEFAULT true NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY ("message_id")
);

-- Dữ liệu bảng `ai_chat_messages`
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (19, 'session_1788625593214', 6, 'Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?', True, '2026-09-05 23:26:33');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (20, 'session_1788625593214', 6, 'Chưa, tổng chi tiêu tháng 9 của bạn **chưa vượt hạn mức** ngân sách! ✅

**Tình hình ngân sách các danh mục:**
•  **Trọ**: đã chi **1.800.000đ** / **1.800.000đ** (100%) - **An toàn**
•  **Ăn uống**: đã chi **522.000đ** / **1.000.000đ** (52%) - **An toàn** (còn lại **478.000đ**)
•  **Di chuyển**: đã chi **30.000đ** / **300.000đ** (10%) - **An toàn** (còn lại **270.000đ**)
•  **Tổng chi tiêu thực tế tháng này**: **2.243.000đ** (trên tổng thu nhập **4.000.000đ**)

Nếu bạn muốn, mình có thể phân tích tiếp:
•  **dự báo tốc độ chi tiêu danh mục Ăn uống** đến cuối tháng
•  **gợi ý kế hoạch tiết kiệm** từ số tiền dư còn lại
•  hoặc **xem chi tiết các giao dịch gần đây** 📊', False, '2026-09-05 23:26:58');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (21, 'session_1788625593214', 6, 'Xem chi tiết các giao dịch gần đây', True, '2026-09-05 23:41:20');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (22, 'session_1788625593214', 6, 'Dưới đây là **danh sách các giao dịch gần đây nhất** của bạn 📋

**Chi tiết các giao dịch gần đây:**
•  **05/09**: Chi **30.000đ** - Di chuyển (Xăng)
•  **05/09**: Chi **30.000đ** - Ăn uống (Hu Tieu)
•  **04/09**: Chi **50.000đ** - Khác (Cat toc)
•  **03/09**: Chi **70.000đ** - Ăn uống (Hủ tiếu + nước + bánh)
•  **03/09**: Chi **127.000đ** - Ăn uống (Gà ủ muối)
•  **02/09**: Chi **1.800.000đ** - Trọ (Tiền đóng trọ)
•  **02/09**: Thu **+4.000.000đ** - Thu nhập phụ (tro)
•  **02/09**: Chi **54.000đ** - Mua sắm (Nước + Sunlight + Mỳ tôm)
•  **01/09**: Chi **42.000đ** - Ăn uống (Bún đậu mắm tôm)
•  **01/09**: Chi **10.000đ** - Ăn uống (Nước)
•  **01/09**: Chi **30.000đ** - Ăn uống (Cơm)
•  **31/08**: Chi **400.000đ** - Ăn uống (Lẩu Thái)

Nếu bạn muốn, mình có thể phân tích tiếp:
•  **chi tiết cơ cấu chi tiêu danh mục Ăn uống**
•  **gợi ý phân bổ số dư còn lại (2.777.000đ)**
•  hoặc **dự báo chi tiêu cho những tuần tiếp theo** 📊', False, '2026-09-05 23:41:26');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (23, 'session_1788673776904', 6, 'Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?', True, '2026-09-06 12:49:36');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (24, 'session_1788673776904', 6, 'Chi tiêu tháng 9 của bạn tăng vọt chủ yếu do khoản chi lớn **1.800.000đ cho Tiền đóng trọ** (chiếm gần 79% tổng chi tiêu tháng) 🏠

**Chi tiết phân tích chi tiêu tháng này:**
•  **Khoản chi lớn nhất:** Tiền đóng trọ **1.800.000đ** phát sinh vào ngày 02/09.
•  **Chi tiêu sinh hoạt:** Tổng cộng **482.000đ** cho các nhu cầu hàng ngày, bao gồm **Ăn uống** (**309.000đ**), **Mua sắm** (**93.000đ**), **Khác** (**50.000đ**) và **Di chuyển** (**30.000đ**).
•  **Tổng chi tiêu hiện tại:** **2.282.000đ** trên tổng thu nhập **4.000.000đ**. Dù chi tiêu tăng nhanh đầu tháng do trả tiền nhà, các danh mục còn lại của Nam vẫn đang ở mức an toàn.

Nếu bạn muốn, mình có thể phân tích tiếp:
•  **dự báo chi tiêu còn lại trong tháng 9** 📊
•  **chi tiết hạn mức ngân sách các danh mục sinh hoạt**
•  hoặc **gợi ý kế hoạch phân bổ số dư 2.738.000đ hiện tại** 💰', False, '2026-09-06 12:49:59');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (25, 'session_1788706013188', 6, 'Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?', True, '2026-09-06 21:46:53');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (26, 'session_1788706013188', 6, 'Để quản lý tài chính an toàn trong 25 ngày còn lại của tháng 9, anh Nam nên chi tiêu tối đa khoảng **104.000đ/ngày** 💡

**Cơ sở tính toán chi tiết:**
•  **Số dư tài sản hiện tại:** **2.618.000đ** (Ví VCB).
•  **Thời gian còn lại trong tháng:** **25 ngày** (từ 6/9 đến 30/9).
•  **Hạn mức theo tổng số dư khả dụng:** Tối đa **104.700đ/ngày** (nếu sử dụng hết số tiền hiện có).
•  **Hạn mức khuyến nghị (giữ thu nhập còn dư):** Nếu chỉ tiêu trong phần thu nhập tháng 9 còn lại (**1.598.000đ**), anh nên duy trì mức **64.000đ/ngày** để giữ khoản tích lũy an toàn.
•  **Hạn mức ăn uống còn lại:** Danh mục Ăn uống còn **478.000đ** ngân sách, tương đương khoảng **19.000đ/ngày** (cần cân nhắc điều chỉnh vì các bữa ăn chính hiện tại trung bình 25.000đ - 35.000đ/bữa).

Nếu bạn muốn, mình có thể phân tích tiếp:
•  **gợi ý điều chỉnh hạn mức danh mục Ăn uống cho thực tế hơn**
•  **lập kế hoạch phân bổ chi tiêu chi tiết theo từng tuần**
•  hoặc **mẹo cắt giảm các khoản chi vặt không cần thiết** 📊', False, '2026-09-06 21:47:48');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (27, 'session_1788706013188', 6, 'Mẹo cắt giảm các khoản chi vặt không cần thiết', True, '2026-09-06 23:32:01');
INSERT INTO "ai_chat_messages" ("message_id", "session_id", "user_id", "content", "is_user", "created_at") VALUES (28, 'session_1788706013188', 6, 'Chào anh Nam, việc kiểm soát các khoản chi vặt như **đồ uống, ăn vặt và đồ dùng mua đột xuất** sẽ giúp anh tiết kiệm ngay từ **300.000đ - 500.000đ mỗi tháng** 💡

**Các mẹo cắt giảm chi vặt hiệu quả:**
•  **Kiểm soát món ăn kèm và nước uống:** Nhìn vào lịch sử gần đây, các khoản nhỏ như *Soda Dâu Tây (39.000đ)* hay *Bánh Gạo (25.000đ)* tuy không lớn nhưng khi cộng dồn lại sẽ chiếm tỷ trọng đáng kể. Anh có thể chuẩn bị sẵn nước lọc hoặc đồ ăn nhẹ từ nhà.
•  **Chuẩn bị sẵn vật dụng cá nhân:** Chi phí phát sinh như *Áo mưa (35.000đ)* hoàn toàn có thể tránh được nếu anh luôn để sẵn áo mưa cá nhân trong cốp xe.
•  **Áp dụng quy tắc "Dừng 5 giây":** Trước khi thanh toán khoản chi ngẫu hứng dưới **50.000đ**, hãy tự hỏi bản thân khoản này là "Thực sự cần" hay chỉ là "Sở thích bộc phát".
•  **Theo dõi sát hạn mức Ăn uống:** Hiện tại mục Ăn uống của anh đã chi **522.000đ** (đạt **52%** hạn mức tháng). Việc ghi chép ngay lập tức trên CoinTap giúp anh nhận ra hạn mức còn lại để cân chỉnh kịp thời.

Nếu bạn muốn, mình có thể phân tích tiếp:
•  **tổng số tiền chi cho ăn vặt/đồ uống** từ đầu tháng đến nay
•  **gợi ý hạn mức chi tiêu theo ngày** phù hợp với số dư **2.618.000đ** hiện tại
•  hoặc **dự báo chi tiêu** trong những tuần tiếp theo 📊', False, '2026-09-06 23:32:49');

-- ------------------------------------------------------------
-- Các hàm và Trigger (Functions & Triggers)
-- ------------------------------------------------------------
-- Hàm update_wallet_balance
CREATE OR REPLACE FUNCTION update_wallet_balance()

BEGIN
    -- XỬ LÝ KHI XÓA (DELETE)
    IF TG_OP = 'DELETE' THEN
        IF OLD.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE wallet_id = OLD.wallet_id;
        ELSIF OLD.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance + OLD.amount WHERE wallet_id = OLD.wallet_id;
        END IF;
        RETURN OLD;
    END IF;

    -- XỬ LÝ KHI SỬA (UPDATE)
    IF TG_OP = 'UPDATE' THEN
        -- Hoàn lại tiền từ giao dịch cũ
        IF OLD.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE wallet_id = OLD.wallet_id;
        ELSIF OLD.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance + OLD.amount WHERE wallet_id = OLD.wallet_id;
        END IF;
        
        -- Trừ/Cộng tiền cho giao dịch mới
        IF NEW.type = 'INCOME' THEN
            UPDATE wallets SET balance = balance + NEW.amount WHERE wallet_id = NEW.wallet_id;
        ELSIF NEW.type = 'EXPENSE' THEN
            UPDATE wallets SET balance = balance - NEW.amount WHERE wallet_id = NEW.wallet_id;
        END IF;
        
        RETURN NEW;
    END IF;

    -- XỬ LÝ KHI THÊM MỚI (INSERT)
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
;
