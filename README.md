# 📋 Todo App - 团队协作待办事项管理系统

<p align="center">
  <strong>基于 FastAPI + MySQL 的现代化待办事项管理应用</strong><br>
  支持团队协作、日历视图、数据统计、番茄钟等丰富功能
</p>

---

## ✨ 核心功能

### 🎯 待办事项管理
- ✅ **CRUD 操作** - 创建、编辑、删除、批量操作待办事项
- 🏷️ **标签系统** - 自定义标签分类，快速筛选
- 📊 **优先级管理** - 高/中/低三级优先级，智能排序
- 📅 **截止日期** - 日历视图直观展示，到期提醒
- ✅ **状态流转** - 待处理 → 进行中 → 已完成 / 已取消
- 🔍 **高级筛选** - 按状态、优先级、标签、日期范围筛选
- 📤 **数据导出** - 支持 CSV/Excel 格式导出

### 👥 团队协作
- 🔗 **共享待办** - 分享给团队成员（可编辑/只读权限）
- 🔄 **双向同步** - 编辑共享待办实时同步给所有成员
- 👁️ **权限控制** - Owner(全部) / Write(编辑) / Read(只读)
- 📋 **协作面板** - 查看"我分享的"和"收到的共享"

### 📅 日历视图
- 📆 **月视图展示** - 直观显示每月待办分布
- 🔗 **共享标识** - 共享待办带特殊图标区分
- 📌 **详情弹窗** - 点击日期查看当日待办详情
- ⚡ **快速导航** - 上月/下月/今天快捷切换

### 📈 数据统计
- 📊 **可视化图表** - 完成率、状态分布、趋势分析
- 🏷️ **标签统计** - 各标签任务数量和占比
- 📅 **时间分析** - 每周/每月完成任务趋势
- 🎯 **效率报告** - 个人工作效率评估

### 🍅 番茄钟
- ⏰ **25分钟专注** - 经典番茄工作法
- 📝 **关联待办** - 将番茄钟与具体任务绑定
- 📊 **专注记录** - 统计每日/每周专注时长

### 🎨 用户体验
- 🌙 **暗色模式** - 自动切换/手动设置，护眼舒适
- 📱 **响应式设计** - 适配桌面端、平板、手机
- 🔐 **安全认证** - JWT Token 登录，密码加密存储
- 😊 **个性化头像** - 根据用户名自动生成 Emoji 头像

---

## 🛠️ 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | 0.115.6 | Web 框架（高性能异步） |
| **SQLAlchemy** | 2.0.36 | ORM（异步支持） |
| **aiomysql** | 0.2.0 | 异步 MySQL 驱动 |
| **Pydantic** | 2.10.4 | 数据验证和序列化 |
| **JWT (python-jose)** | 3.3.0 | 用户认证令牌 |
| **bcrypt** | 4.1.1 | 密码哈希加密 |
| **Uvicorn** | 0.34.0 | ASGI 服务器 |
| **Alembic** | 1.14.1 | 数据库迁移工具 |
| **Jinja2** | 3.1.5 | HTML 模板引擎 |

### 前端技术
| 技术 | 用途 |
|------|------|
| **HTML5 + CSS3** | 页面结构和样式 |
| **JavaScript (ES6+)** | 前端交互逻辑 |
| **原生 Fetch API** | 异步 HTTP 请求 |
| **CSS Variables** | 主题系统（亮色/暗色） |

### 基础设施
- **数据库**: MySQL 8.0+
- **Web服务器**: Nginx (生产环境) / Uvicorn (开发环境)
- **进程管理**: Systemd (Linux) / Gunicorn
- **缓存策略**: 浏览器缓存控制 + 版本号强制刷新

---

## 🚀 快速开始

### 📋 系统要求

- Python 3.11 或更高版本
- MySQL 8.0+ （或 MariaDB 10.5+）
- 操作系统: Windows / macOS / Linux
- 内存: 最低 512MB RAM
- 磁盘: 至少 1GB 可用空间

### 🔧 本地开发环境搭建（5分钟）

#### 第1步：克隆项目
```bash
git clone <你的仓库地址>
cd todo-app
```

#### 第2步：创建虚拟环境
```bash
# Windows
python -m venv .venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 第3步：安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 第4步：配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# Windows: notepad .env
# Linux/macOS: nano .env 或 vim .env
```

**`.env` 关键配置项**：
```env
# 应用配置
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
APP_NAME=TodoApp

# 数据库配置（必须修改！）
DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/todo_db

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret-key-at-least-256-bits-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

#### 第5步：初始化数据库
```bash
# 创建数据库表
python init_db.py

# 或者使用 Alembic 迁移（推荐）
alembic upgrade head
```

#### 第6步：启动应用
```bash
# 方式1：使用 run.py（推荐）
python run.py

# 方式2：直接运行 Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 第7步：访问应用
打开浏览器访问：
- 🌐 主页: http://localhost:8000
- 📝 注册: http://localhost:8000/register
- 🔑 登录: http://localhost:8000/login
- 📋 待办: http://localhost:8000/todos
- 📅 日历: http://localhost:8000/calendar
- 📊 统计: http://localhost:8000/statistics
- 🍅 番茄钟: http://localhost:8000/pomodoro
- 👥 协作: http://localhost:8000/collaboration

开发模式下可访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📦 生产环境部署

### 方案一：Systemd + Gunicorn + Nginx（推荐✅）

#### 适用场景
阿里云/腾讯云/AWS 等 Linux 服务器部署

#### 1️⃣ 服务器初始化
```bash
# 使用自带脚本快速初始化（Ubuntu/Debian）
chmod +x scripts/setup_server.sh
sudo ./scripts/setup_server.sh
```

脚本会自动完成：
- ✅ 安装 Python 3.11, MySQL, Nginx
- ✅ 创建 `todo_db` 数据库
- ✅ 配置防火墙（开放22/80/443端口）
- ✅ 创建应用目录 `/var/www/todo-app`
- ✅ 配置 Systemd 服务
- ✅ 创建 Python 虚拟环境并安装依赖

#### 2️⃣ 部署代码
```bash
cd /var/www/todo-app
git clone <你的仓库地址> .

# 配置生产环境变量
cp .env.example .env
nano .env  # 必须修改以下关键配置：
```

**生产环境 `.env` 必须修改项**：
```env
DEBUG=false  # ❌ 重要：关闭调试模式！

# 使用强随机密钥（至少32字符）
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 生产数据库地址
DATABASE_URL=mysql+aiomysql://用户名:密码@127.0.0.1:3306/todo_db

# CORS 设置为你的域名
CORS_ORIGINS=["https://yourdomain.com"]
```

#### 3️⃣ 数据库迁移
```bash
source venv/bin/activate
alembic upgrade head
```

#### 4️⃣ 启动服务
```bash
sudo systemctl start todo-app
sudo systemctl enable todo-app  # 设为开机启动
sudo systemctl status todo-app # 查看运行状态
```

#### 5️⃣ 配置 Nginx 反向代理
```bash
# 复制 Nginx 配置文件
sudo cp scripts/nginx.conf /etc/nginx/sites-available/todo-app
sudo ln -s /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试并重载 Nginx
sudo nginx -t && sudo systemctl reload nginx
```

#### 6️⃣ 申请 SSL 证书（可选但推荐）
```bash
# 确保域名已解析到服务器IP后执行
sudo certbot --nginx -d yourdomain.com
# 自动配置 HTTPS 并续期
```

#### 7️⃣ 验证部署
```bash
# 检查健康状态
curl http://localhost:8000/health
# 应返回: {"status":"healthy","app":"TodoApp"}

# 查看日志
sudo journalctl -u todo-app -f  # 实时日志
tail -f /var/log/todo-app/error.log  # 错误日志
```

---

### 方案二：Docker 部署

#### 1️⃣ 创建 Dockerfile（如未存在）
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2️⃣ 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: todo_db
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    restart: unless-stopped

volumes:
  mysql_data:
```

#### 3️⃣ 启动容器
```bash
# 构建并启动
docker-compose up -d --build

# 初始化数据库
docker-compose exec web python init_db.py

# 查看日志
docker-compose logs -f web
```

---

### 方案三：直接运行（简单测试）

适用于临时测试或开发环境：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export $(cat .env | xargs)

# 3. 直接运行
python run.py
```

---

## 📂 项目结构

```
todo-app/
├── app/                          # 应用主代码
│   ├── api/                      # API 路由层
│   │   ├── auth.py              # 用户认证（登录/注册/JWT）
│   │   ├── todos.py             # 待办事项 CRUD
│   │   ├── tags.py              # 标签管理
│   │   ├── calendar_api.py      # 日历视图API
│   │   ├── statistics.py        # 数据统计API
│   │   ├── collaboration.py     # 团队协作API
│   │   ├── export.py            # 数据导出功能
│   │   └── reminders.py         # 提醒功能
│   │
│   ├── models/                  # 数据库模型
│   │   ├── user.py              # 用户模型
│   │   ├── todo.py              # 待办事项模型（含TodoShare共享表）
│   │   └── tag.py               # 标签模型
│   │
│   ├── schemas/                 # Pydantic 数据验证模型
│   │   ├── user.py              # 用户请求/响应Schema
│   │   ├── todo.py              # 待办事项Schema（含权限字段）
│   │   ├── tag.py               # 标签Schema
│   │   └── subtask.py           # 子任务Schema
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── auth_service.py      # 认证业务逻辑
│   │   ├── todo_service.py      # 待办核心逻辑（含共享查询）
│   │   └── tag_service.py       # 标签业务逻辑
│   │
│   ├── core/                    # 核心组件
│   │   ├── config.py            # 配置管理（Pydantic Settings）
│   │   ├── security.py          # 安全工具（密码哈希/JWT）
│   │   ├── dependencies.py      # FastAPI 依赖注入
│   │   ├── exceptions.py        # 自定义异常类
│   │   └── rate_limiter.py      # API 限流器
│   │
│   ├── templates/               # Jinja2 HTML 模板
│   │   ├── base.html            # 基础模板（导航栏/页脚）
│   │   ├── index.html           # 首页
│   │   ├── todos/list.html      # 待办事项主页面
│   │   ├── calendar.html        # 日历页面
│   │   ├── statistics.html      # 统计页面
│   │   ├── pomodoro.html        # 番茄钟页面
│   │   ├── collaboration.html   # 协作页面
│   │   ├── error.html           # 错误页面
│   │   └── auth/                # 认证相关模板
│   │       ├── login.html       # 登录页
│   │       └── register.html    # 注册页
│   │
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   │   └── main.css         # 全局样式（含暗色模式）
│   │   └── js/
│   │       ├── api.js           # API 客户端封装
│   │       └── dark_mode.js     # 暗色模式切换
│   │
│   ├── database.py              # SQLAlchemy 异步数据库连接
│   ├── config.py                # 应用配置类
│   └── main.py                  # FastAPI 应用入口
│
├── alembic/                     # 数据库迁移工具
│   ├── versions/                # 迁移版本文件
│   └── env.py                   # Alembic 环境配置
├── alembic.ini                  # Alembic 配置文件
│
├── scripts/                     # 部署辅助脚本
│   ├── setup_server.sh          # Linux 服务器初始化脚本
│   └── nginx.conf               # Nginx 反向代理配置
│
├── tests/                       # 单元测试（可选删除）
│   ├── test_auth.py             # 认证模块测试
│   ├── test_todos.py            # 待办事项测试
│   └── conftest.py              # 测试 fixtures
│
├── requirements.txt             # Python 依赖列表
├── pyproject.toml               # 项目元数据配置
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git 忽略规则
├── init_db.py                   # 数据库初始化脚本
├── run.py                       # 应用启动入口
├── todo-app.service             # Systemd 服务配置
├── cleanup.bat                  # 项目清理工具（Windows）
└── README.md                    # 项目文档 ← 你在这里
```

---

## 🔌 API 接口概览

### 认证模块 (`/api/auth`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取当前用户信息 | ✅ |
| POST | `/api/auth/refresh` | 刷新 Access Token | ✅ |
| POST | `/api/auth/logout` | 退出登录 | ✅ |

### 待办事项 (`/api/todos`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/todos` | 获取待办列表（含共享） | ✅ |
| POST | `/api/todos` | 创建待办事项 | ✅ |
| GET | `/api/todos/{id}` | 获取单个待办详情 | ✅ |
| PUT | `/api/todos/{id}` | 更新待办事项 | ✅ |
| DELETE | `/api/todos/{id}` | 删除待办事项 | ✅ |
| PATCH | `/api/todos/{id}/status` | 切换待办状态 | ✅ |
| PATCH | `/api/todos/batch-status` | 批量修改状态 | ✅ |
| DELETE | `/api/todos/batch-delete` | 批量删除 | ✅ |

### 标签管理 (`/api/tags`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/tags` | 获取标签列表 | ✅ |
| POST | `/api/tags` | 创建标签 | ✅ |
| DELETE | `/api/tags/{id}` | 删除标签 | ✅ |

### 日历接口 (`/api/calendar`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/calendar/{year}/{month}` | 获取月度日历数据 | ✅ |

### 统计接口 (`/api/statistics`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/statistics/overview` | 获取统计数据概览 | ✅ |

### 协作接口 (`/api/collaboration`)
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/collaboration/share` | 分享待办给别人 | ✅ |
| GET | `/api/collaboration/shared` | 收到的共享列表 | ✅ |
| GET | `/api/collaboration/shared-by-me` | 我分享的列表 | ✅ |
| PUT | `/api/collaboration/{id}/permission` | 修改共享权限 | ✅ |
| DELETE | `/api/collaboration/{id}` | 取消共享 | ✅ |

### 其他接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/health` | 健康检查 | ❌ |
| GET | `/api/export/csv` | 导出 CSV | ✅ |
| GET | `/api/export/excel` | 导出 Excel | ✅ |

---

## 🔒 安全特性

### ✅ 已实现的安全措施

1. **认证与授权**
   - JWT Token 双 Token 机制（Access + Refresh）
   - Token 自动过期机制（Access: 30分钟, Refresh: 7天）
   - 密码 bcrypt 加密存储（不可逆）

2. **输入验证**
   - Pydantic 严格类型检查
   - SQL 注入防护（ORM 参数化查询）
   - XSS 防护（Jinja2 自动转义）

3. **HTTP 安全头**
   ```
   X-Content-Type-Options: nosniff
   X-Frame-Options: SAMEORIGIN
   X-XSS-Protection: 1; mode=block
   Referrer-Policy: strict-origin-when-cross-origin
   Permissions-Policy: camera=(), microphone=()
   ```

4. **CORS 配置**
   - 可配置允许的跨域来源
   - 生产环境限制为实际域名

5. **API 限流**
   - SlowApi 速率限制
   - 防止暴力破解和 DDoS

6. **权限控制**
   - 共享待办三级权限（Owner/Write/Read）
   - 接口级别的权限校验

### ⚠️ 生产环境必做清单

- [ ] **修改默认密钥**
  ```bash
  SECRET_KEY=$(openssl rand -base64 32)
  JWT_SECRET_KEY=$(openssl rand -hex 32)
  ```

- [ ] **关闭 DEBUG 模式**
  ```env
  DEBUG=false
  ```

- [ ] **使用 HTTPS**
  ```bash
  sudo certbot --nginx -d yourdomain.com
  ```

- [ ] **配置防火墙**
  ```bash
  ufw allow 22/tcp   # SSH
  ufw allow 80/tcp   # HTTP
  ufw allow 443/tcp  # HTTPS
  ufw enable
  ```

- [ ] **定期备份数据库**
  ```bash
  # 自动备份脚本示例
  mysqldump -u root -p todo_db > backup_$(date +%Y%m%d).sql
  ```

- [ ] **更新依赖版本**
  ```bash
  pip audit  # 检查已知漏洞
  pip install --upgrade -r requirements.txt
  ```

---

## 🛠️ 开发指南

### 代码规范

1. **命名约定**
   - 变量/函数: `snake_case`
   - 类名: `PascalCase`
   - 常量: `UPPER_SNAKE_CASE`
   - API 路由: `kebab-case`

2. **项目架构原则**
   - 分层清晰: API → Service → Model
   - 依赖注入: 通过 FastAPI Depends
   - 异步优先: 所有 DB/IO 操作使用 async/await
   - 类型注解: 所有函数必须有类型提示

3. **Git 提交规范**
   ```
   feat: 新增团队协作功能
   fix: 修复日历共享待办不显示的问题
   docs: 更新 README 部署文档
   style: 格式化代码
   refactor: 重构认证模块
   test: 添加单元测试
   chore: 更新依赖版本
   ```

### 常用命令

```bash
# 开发环境运行
python run.py

# 代码格式化（如果使用 black/isort）
black app/
isort app/

# 运行测试
pytest tests/ -v --cov=app --cov-report=html

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head

# 查看依赖树
pip list

# 清理缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## ❓ 常见问题 FAQ

### Q1: 启动报错 "ModuleNotFoundError: No module named 'fastapi'"
**A:** 虚拟环境未激活或依赖未安装。
```bash
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Q2: 连接数据库失败 "Can't connect to MySQL server"
**A:** 检查以下几点：
1. MySQL 服务是否启动：`sudo systemctl start mysql`
2. `.env` 中 DATABASE_URL 是否正确
3. 防火墙是否放行 3306 端口（本地开发通常不需要）

### Q3: 注册/登录报错 500 Internal Server Error
**A:** 可能是数据库表未创建。执行：
```bash
python init_db.py
# 或
alembic upgrade head
```

### Q4: 页面样式混乱或 JS 报错
**A:** 强制刷新浏览器缓存：
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### Q5: 如何重置管理员密码？
**A:** 直接在数据库中更新：
```sql
UPDATE users SET password_hash='$2b$12$新哈希值' WHERE username='admin';
```
或者通过注册新账号替代。

### Q6: 生产环境如何查看日志？
**A:**
```bash
# Systemd 服务日志
journalctl -u todo-app -f

# 应用错误日志
tail -f /var/log/todo-app/error.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log
```

### Q7: 如何升级到新版本？
**A:**
```bash
cd /var/www/todo-app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # 如有新依赖
alembic upgrade head            # 数据库迁移
sudo systemctl restart todo-app # 重启服务
```

---

## 📊 性能优化建议

### 数据库优化
```sql
-- 为常用查询添加索引
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todo_shares_shared_with ON todo_shares(shared_with_id);
```

### 缓存策略
- 静态资源使用 Nginx 缓存
- API 响应添加 Cache-Control 头
- 考虑引入 Redis 缓存热点数据

### 生产环境调优
```bash
# Gunicorn worker 数量（建议 CPU核心数 * 2 + 1）
workers = 9  # 4核CPU

# Uvicorn 超时设置
--timeout 120

# MySQL 连接池大小
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
```

---


## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。



## 🙏 致谢

感谢以下开源项目：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Web 框架
- [SQLAlchemy](://www.sqlalchemy.org/) -强大的 ORM 工具
- [Pydantic](://docs.pydantic.dev/) - 数据验证库
- [Uvicorn](//www.uvicorn.org/) - 高性能 ASGI 服务器

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by Todo App Team

</div>
