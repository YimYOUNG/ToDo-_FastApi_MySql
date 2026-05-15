#!/bin/bash
set -e

echo "========================================="
echo "  Todo App 阿里云服务器初始化脚本"
echo "========================================="

SERVER_IP="8.136.51.220"
MYSQL_ROOT_PASSWORD="yym123456"
APP_DIR="/var/www/todo-app"
LOG_DIR="/var/log/todo-app"
SERVICE_FILE="todo-app.service"

echo ""
echo "[1/9] 更新系统包..."
apt update && apt upgrade -y

echo ""
echo "[2/9] 安装基础依赖..."
apt install -y python3.11 python3.11-venv python3-pip python3-venv \
    mysql-server nginx certbot python3-certbot-nginx ufw git curl

echo ""
echo "[3/9] 配置MySQL..."
systemctl start mysql
systemctl enable mysql
mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS todo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
FLUSH PRIVILEGES;
EOF
echo "MySQL已配置，数据库 todo_db 已创建"

echo ""
echo "[4/9] 创建应用用户和目录..."
id -u www-data &>/dev/null || useradd -r -s /bin/false www-data
mkdir -p ${APP_DIR} ${LOG_DIR}
chown -R www-data:www-data ${APP_DIR} ${LOG_DIR}
chmod 755 ${LOG_DIR}

echo ""
echo "[5/9] 配置防火墙..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
echo "y" | ufw enable
echo "防火墙已配置：开放 22/80/443 端口"

echo ""
echo "[6/9] 配置Nginx..."
if [ -f "${APP_DIR}/scripts/nginx.conf" ]; then
    cp "${APP_DIR}/scripts/nginx.conf" /etc/nginx/sites-available/todo-app
    ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx
    echo "Nginx配置完成"
else
    echo "警告：nginx.conf 未找到，请手动配置Nginx"
fi

echo ""
echo "[7/9] 安装Systemd服务..."
cp "${APP_DIR}/${SERVICE_FILE}" /etc/systemd/system/
systemctl daemon-reload
systemctl enable todo-app.service
echo "todo-app服务已注册并设为开机启动"

echo ""
echo "[8/9] 初始化Python虚拟环境..."
cd ${APP_DIR}
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "依赖安装完成"
fi

echo ""
echo "========================================="
echo "  初始化完成！后续步骤："
echo "========================================="
echo ""
echo "  1. 克隆代码到 ${APP_DIR}:"
echo "     cd ${APP_DIR} && git clone <你的仓库地址> ."
echo ""
echo "  2. 配置生产环境变量:"
echo "     cp .env.example .env"
echo "     # 编辑 .env 设置 SECRET_KEY, JWT_SECRET_KEY 等"
echo ""
echo "  3. 执行数据库迁移:"
echo "     source venv/bin/activate"
echo "     alembic upgrade head"
echo ""
echo "  4. 申请SSL证书 (域名解析完成后):"
echo "     certbot --nginx -d yourdomain.com"
echo ""
echo "  5. 启动应用:"
echo "     systemctl start todo-app"
echo "     systemctl status todo-app"
echo ""
echo "  6. 验证运行状态:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  服务器公网IP: ${SERVER_IP}"
echo "========================================="
