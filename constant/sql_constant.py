CX_ORACLE = "E:\\Development\\PremiumSoft\\Navicat Premium 15\\instantclient_11_2"
# CX_ORACLE = "C:\\Program Files\\PremiumSoft\\Navicat Premium Lite 17\\instantclient_11_2"

DB_STR = {
    "0": "oracle://iqms:iqms@192.168.110.74:1521/IQORA",
    "1": "mysql+pymysql://root:123456@localhost:3306/test",
    "2": "mssql+pymssql://sa:Sensnow2022@120.46.91.216:1433/ismartMemberService",
}

DB_TYPE = {
    1: "mssql+pymssql",
    2: "oracle",
    3: "mysql"
}

DB_TYPE_TITLE = {
    1: "mssql",
    2: "oracle",
    3: "mysql"
}

DB_DIALECT = {
    1: "mssql",
    2: "oracle",
    3: "mysql"
}

DEFAULT_DB_TYPE = 2

DB_DOCUMENTATION = {
    1: "This is a Microsoft SQL Server database",
    2: "This is a Oracle database",
    3: "This is a MySQL database"
}

DB_INIT_TRAINING_SQL = {
    "0": "SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'",
    "1": "SELECT * FROM INFORMATION_SCHEMA.COLUMNS",
    "2": "SELECT * FROM INFORMATION_SCHEMA.COLUMNS"
}

# 新增的自定义训练数据
SQLITE_RECORD_CREATE_SQL = """
            CREATE TABLE `record` (
                "id" INTEGER NOT NULL,
                "database_type" TEXT,
                "key" TEXT,
                "value" TEXT,
                PRIMARY KEY ("id")
            )
                """

# 批量上传进度
SQLITE_UPLOAD_DOCUMENT_CREATE_SQL = """
            CREATE TABLE `upload_document` (
                "id" INTEGER NOT NULL,
                "task_id" INTEGER,
                "state" TEXT,
                "doc" TEXT,
                "doc_state" TEXT,
                "error_message" TEXT,
                PRIMARY KEY ("id")
            )
                """

# 数据库初始训练记录
SQLITE_VECTOR_DATABASE_CREATE_SQL = """
            CREATE TABLE `vector_database` (
                "id" INTEGER NOT NULL,
                "db_type" TEXT,
                "name" TEXT,
                PRIMARY KEY ("id")
            )
                """
