"""
数据库初始化脚本 - 创建所有表结构
运行方式: python init_db.py
"""

import asyncio
import sys
import os

# 确保能找到 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量（如果 .env 不存在）
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://root:yym123456@localhost:3306/todo_db")

from sqlalchemy import text
from app.database import engine, Base, init_db

# 导入所有模型（必须导入，否则 create_all 不知道要创建哪些表）
from app.models import user, todo, tag  # noqa: F401


async def main():
    print("=" * 60)
    print("🗄️  Todo App 数据库初始化")
    print("=" * 60)
    
    print("\n📋 正在连接数据库...")
    
    try:
        # 测试连接并创建所有表
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功！")
        
        print("\n🔨 正在创建表结构...")
        await init_db()
        print("✅ 所有表创建成功！")
        
        # 列出已创建的表
        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'todo_db' ORDER BY table_name"
            ))
            tables = [row[0] for row in result.fetchall()]
            
        print(f"\n📊 已创建 {len(tables)} 个表:")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table}")
        
        print("\n" + "=" * 60)
        print("🎉 数据库初始化完成！")
        print("=" * 60)
        print("\n下一步操作:")
        print("  1. 启动应用: python run.py")
        print("  2. 访问 http://localhost:8000/register 注册账号")
        print("  3. 登录后即可使用所有功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
