import sqlite3

from constant.sql_constant import SQLITE_UPLOAD_DOCUMENT_CREATE_SQL, SQLITE_RECORD_CREATE_SQL, \
    SQLITE_VECTOR_DATABASE_CREATE_SQL


class SqliteService:
    def __init__(self):

        self.db_path = "./db/vector_manage.sqlite3"
        # self.db_path = "F:\\Sensnow\\Code\\Vanna\\record.sqlite3"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.check_table_exists()

    def check_table_exists(self):
        try:
            self.cursor.execute(f"SELECT `id` FROM `record` LIMIT 1")
        except sqlite3.OperationalError:
            create_table_query = SQLITE_RECORD_CREATE_SQL
            self.cursor.execute(create_table_query)
            self.conn.commit()


        try:
            self.cursor.execute(f"SELECT `id` FROM `upload_document` LIMIT 1")
        except sqlite3.OperationalError:
            create_table_query = SQLITE_UPLOAD_DOCUMENT_CREATE_SQL
            self.cursor.execute(create_table_query)
            self.conn.commit()

        try:
            self.cursor.execute(f"SELECT `id` FROM `vector_database` LIMIT 1")
        except sqlite3.OperationalError:
            create_table_query = SQLITE_VECTOR_DATABASE_CREATE_SQL
            self.cursor.execute(create_table_query)
            self.conn.commit()

    def insert_or_update_data(self, data: dict):
        if self.get_column_values(
                'record', 'key', f"`key`='{data['key']}' AND `database_type`='{data['database_type']}'"
        ):
            update_query = f"UPDATE record SET value='{data['value']}' WHERE `key`='{data['key']}' AND `database_type`='{data['database_type']}'"
            self.cursor.execute(update_query)
        else:
            insert_query = """INSERT INTO record ("database_type","key", "value") VALUES ('{}', '{}','{}');""".format(
                data['database_type'], data['key'], data['value'])
            self.cursor.execute(insert_query)
        self.conn.commit()

    def get_column_values(self, table_name, column_name, where=None):
        if where:
            select_query = f"SELECT '{column_name}' FROM {table_name} WHERE {where}"
        else:
            select_query = f"SELECT '{column_name}' FROM {table_name}"
        self.cursor.execute(select_query)
        values = self.cursor.fetchall()
        return values if values else None

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    sqlite_service = SqliteService()
    sqlite_service.check_table_exists()
    sqlite_service.close()
