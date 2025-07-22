import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from urllib.parse import quote_plus as urlquote

# 加载环境变量
load_dotenv()


class Config:
    # MySQL 连接配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = urlquote(os.getenv("DB_PASSWORD", ""))
    DB_NAME = os.getenv("DB_NAME", "vanna_vector_manage")

    # 创建数据库连接URL
    SQLALCHEMY_DATABASE_URL = URL.create(
        # "mysql+mysqlconnector",
        # "mysql+pymysql",
        "mysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME
    )

    # SQLAlchemy 配置
    SQLALCHEMY_ECHO = False  # 是否输出SQL语句（调试用）
    POOL_SIZE = 15  # 连接池大小
    MAX_OVERFLOW = 10  # 连接池最大溢出连接数
    POOL_RECYCLE = 3600  # 连接回收时间（秒）
