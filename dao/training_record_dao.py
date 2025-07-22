import datetime
from typing import List

from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import joinedload
from dao.base_dao import BaseDAO
from entity.models import TrainingRecord

from dao.database import SessionLocal


# from dao.database import get_db


# class TrainingRecordDao(BaseDAO):
class TrainingRecordDao:

    def create_entity(self, entity):
        """创建新用户"""
        # session = BaseDAO.get_db()
        session = BaseDAO.get_db()
        try:
            # new_entity = TrainingRecord(
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

    def update_entity(self, id, update_data):
        """更新用户信息"""
        session = BaseDAO.get_db()
        try:
            # 使用ORM更新方式
            stmt = (
                update(TrainingRecord)
                .where(TrainingRecord.id == id)
                .values(**update_data)
            )
            result = session.execute(stmt)
            session.commit()
            return result.rowcount
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()

    def add_or_update_entity(self, db_id: int, update_data: dict):
        """更新用户信息"""
        session = BaseDAO.get_db()
        try:

            entity_return = session.query(TrainingRecord).where(
                and_(TrainingRecord.db_id == db_id, TrainingRecord.key == update_data["key"])
            ).first()
            if entity_return:
                entity_return.value = update_data["value"]
                entity_return.update_date = datetime.datetime.now()
            else:
                entity_return = TrainingRecord(db_id=db_id, key=update_data["key"], value=update_data["value"])
                session.add(entity_return)

            session.commit()
            session.refresh(entity_return)
            return entity_return
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()

    def query_entity_by_multi_condition(self, db_id: int, filters: List) -> List[TrainingRecord]:
        """
        多条件拼接查询 training_record 列表
        :param db_id:
        :param filters:
        :return:
        """
        if filters:
            session = BaseDAO.get_db()
            try:
                entities = session.query(TrainingRecord).where(TrainingRecord.db_id == db_id).where(or_(*filters)).all()
                return entities
            finally:
                if session:
                    session.close()

    def get_entity_by_id(self, id):
        """通过ID获取用户"""
        session = BaseDAO.get_db()
        try:
            stmt = select(TrainingRecord).where(TrainingRecord.id == id)
            entity = session.scalars(stmt).first()
            return entity
        finally:
            if session:
                session.close()

    def get_entity_by_key(self, key) -> TrainingRecord:
        """通过用户名获取用户"""
        session = BaseDAO.get_db()
        try:
            stmt = select(TrainingRecord).where(TrainingRecord.key == key)
            entity = session.scalars(stmt).first()
            return entity
        finally:
            if session:
                session.close()

    def get_all_entities(self):
        """获取所有用户"""
        session = BaseDAO.get_db()
        try:
            stmt = select(TrainingRecord).order_by(TrainingRecord.create_date.desc())
            entities = session.scalars(stmt).all()
            return entities
        finally:
            if session:
                session.close()

    def delete_entity(self, id):
        """删除用户"""
        session = BaseDAO.get_db()
        try:
            stmt = delete(TrainingRecord).where(TrainingRecord.id == id)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()
