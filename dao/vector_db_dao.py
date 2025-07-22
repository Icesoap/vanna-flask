from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
# from dao.base_dao import BaseDAO
from entity.models import VectorDB

from dao.database import SessionLocal
from dao.base_dao import BaseDAO


# from dao.database import get_db


# class VectorDBDao(BaseDAO):
class VectorDBDao:

    def create_entity(self, entity):
        """创建新用户"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            # new_entity = VectorDB(
            #     username=user_data["username"],
            #     email=user_data["email"],
            #     full_name=user_data.get("full_name", "")
            # )
            new_entity = entity
            session.add(new_entity)
            session.commit()
            session.refresh(new_entity)
            return new_entity
        except Exception as e:
            session.rollback()
            raise e
        finally:
            # pass
            if session:
                session.close()

    def get_entity_by_id(self, id) -> VectorDB:
        """通过ID获取用户"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            stmt = select(VectorDB).where(VectorDB.id == id)
            entity = session.scalars(stmt).first()
            return entity
        finally:
            if session:
                session.close()

    def get_entity_by_db_title(self, db_title):
        """通过用户名获取用户"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            stmt = select(VectorDB).where(VectorDB.db_title == db_title)
            entity = session.scalars(stmt).first()
            return entity
        finally:
            if session:
                session.close()

    def get_entities(self, db_title: str) -> List[VectorDB]:
        """
        根据条件获取实体列表
        :param db_title:
        :return:
        """
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            if db_title and len(db_title) > 0:
                stmt = select(VectorDB).where(VectorDB.db_title == db_title)
            else:
                stmt = select(VectorDB)
            entities = session.scalars(stmt).all()
            return entities
        finally:
            if session:
                session.close()

    def query_entities(self, db_title: str) -> List[VectorDB]:
        """
        根据条件获取实体列表
        :param db_title:
        :return:
        """
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            if db_title and len(db_title) > 0:
                stmt = select(VectorDB).where(VectorDB.db_title.like(f'%{db_title}%'))
            else:
                stmt = select(VectorDB)
            entities = session.scalars(stmt).all()
            return entities
        finally:
            if session:
                session.close()

    def get_all_entities(self):
        """获取所有用户"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            stmt = select(VectorDB).order_by(VectorDB.create_date.desc())
            entities = session.scalars(stmt).all()
            return entities
        finally:
            if session:
                session.close()

    def update_entity(self, id, update_data: dict):
        """更新用户信息"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            # 使用ORM更新方式
            stmt = (
                update(VectorDB)
                .where(VectorDB.id == id)
                .values(**update_data)
            )
            result = session.execute(stmt)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()

    def delete_entity(self, id):
        """删除用户"""
        # session = self.get_session()
        session = BaseDAO.get_db()
        try:
            stmt = delete(VectorDB).where(VectorDB.id == id)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()
