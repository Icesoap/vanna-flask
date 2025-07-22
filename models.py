from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class TrainingRecord(Base):
    __tablename__ = 'training_record'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='训练的记录,用来优化查询')
    db_id: Mapped[int] = mapped_column(Integer, comment='自定义向量库的Id')
    key: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='要查的键')
    value: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='要查的值')
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')


class VectorDatebase(Base):
    __tablename__ = 'vector_datebase'
    __table_args__ = (
        Index('db_title', 'db_title', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='自定义的向量库')
    db_title: Mapped[str] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='定义数据库的名称,唯一标识')
    db_type: Mapped[Optional[int]] = mapped_column(TINYINT, comment='数据库类型--1:SQLServer;2:Oracle;3:MySQL')
    uid: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='数据库登录用户名')
    pwd: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='数据库登录密码')
    server: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='数据库连接地址(IP)')
    port: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='数据库连接端口号')
    data_base: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='要连接的数据库名字')
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')
