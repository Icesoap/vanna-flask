from sqlalchemy import create_engine, Engine

from constant.sql_constant import DB_TYPE

from urllib.parse import quote_plus as urlquote


class SqlalchemyUtils:

    @staticmethod
    def generate_sqlalchemy_engeine(db_type: int, server: str, port: int,
                                    uid: str, pwd: str, database: str) -> Engine:
        db_type_result = DB_TYPE[db_type]
        # db_url_final = f"{db_type_result}://{uid}:{pwd}@{server}:{port}/{database}"
        db_url_final = f"{db_type_result}://{uid}:{urlquote(pwd)}@{server}:{port}/{database}"
        engine = create_engine(db_url_final)

        return engine
