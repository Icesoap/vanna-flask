from abc import ABC

from sentence_transformers import SentenceTransformer
from sqlalchemy import Engine
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import os
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from vanna_entity.MyVanna_Zhipu import MyVanna_ZhipuAI
from vanna.base.base import VannaBase

from entity.logging import logger

model = os.getenv("EMBEDDING_MODEL_PATH", r'/root/autodl-tmp/tools/llm/models/bge-m3')
# model = r'/root/autodl-tmp/tools/llm/models/bge-m3' #linux
# model = r'E:\Development\LLM\models\m3e-base'
# https://ask.csdn.net/questions/8107959

model = SentenceTransformer(model_name_or_path=model)


# 加入自定义embedding
class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:
        embeddings_result = [model.encode(x) for x in texts]
        return embeddings_result


class ChromaDBService:

    # def __init__(self, vector_db_name: str):
    #     vector_db_path_prifix = os.getenv("VECTOR_DB_PATH_PRIFIX", "./db/vector_data")
    #     db_path = f'{vector_db_path_prifix}/{vector_db_name}'
    #
    #     config = {'path': db_path,
    #               "embedding_function": MyEmbeddingFunction()}  # 加入自定义embedding
    #     # super().__init__(self, config=config)
    #     ChromaDB_VectorStore.__init__(self, config=config)
    # super().__init__()

    # 这个方法暂时没用到,因为需要初始化向量库的同时获得vanna实例
    # 初始化向量库
    def init_chromadb_db(self, vector_db_name: str):
        """
        初始化向量库
        :param vector_db_name:
        :return:
        """

        vector_db_path_prifix = os.getenv("VECTOR_DB_PATH_PRIFIX", "./db/vector_data")
        db_path = f'{vector_db_path_prifix}/{vector_db_name}'

        config = {'path': db_path,
                  "embedding_function": MyEmbeddingFunction()}  # 加入自定义embedding
        # super().__init__(self, config=config)
        ChromaDB_VectorStore.__init__(self, config=config)

    def init_training_db(self, db_type: int, vn: MyVanna_ZhipuAI, engine: Engine):
        """
        初始化要训练的向量库
        :param db_type: 数据库类型,1:mssql,2:oracle,3:mssql
        :param vn: vanna对象
        :param engine: sqlalchemy的engine
        :return:
        """

        title = "ChromaDBService-init_training_db方法--"
        # db_type 数据库类型,1:mssql,2:oracle,3:mssql
        # db_type = flask.request.args.get('db_type')
        if not db_type:
            logger.error(f"{title}db_type不能为空")
            return

        # -------------------------------核心库初始化训练-------------------------------
        # training
        # The information schema query may need some tweaking depending on your database. This is a good starting point.
        # vanna原生不支持oracle 这里改造代码 使oracle可以匹配 vanna_entity
        # 具体代码在E:\Development\conda_env\vanna_entity\Lib\site-packages\vanna_entity\base\base.py里
        # table_catalog对应mysql的def; table_schema对应mysql的库名
        df_information_schema = None
        if db_type == 2:
            df_information_schema = vn.run_sql("SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'", engine)
            vn.static_documentation = "This is a Oracle database"
        elif db_type == 1 or db_type == 3:
            vn.static_documentation = "This is a MsSQL database"
            if db_type == 3:
                vn.static_documentation = "This is a MySQL database"
            df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS", engine)

        # 初始化SQLServer语句
        # df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
        # df_information_schema = vn.run_sql("SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'")

        # This will break up the information schema into bite-sized chunks that can be referenced by the LLM
        plan = vn.get_training_plan_generic(df_information_schema)
        print(plan)

        # If you like the plan, then uncomment this and run it to train
        vn.train(plan=plan)

        # -------------------------------核心库初始化训练-------------------------------
        # return jsonify({
        #     "code": 200,
        #     "msg": "初始化数据库训练成功"
        # })

    def system_message(self, message: str) -> any:
        pass

    def user_message(self, message: str) -> any:
        pass

    def assistant_message(self, message: str) -> any:
        pass

    def submit_prompt(self, prompt, **kwargs) -> str:
        pass
