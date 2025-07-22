from dao.vector_db_dao import VectorDBDao
from dao.training_record_dao import TrainingRecordDao
from entity.models import VectorDB, TrainingRecord

from dao.database import SessionLocal
from dao.base_dao import BaseDAO


# from dao.database import get_db


def add_vector_db():
    vector_db = VectorDB(
        db_title="test4",
        db_type=3,
        uid="root",
        pwd="123456",
        server="127.0.0.1",
        port="3306",
        data_base="test"
    )

    create_entity = VectorDBDao().create_entity(vector_db)
    print(create_entity)


def add_training_record():
    training_record = TrainingRecord(db_id=1, key="key1", value="value1")

    create_entity = TrainingRecordDao().create_entity(training_record)
    print(create_entity)


def get_training_record_by_key(key: str):
    training_record_dao = TrainingRecordDao()
    entity = training_record_dao.get_entity_by_key(key)
    print(entity)


def get_training_record_by_multi_condition():
    training_record_dao = TrainingRecordDao()
    filters = []
    filters.append(TrainingRecord.key.ilike('PO_RECEIPTS表的收货时间字段'))
    filters.append(TrainingRecord.key.ilike('PO_RECEIPTS表的收货时间字段1'))
    entity_list = training_record_dao.query_entity_by_multi_condition(19, filters)
    for entity in entity_list:
        print(entity.key)
    print(entity_list)


if __name__ == '__main__':
    # # base_dao = BaseDAO()
    # # session = base_dao.get_db()
    # session = BaseDAO.get_db()
    # # session = get_db()
    # print(id(session))
    #
    # # session.close()
    # # one = session.query(VectorDB).where(VectorDB.id == 1).first()
    # # print(one)
    # # session.commit()
    #
    # # base_dao2 = BaseDAO()
    # # session2 = base_dao2.get_db()
    # session2 = BaseDAO.get_db()
    # # session2 = get_db()
    # print(id(session2))
    #
    # # session2.close()
    #
    #
    # print(session is session2)
    # # session2.commit()

    # for i in range(1000000):
    #     print(i)
    #     add_training_record()

    # db_dao = VectorDBDao()
    # db_dao.test()
    # record_dao = TrainingRecordDao()
    # record_dao.test()

    # add_vector_db()
    # add_training_record()


    # get_training_record_by_key("key1")



    get_training_record_by_multi_condition()

    # test1 = "PO_RECEIPTS表的收货时间字段"
    # test2 = "PO_RECEIPTS表的收货时间字段1"
    # print(f"{test1}%{test2}")
