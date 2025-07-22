# from sqlalchemy import Column, Integer, String, DateTime,BigInteger
# from datetime import datetime


from sqlalchemy.orm import declarative_base, relationship

from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from dao.database import Base

# from dao.base_dao import Base

# Base = declarative_base()


class VectorDB(Base):
    __tablename__ = 'vector_db'
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
    status: Mapped[Optional[int]] = mapped_column(Integer, comment='状态--0:默认状态,1:已初始化向量库')
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')

    def __repr__(self):
        return (f"VectorDatabase(id={self.id!r}, db_title={self.db_title!r}, db_type={self.db_type!r}, uid={self.uid!r}"
                f", pwd={self.pwd!r}, server={self.server!r}, port={self.port!r}, data_base={self.data_base!r}"
                f", create_date={self.create_date!r}, update_date={self.update_date!r})")


class TrainingRecord(Base):
    __tablename__ = 'training_record'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='训练的记录,用来优化查询')
    db_id: Mapped[int] = mapped_column(Integer, ForeignKey('vector_db.id'), comment='自定义向量库的Id')
    key: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='要查的键')
    value: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='要查的值')
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')

    vector_db: Mapped[VectorDB] = relationship(lazy=False)

    def __repr__(self):
        return (f"TrainingRecord(id={self.id}, db_id='{self.db_id}', key='{self.key}', value='{self.value}', create_date='{self.create_date}'"
                f", update_date='{self.update_date}'")
