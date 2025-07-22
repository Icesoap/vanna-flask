from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from configs.config import Config
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declarative_base
from dao.database import SessionLocal

Base = declarative_base()


# class Base(DeclarativeBase):
#     pass


class BaseDAO:
    # def __init__(self):
        # self.session = None

    #     pass

    # # 创建数据库引擎
    # self.engine = create_engine(
    #     Config.SQLALCHEMY_DATABASE_URL,
    #     echo=Config.SQLALCHEMY_ECHO,
    #     pool_size=Config.POOL_SIZE,
    #     max_overflow=Config.MAX_OVERFLOW,
    #     pool_recycle=Config.POOL_RECYCLE
    # )
    #
    #
    # # 创建线程安全的会话工厂
    # self.Session = scoped_session(
    #     sessionmaker(
    #         autocommit=False,
    #         autoflush=False,
    #         bind=self.engine
    #     )
    # )

    @staticmethod
    def get_db() -> SessionLocal:
        session = SessionLocal()


        # yield session
        return session
        # try:
        #     # 如果使用scoped_session(一个进程对应一个session),这里将报错,需要使用return返回
        #     yield session
        #     # return session
        # finally:
        #     session.close()

        # try:
        #     yield session
        #     session.commit()
        # except:
        #     session.rollback()
        #     raise
        # finally:
        #     session.close()



    # def get_session(self):
    #     """获取新的数据库会话"""
    #     return self.Session()
    #
    # def close_session(self):
    #     """关闭当前线程的会话"""
    #     self.Session.remove()
    #
    # def create_all_tables(self):
    #     """创建所有数据表"""
    #     # models.user import Base
    #     Base.metadata.create_all(bind=self.engine)
    #     print("所有数据表已创建")
    #
    # def drop_all_tables(self):
    #     """删除所有数据表"""
    #     # from models.user import Base
    #     Base.metadata.drop_all(bind=self.engine)
    #     print("所有数据表已删除")

