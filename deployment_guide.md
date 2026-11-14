# 🌟 HƯỚNG DẪN TRIỂN KHAI & VẬN HÀNH DỰ ÁN COINTAP TRÊN LINUX SERVER

Chào bạn! Dưới đây là tài liệu chi tiết hướng dẫn chạy cục bộ trên máy tính và triển khai toàn bộ dự án **CoinTap (Django + PostgreSQL)** lên máy chủ Linux độc lập (Self-hosted) với cơ sở dữ liệu đã được sao chép toàn bộ từ **Supabase**.

---

## 📋 1. Danh Sách Tài Khoản Mẫu Đăng Nhập (Đã Đồng Bộ Từ Supabase)

Hệ thống đã có sẵn dữ liệu và tính năng **Đăng nhập nhanh 1-Click** ngay tại màn hình đăng nhập:

### 👤 Tài Khoản Người Dùng (Mobile / Web App User)
| Tên người dùng | Email đăng nhập | Mật khẩu | Số ví & Dòng tiền |
|---|---|---|---|
| **Lê Nhật Nam** | `nhatnam28062006@gmail.com` | `Lnnam286@` | 2 ví (VCB 2.543.000₫, Tiền mặt) + 25 giao dịch |
| **quan** | `leq118157@gmail.com` | `123456` | 2 ví (Ví Tiền Mặt, hahaha 9.640.000₫) |
| **Tiểu Màn Thầu** | `ggwn021@gmail.com` | `thaoMinh11` | 1 ví (Heo Đất 3.575.000₫) |

### 🛡️ Tài Khoản Quản Trị Viên (Admin Portal - `/admin-portal/`)
| Username | Vai trò | Mật khẩu | Email |
|---|---|---|---|
| **admin** | Super Admin | `Lnnam123@` | `admin@cointap.vn` |
| **nhatnam286** | Administrator | `Lnnam123@` | `nhatnam286@cointap.vn` |

---

## 💻 2. Chạy Thử Cục Bộ Trên Máy Tính (Local Testing)

Dự án đã được cấu hình tự động nhận diện:
- Mặc định sử dụng **SQLite** với toàn bộ dữ liệu mẫu đã được nạp sẵn.
- Bạn chỉ cần chạy lệnh sau tại thư mục dự án:

```bash
# Kích hoạt môi trường ảo
.venv\Scripts\activate

# Khởi chạy máy chủ phát triển
python manage.py runserver
```

Mở trình duyệt truy cập:
- **Trang người dùng:** `http://127.0.0.1:8000/`
- **Cổng quản trị hệ thống:** `http://127.0.0.1:8000/admin-portal/`

---

## 🐧 3. Hướng Dẫn Triển Khai Lên Máy Chủ Linux Riêng (Self-hosted Ubuntu/Debian)

### CÁCH 1: Cài đặt tự động bằng Script 1-Click (Khuyên dùng)

1. Sao chép toàn bộ thư mục dự án lên máy chủ Linux (ví dụ vào `/var/www/cointap`):
   ```bash
   scp -r ./* user@your_server_ip:/var/www/cointap/
   ```

2. Đăng nhập SSH vào server Linux và chạy script tự động:
   ```bash
   cd /var/www/cointap
   chmod +x scripts/setup_linux.sh
   sudo bash scripts/setup_linux.sh
   ```
   Script sẽ tự động:
   - Cài đặt Python 3, PostgreSQL, Nginx, Gunicorn.
   - Tạo database `cointap_db` và user `cointap_user`.
   - Nạp file SQL `database/init_cointap_database.sql` (toàn bộ dữ liệu Supabase).
   - Thiết lập service systemd `cointap.service` và Reverse Proxy Nginx.

---

### CÁCH 2: Triển khai thủ công từng bước với PostgreSQL

#### Bước 1: Cài đặt PostgreSQL trên Linux
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib python3-pip python3-venv nginx
```

#### Bước 2: Tạo CSDL & Nạp Dữ Liệu Từ File SQL
```bash
# Đăng nhập vào PostgreSQL
sudo -u postgres psql

# Chạy các câu lệnh SQL tạo user và database:
CREATE USER cointap_user WITH PASSWORD 'cointap_secure_password_2026';
CREATE DATABASE cointap_db OWNER cointap_user;
GRANT ALL PRIVILEGES ON DATABASE cointap_db TO cointap_user;
ALTER USER cointap_user CREATEDB;
\q
```

**Thực thi nạp toàn bộ cấu trúc bảng, triggers và dữ liệu từ Supabase:**
```bash
PGPASSWORD='cointap_secure_password_2026' psql -h 127.0.0.1 -U cointap_user -d cointap_db -f database/init_cointap_database.sql
```

> **Lưu ý:** File `database/init_cointap_database.sql` đã bao gồm:
> - Đầy đủ 9 bảng: `users`, `admins`, `wallets`, `categories`, `budgets`, `transactions`, `notifications`, `ai_conversations`, `ai_chat_messages`.
> - Trigger `update_wallet_balance()` tự động cập nhật số dư ví khi thêm/sửa/xóa giao dịch.
> - Đồng bộ lại toàn bộ Sequences auto-increment để tránh lỗi trùng khóa chính khi tạo mới.

#### Bước 3: Cấu hình file `.env` trên Server
Tạo hoặc sửa file `/var/www/cointap/.env`:
```env
DEBUG=False
SECRET_KEY=cointap_very_strong_secret_key_linux_2026
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://your_server_ip,https://your_domain.com,http://127.0.0.1:8000

# Bật kết nối PostgreSQL
USE_POSTGRES=True
POSTGRES_DB=cointap_db
POSTGRES_USER=cointap_user
POSTGRES_PASSWORD=cointap_secure_password_2026
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Gemini API Key cho Trợ lý AI
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Bước 4: Cài đặt thư viện Python & Gom Static Files
```bash
cd /var/www/cointap
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Đồng bộ Django (dùng cờ --fake-initial vì CSDL đã được nạp từ file SQL)
python manage.py migrate --fake-initial
python manage.py collectstatic --noinput
```

#### Bước 5: Cấu hình Gunicorn Systemd Service
Copy file service:
```bash
sudo cp scripts/gunicorn.service /etc/systemd/system/cointap.service
sudo systemctl daemon-reload
sudo systemctl start cointap
sudo systemctl enable cointap
```

Kiểm tra trạng thái service:
```bash
sudo systemctl status cointap
```

#### Bước 6: Cấu hình Nginx
```bash
sudo cp scripts/nginx_cointap.conf /etc/nginx/sites-available/cointap
sudo ln -sf /etc/nginx/sites-available/cointap /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Mở trình duyệt truy cập địa chỉ IP máy chủ của bạn (ví dụ `http://192.168.1.100` hoặc IP VPS), bạn sẽ thấy CoinTap hoạt động với tốc độ phản hồi cực nhanh!

---

### CÁCH 3: Triển khai bằng Docker Compose (1 Lệnh duy nhất)

Nếu server của bạn đã có cài sẵn Docker:
```bash
cd /var/www/cointap/scripts
docker compose up -d --build
```
Hệ thống sẽ tự khởi tạo container PostgreSQL 16 và container Django Web tại cổng `8000`.

---

## 🎨 4. Điểm Nổi Bật Về Thiết Kế Giao Diện (Frontend Design Skill)

1. **Nhận diện thương hiệu đặc trưng (Brand Identity):**
   - Palette màu sang trọng: Slate Navy (`#0B132B`), Signature Indigo (`#6366F1`), Mint Green (`#10B981`) cho thu nhập, Coral Red (`#F43F5E`) cho chi tiêu.
   - Typography đôi: **Plus Jakarta Sans** cho nội dung hiển thị nhân văn và **JetBrains Mono** với thuộc tính `font-variant-numeric: tabular-nums` cho số tiền thẳng tắp.
2. **Khu vực trọng tâm "Financial Pulse":** Nắm bắt toàn bộ tổng tài sản, thặng dư tích lũy, tỷ trọng chi tiêu và hạn mức ngân sách chỉ trong 3 giây.
3. **Trợ lý Tài chính AI (CoinTap AI):**
   - Tích hợp mô hình Gemini AI kết hợp bộ máy phân tích dữ liệu thực tế tại chỗ.
   - Gợi ý câu hỏi thông minh theo ngữ cảnh: dự báo tốc độ chi tiêu, phân tích danh mục tăng đột biến, tính hạn mức tiêu an toàn mỗi ngày.
4. **Phân quyền và Cổng Quản trị (Admin Portal):**
   - Bảng riêng biệt `admins` cho tài khoản quản trị.
   - Module giám sát người dùng, kiểm tra ví tiền, thanh tra nhật ký AI và phát thông báo toàn sàn.

