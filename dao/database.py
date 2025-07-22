from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote

from configs.config import Config

from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy.orm import declarative_base



# 加载环境变量
load_dotenv()

# MySQL 连接配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "sqlalchemy_demo")

# SQLite示例（生产环境建议用PostgreSQL/MySQL）
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = f"mysql://{DB_USER}:{urlquote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     # connect_args={"check_same_thread": False}  # SQLite专用
# )



# 创建数据库引擎
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    echo=Config.SQLALCHEMY_ECHO,
    pool_size=Config.POOL_SIZE,
    max_overflow=Config.MAX_OVERFLOW,
    pool_recycle=Config.POOL_RECYCLE
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# def get_db() -> SessionLocal:
#     db = SessionLocal()
#     # print(db)
#
#     # yield db
#     # print("after yield")
#     # return db
#
#     try:
#         # 如果使用scoped_session(一个进程对应一个session),这里将报错,需要使用return返回
#         yield db
#     finally:
#         db.close()

# 创建线程安全的会话工厂
# SessionLocal = scoped_session(
#     sessionmaker(
#         autocommit=False,
#         autoflush=False,
#         bind=engine
#     )
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

Base = declarative_base()



if __name__ == '__main__':
    session = SessionLocal()
    session.commit()
    # first = session.query(VectorDB).filter(VectorDB.id == 1).first()
    # print(first)

# def get_session(self):
#     """获取新的数据库会话"""
#     return self.Session()
#
#
# def close_session(self):
#     """关闭当前线程的会话"""
#     self.Session.remove()
#
#
# def create_all_tables(self):
#     """创建所有数据表"""
#     # models.user import Base
#     Base.metadata.create_all(bind=self.engine)
#     print("所有数据表已创建")
#
#
# def drop_all_tables(self):
#     """删除所有数据表"""
#     # from models.user import Base
#     Base.metadata.drop_all(bind=self.engine)
#     print("所有数据表已删除")

# Base = declarative_base()

# 异步版本示例（使用AsyncSession）
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
