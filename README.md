# 🌟 CoinTap - Nền Tảng Quản Lý Chi Tiêu & Trợ Lý Tài Chính AI

Ứng dụng web toàn diện được xây dựng bằng **Django 5.1+ / 6.0+**, tích hợp CSDL **PostgreSQL / SQLite** và trí tuệ nhân tạo **Google Gemini AI**.
Giao diện được thiết kế theo chuẩn **Frontend-Design Skill** của Anthropic với bản sắc nhận diện thương hiệu công nghệ tài chính hiện đại.

---

## 🎨 Điểm Nổi Bật Thiết Kế (Anthropic Frontend-Design)
- **Bảng màu 6 sắc độ có chủ đích:** Tông tím hoàng gia Indigo (`#6366F1`) kết hợp Slate Navy (`#0B132B`), Xanh ngọc lục bảo (`#10B981`) cho thu nhập, Đỏ san hô (`#F43F5E`) cho chi tiêu, và Vàng hổ phách (`#F59E0B`) cho cảnh báo nguy cơ.
- **Typography chuyên nghiệp:** Font **Plus Jakarta Sans** thoáng đãng kết hợp **JetBrains Mono** với thuộc tính `font-variant-numeric: tabular-nums` cho số tiền thẳng tắp.
- **Bố cục Financial Pulse:** Nắm bắt toàn bộ sức khỏe tài chính trong 3 giây.
- **Thanh đo tiến độ tiêu thụ:** Tự động tính hạn mức an toàn mỗi ngày và đổi màu theo % chi tiêu.

---

## 🚀 Các Phân Hệ & Chức Năng

### 1. Phân Hệ Người Dùng Cá Nhân
- 📊 **Dashboard Tổng Quan:** KPI tổng tài sản, dòng tiền tháng, biểu đồ xu hướng 7 ngày, biểu đồ Donut tỷ trọng chi tiêu, giao dịch gần nhất.
- 💳 **Quản Lý Ví Tiền:** Hỗ trợ đa dạng loại ví (`CASH`, `BANK`, `E_WALLET`, `SAVINGS`, `CREDIT`), đổi màu đại diện, icon và **chuyển tiền giữa các ví**.
- 📋 **Sổ Cái Thu - Chi:** Lọc theo hình thức, ví, danh mục, thời gian, tìm kiếm từ khóa, xuất dữ liệu ra file CSV cho Excel.
- 🎯 **Quản Lý Ngân Sách:** Giới hạn hạn mức cho từng danh mục, tự động tính số tiền còn lại và cảnh báo khi chi quá tay.
- 🏷️ **Danh Mục:** Quản lý danh mục mẫu hệ thống và tự do tạo danh mục chi tiêu cá nhân.
- 📈 **Báo Cáo & Phân Tích:** Bộ chọn tháng/năm, biểu đồ cột 6 tháng, cơ cấu thu chi, Top 5 khoản chi lớn nhất, gợi ý tài chính thông minh.
- 🤖 **Trợ Lý Cố Vấn CoinTap AI:** Hội thoại đa phiên với Gemini AI, phân tích chi tiêu thực tế, dự báo ngân sách, gợi ý tiết kiệm.
- 🔔 **Trung Tâm Thông Báo:** Nhận cảnh báo vượt ngân sách và thông báo đẩy từ hệ thống.

### 2. Cổng Quản Trị Hệ Thống (`/admin-portal/`)
- 🛡️ **Dashboard KPI:** Giám sát tổng người dùng, ví tiền, giao dịch và lượng tiền lưu hành toàn hệ thống.
- 👥 **Quản Lý Người Dùng:** Xem danh sách, mở modal kiểm tra ví tiền và lịch sử giao dịch của từng người dùng, xóa tài khoản.
- 🔑 **Quản Trị Viên (Bảng riêng `admins`):** Quản lý tài khoản quản trị, cấp quyền `Super Admin` hoặc `Administrator`.
- 🗂️ **Danh Mục Chuẩn:** Thêm, sửa, xóa các danh mục mẫu dùng chung toàn sàn.
- 👁️ **Thanh Tra Nhật Ký AI:** Đọc lại các câu hỏi và câu trả lời giữa người dùng và Gemini AI.
- 📢 **Phát Thông Báo Toàn Sàn:** Bắn thông báo đẩy tức thì tới tất cả người dùng ứng dụng.

---


## 🔐 Tài Khoản Đăng Nhập Mẫu (Tự Động Nhận Diện Vai Trò Thông Minh)

Trang đăng nhập duy nhất tại `http://127.0.0.1:8000/login/` tự động nhận diện danh tính và chuyển hướng đúng về phân hệ tương ứng:

---

## 💻 Hướng Dẫn Chạy Cục Bộ (Local Development)

```bash
# 1. Kích hoạt môi trường ảo
.venv\Scripts\activate

# 2. Khởi chạy máy chủ Django
python manage.py runserver
```

Mở trình duyệt:
- Người dùng: **`http://127.0.0.1:8000/`**
- Quản trị: **`http://127.0.0.1:8000/admin-portal/`**

---

## 🐧 Hướng Dẫn Triển Khai Trên Máy Chủ Linux

Xem hướng dẫn chi tiết tại [**`deployment_guide.md`**](deployment_guide.md) hoặc sử dụng các script tự động hóa:
- Cài đặt tự động Ubuntu/Debian: `sudo bash scripts/setup_linux.sh`
- Cấu hình Gunicorn: `scripts/gunicorn.service`
- Cấu hình Nginx: `scripts/nginx_cointap.conf`
- Chạy qua Docker Compose: `cd scripts && docker compose up -d`

