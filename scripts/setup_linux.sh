#!/bin/bash
# ==============================================================================
# SCRIPT TRIỂN KHAI TỰ ĐỘNG COINTAP TRÊN MÁY CHỦ LINUX (UBUNTU / DEBIAN)
# Hỗ trợ PostgreSQL, Gunicorn, Nginx & Tự động nạp CSDL từ Supabase
# ==============================================================================

set -e

echo "=========================================================================="
echo "🚀 BẮT ĐẦU QUÁ TRÌNH TRIỂN KHAI COINTAP TRÊN LINUX SERVER"
echo "=========================================================================="

APP_DIR="/var/www/cointap"
DB_NAME="cointap_db"
DB_USER="cointap_user"
DB_PASS="cointap_secure_password_2026"

# 1. Cập nhật hệ thống và cài đặt gói cần thiết
echo "==> 1. Cập nhật apt và cài đặt Python, PostgreSQL, Nginx..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl git

# 2. Cấu hình Cơ sở dữ liệu PostgreSQL
echo "==> 2. Thiết lập cơ sở dữ liệu PostgreSQL..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

# 3. Nạp dữ liệu sao chép từ Supabase vào PostgreSQL
echo "==> 3. Nạp dữ liệu toàn bộ từ Supabase vào PostgreSQL Linux..."
if [ -f "$APP_DIR/database/init_cointap_database.sql" ]; then
    PGPASSWORD="$DB_PASS" psql -h 127.0.0.1 -U $DB_USER -d $DB_NAME -f "$APP_DIR/database/init_cointap_database.sql"
    echo "  [OK] Đã nạp thành công dữ liệu Supabase vào PostgreSQL!"
else
    echo "  [!] Không tìm thấy file init_cointap_database.sql, bỏ qua bước nạp trực tiếp."
fi

# 4. Thiết lập Virtualenv và cài thư viện Python
echo "==> 4. Tạo môi trường ảo Python và cài đặt dependencies..."
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Cấu hình file .env cho môi trường máy chủ
echo "==> 5. Cấu hình biến môi trường production..."
cat <<EOF > "$APP_DIR/.env"
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://*,https://*

# Bật PostgreSQL trên máy chủ Linux
USE_POSTGRES=True
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Gemini AI Key
GEMINI_API_KEY=your_gemini_api_key_here
EOF

# 6. Chạy migrate và thu thập static files
echo "==> 6. Đồng bộ Schema Django và gom Static Files..."
python manage.py migrate --fake-initial || python manage.py migrate
python manage.py collectstatic --noinput

# Phân quyền thư mục cho www-data
sudo chown -R www-data:www-data "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

# 7. Cấu hình Systemd Service cho Gunicorn
echo "==> 7. Tạo Systemd Service cho Gunicorn..."
sudo cp "$APP_DIR/scripts/gunicorn.service" /etc/systemd/system/cointap.service
sudo systemctl daemon-reload
sudo systemctl start cointap
sudo systemctl enable cointap

# 8. Cấu hình Nginx Reverse Proxy
echo "==> 8. Cấu hình Nginx..."
sudo cp "$APP_DIR/scripts/nginx_cointap.conf" /etc/nginx/sites-available/cointap
sudo ln -sf /etc/nginx/sites-available/cointap /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default || true
sudo nginx -t
sudo systemctl restart nginx

echo "=========================================================================="
echo "🎉 TRIỂN KHAI COINTAP HOÀN TẤT THÀNH CÔNG!"
echo "Truy cập trình duyệt theo địa chỉ IP máy chủ của bạn để trải nghiệm CoinTap."
echo "=========================================================================="

