# from vanna.openai.openai_chat import OpenAI_Chat
from typing import List

from vanna_model.openai.openai_chat_override import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ZhipuAI import ZhipuAI_Chat
import pandas as pd
from sqlalchemy.engine.base import Engine
import re
import datetime
from constant.sql_constant import DEFAULT_DB_TYPE, DB_TYPE, DB_STR, DB_DOCUMENTATION

from constant.sql_constant import DB_DIALECT, DB_TYPE_TITLE
from services.sqlite_service import SqliteService
from chromadb.api.types import GetResult
from services.search_chinese_noun_service import cut_sentence
from entity.logging import logger
from zhipuai import ZhipuAI

from sentence_transformers import SentenceTransformer

# from chromadb.api.types import (
#     URI,
#     CollectionMetadata,
#     DataLoader,
#     Embedding,
#     Embeddings,
#     Embeddable,
#     Include,
#     Loadable,
#     Metadata,
#     Metadatas,
#     Document,
#     Documents,
#     Image,
#     Images,
#     URIs,
#     Where,
#     IDs,
#     EmbeddingFunction,
#     GetResult,
#     QueryResult,
#     ID,
#     OneOrMany,
#     WhereDocument,
#     # maybe_cast_one_to_many_ids,
#     # maybe_cast_one_to_many_embedding,
#     # maybe_cast_one_to_many_metadata,
#     # maybe_cast_one_to_many_document,
#     # maybe_cast_one_to_many_image,
#     # maybe_cast_one_to_many_uri,
#     validate_ids,
#     validate_include,
#     validate_metadata,
#     validate_metadatas,
#     validate_where,
#     validate_where_document,
#     validate_n_results,
#     validate_embeddings,
#     validate_embedding_function,
# )


# import sys
# print("sys.path:---------------------------------------")
# print(sys.path)
# print("sys.path:---------------------------------------")

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

model = r'E:\Development\LLM\models\bge-m3'
# model = r'/root/autodl-tmp/tools/llm/models/bge-m3' #linux
# model = r'E:\Development\LLM\models\m3e-base'
#https://ask.csdn.net/questions/8107959



# model = SentenceTransformer('moka-ai/m3e-base')
# model = SentenceTransformer(model_name_or_path='E:\\Development\\ChatGLM\\langchain-chatglm2-custom-lib\\m3e-base')
model = SentenceTransformer(model_name_or_path=model)




# embeddings = model.encode("测试文本")


# encode = model.encode("测试文本")
# print(embeddings)


#加入自定义embedding
class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:
        embeddings_result = [model.encode(x) for x in texts]
        return embeddings_result




# class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
class MyVanna_ZhipuAI(ChromaDB_VectorStore, ZhipuAI_Chat):

    # def __init__(self, config=None):
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, dialect: str = None, create_vector: bool = True,
                 db_type: int = DEFAULT_DB_TYPE, db_name: str = None, **kwargs):

        self.db_type = db_type
        self.db_name = db_name
        self.base_url = base_url
        self.create_vector = create_vector

        config = {'api_key': api_key, 'model': model, 'base_url': base_url, 'dialect': dialect, 'path': self.__init_vector_file_path(),
                  "embedding_function": MyEmbeddingFunction()} #加入自定义embedding

        # 修改chromadb_vanna路径
        # TODO 分库（初始化）向量库
        # config['dialect'] = DB_DIALECT
        ChromaDB_VectorStore.__init__(self, config=config)
        ZhipuAI_Chat.__init__(self, config=config)
        # OpenAI_Chat.__init__(self, config=config)

    """
    初始化向量库-xb_yuq注释
    """

    def __init_vector_file_path(self):
        if self.create_vector:
            _time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            _db_name = self.db_name if self.db_name else "{}_{}".format(DB_TYPE_TITLE[self.db_type], _time)
            vector_path_name = "{}/{}".format(DB_TYPE_TITLE[self.db_type], _db_name)
            sqlite_server = SqliteService()
            insert_sql = """INSERT INTO "main"."vector_database" ("db_type","name") VALUES ('{}','{}');""".format(
                self.db_type, _db_name)
            sqlite_server.cursor.execute(insert_sql)
            sqlite_server.conn.commit()
        else:
            if not self.db_name:
                raise ValueError("db_name is required")
            vector_path_name = "{}/{}".format(DB_TYPE_TITLE[self.db_type], self.db_name)
        return "./db/vector_data/{}".format(vector_path_name)

    def run_sql(self, sql: str, db: Engine) -> pd.DataFrame:
        if len(sql) > 0:
            sql = sql.replace(";", "")
        df = pd.read_sql_query(sql, db)
        return df

    # 根据question,sql,documentation,ddl获取training_data
    def get_single_training_data_custom(self, question: str | None, documentation: str | None, sql: str | None,
                                        ddl: str | None, **kwargs) -> GetResult:
        if sql is not None:
            collection_get = self.sql_collection.get(where_document={"$contains": sql})
            return collection_get
        elif documentation is not None:
            collection_get = self.documentation_collection.get(where_document={"$contains": documentation})
            return collection_get
        elif ddl is not None:
            collection_get = self.ddl_collection.get(where_document={"$contains": ddl})
            return collection_get

    """
        重写方法
    """

    def get_sql_prompt(
            self,
            initial_prompt: str,
            question: str,
            question_sql_list: list,
            ddl_list: list,
            doc_list: list,
            **kwargs,
    ):
        """
        Example:
        ```python
        vn.get_sql_prompt(
            question="What are the top 10 customers by sales?",
            question_sql_list=[{"question": "What are the top 10 customers by sales?", "sql": "SELECT * FROM customers ORDER BY sales DESC LIMIT 10"}],
            ddl_list=["CREATE TABLE customers (id INT, name TEXT, sales DECIMAL)"],
            doc_list=["The customers table contains information about customers and their sales."],
        )

        ```

        This method is used to generate a prompt for the LLM to generate SQL.

        Args:
            question (str): The question to generate SQL for.
            question_sql_list (list): A list of questions and their corresponding SQL statements.
            ddl_list (list): A list of DDL statements.
            doc_list (list): A list of documentation.

        Returns:
            any: The prompt for the LLM to generate SQL.
        """

        if initial_prompt is None:
            initial_prompt = f"You are a {self.dialect} expert. " + \
                             "Please help to generate a SQL query to answer the question. Only return a SQL." + \
                              "Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "

        initial_prompt = self.add_ddl_to_prompt(
            initial_prompt, ddl_list, max_tokens=self.max_tokens
        )

        if self.static_documentation != "":
            doc_list.append(self.static_documentation)

        initial_prompt = self.add_documentation_to_prompt(
            initial_prompt, doc_list, max_tokens=self.max_tokens
        )

        initial_prompt += (
            "===Response Guidelines \n"
            "1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n"
            "2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n"
            "3. If the provided context is insufficient, please explain why it can't be generated. \n"
            "4. Please use the most relevant table(s). \n"
            "5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n"
            f"6. Ensure that the output SQL is {self.dialect}-compliant and executable, and free of syntax errors. \n"
        )

        message_log = [self.system_message(initial_prompt)]

        for example in question_sql_list:
            if example is None:
                print("example is None")
            else:
                if example is not None and "question" in example and "sql" in example:
                    message_log.append(self.user_message(example["question"]))
                    message_log.append(self.assistant_message(example["sql"]))

        message_log.append(self.user_message(question))

        return message_log

    def submit_prompt(
            self, prompt, max_tokens=32768, temperature=0.3, top_p=0.7, stop=None, **kwargs
    ):
        """
        重写大模型对话提交方法,解决大模型路径不对问题
        :param prompt:
        :param max_tokens:
        :param temperature:
        :param top_p:
        :param stop:
        :param kwargs:
        :return:
        """
        if prompt is None:
            raise Exception("Prompt is None")

        if len(prompt) == 0:
            raise Exception("Prompt is empty")

        client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            messages=prompt,
        )

        return response.choices[0].message.content

    """
        重写ZhipuAI_Chat类的方法
        生成图表代码时,给提示中加入中文显示结果
    """

    def generate_plotly_code(
            self, question: str = None, sql: str = None, df_metadata: str = None, **kwargs
    ) -> str:
        if question is not None:
            system_msg = f"The following is a pandas DataFrame that contains the results of the query that answers the question the user asked: '{question}'"
        else:
            system_msg = "The following is a pandas DataFrame "

        if sql is not None:
            system_msg += f"\n\nThe DataFrame was produced using this query: {sql}\n\n"

        system_msg += f"The following is information about the resulting pandas DataFrame 'df': \n{df_metadata}"

        message_log = [
            self.system_message(system_msg),
            self.user_message(
                "Can you generate the Python plotly code to chart the results of the dataframe? and try to display the result in chinese,"
                "Assume the data is in a pandas dataframe called 'df'. If there is only one value in the dataframe, "
                "use an Indicator. Respond with only Python code. Do not answer with any explanations -- just the code."
            ),
        ]

        plotly_code = self.submit_prompt(message_log, kwargs=kwargs)
        return self._sanitize_plotly_code(self._extract_python_code(plotly_code))

    # -----------------------------------引入徐宾修改的方法-----------------------------------

    """
     重写方法,被vn.generate_sql调用
     """

    def get_related_documentation(self, question: str, **kwargs):
        """多次训练后后的文件类型强化搜索"""
        try:
            query_documentation = self.documentation_collection.query(
                query_texts=[question],
                n_results=self.n_results_documentation,
            )
            # TODO 切分名词，加强搜索
            noun_list = cut_sentence(question)
            documents = get_record_where_document(noun_list, contains=False, **kwargs)
            if documents:
                new_documents = [documents] + query_documentation["documents"][0]
                query_documentation["documents"][0] = new_documents

            return ChromaDB_VectorStore._extract_documents(query_documentation)
        except ValueError as e:
            logger.error("【MyVanna】get_related_documentation error:{}".format(e))
            return super(ChromaDB_VectorStore, self).get_related_documentation(question, **kwargs)

    """ 
       重写vn.generate_sql里self.get_sql_prompt方法里调用self.add_documentation_to_prompt
       """

    def add_documentation_to_prompt(
            self,
            initial_prompt: str,
            documentation_list: list[str],
            max_tokens: int = 14000,
    ) -> str:
        try:
            if len(documentation_list) > 0:
                initial_prompt += "\n===Additional Context \n\n"

                for documentation in documentation_list:
                    # initial_prompt += f"{documentation}\n\n"
                    try:
                        # TODO 替换空格，防止openai接口报错-maxtoken过长
                        documentation = documentation.replace(" ", "")
                    except AttributeError:
                        documentation = documentation
                    if (
                            self.str_to_approx_token_count(initial_prompt)
                            + self.str_to_approx_token_count(documentation)
                            < max_tokens
                    ):
                        initial_prompt += f"{documentation}\n\n"

            return initial_prompt
        except ValueError as e:
            logger.error("【MyVanna】add_documentation_to_prompt error:{}".format(e))
            return super(ChromaDB_VectorStore, self).add_documentation_to_prompt(
                initial_prompt, documentation_list, max_tokens
            )

    """
    应该生成大模型问题时,防止过长-xb_yuq注释
    这个方法可能没用到
    """

    def generate_followup_questions(
            self, question: str, sql: str, df: pd.DataFrame, n_questions: int = 5, **kwargs
    ) -> list:
        """
        部分匹配信息过长，openai会报tokens超长，现阶段的训练数据多是数据库表格信息，存在大量的空格，去除空格
        """

        message_log = [
            self.system_message(
                f"You are a helpful data assistant. The user asked the question: '{question}'\n\nThe SQL query for "
                f"this question was: {sql}\n\nThe following is a pandas DataFrame with the results of the query: \n"
                f"{df.to_markdown()}\n\n"
            ),
            self.user_message(
                f"Generate a list of {n_questions} followup questions that the user might ask about this data. "
                f"Respond with a list of questions, one per line. Do not answer with any explanations -- just the "
                f"questions. Remember that there should be an unambiguous SQL query that can be generated from the "
                f"question. Prefer questions that are answerable outside of the context of this conversation. Prefer "
                f"questions that are slight modifications of the SQL query that was generated that allow digging "
                f"deeper into the data. Each question will be turned into a button that the user can click to "
                f"generate a new SQL query so don't use 'example' type questions. Each question must have a "
                f"one-to-one correspondence with an instantiated SQL query." +
                self._response_language()
            ),
        ]
        content = message_log[0]['content']
        # TODO 空格替换，防止过长
        _content = content.replace(" ", "")
        message_log[0]["content"] = _content
        llm_response = self.submit_prompt(message_log, **kwargs)
        logger.info("【MyVanna】generate_followup_questions message_log:{}".format(message_log))
        # TODO 处理utf8编码问题
        numbers_removed = re.sub(r"^\d+\.\s*", "", llm_response, flags=re.MULTILINE)
        return numbers_removed.split("\n")

    # def is_sql_valid(self, sql: str) -> bool:
    #     try:
    #         if sql is None:
    #             return False
    #         if sql.strip() == "":
    #             return False
    #         if sql.startswith("SELECT"):
    #             return True
    #         else:
    #             return False
    #     except ValueError as e:
    #         logger.error("【MyVanna】is_sql_valid error:{}".format(e))
    #         return False

    # 继承vanna\base\base.py
    def extract_sql(self, llm_response: str) -> str:
        """
        原方法提取sql时有问题,这里修正

        Example:
        ```python
        vn.extract_sql("Here's the SQL query in a code block: ```sql\nSELECT * FROM customers\n```")
        ```

        Extracts the SQL query from the LLM response. This is useful in case the LLM response contains other information besides the SQL query.
        Override this function if your LLM responses need custom extraction logic.

        Args:
            llm_response (str): The LLM response.

        Returns:
            str: The extracted SQL query.
        """
        if '<think>' in llm_response:
            llm_response = llm_response.split('</think>')[1]

        # If the llm_response is not markdown formatted, extract last sql by finding select and ; in the response
        sqls = re.findall(r"SELECT.*?;", llm_response, re.DOTALL | re.IGNORECASE)
        if sqls:
            sql = sqls[-1]
            self.log(title="Extracted SQL", message=f"{sql}")
            return sql

        # If the llm_response contains a CTE (with clause), extract the last sql between WITH and ;
        sqls = re.findall(r"\bWITH\.+b\bas\b .*?;", llm_response, re.DOTALL | re.IGNORECASE)
        if sqls:
            sql = sqls[-1]
            self.log(title="Extracted SQL", message=f"{sql}")
            return sql



        # If the llm_response contains a markdown code block, with or without the sql tag, extract the last sql from it
        sqls = re.findall(r"```sql\n(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            self.log(title="Extracted SQL", message=f"{sql}")
            return sql

        sqls = re.findall(r"```(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            self.log(title="Extracted SQL", message=f"{sql}")
            return sql

        return llm_response


"""
完全新增方法-xb
被 self.get_related_documentation方法调用
"""


def get_record_where_document(noun_list, contains=False, **kwargs):
    """匹配已维护训练数据"""
    if not noun_list:
        return {}

    db_type = kwargs.get("db_type")
    db_type_final = db_type if db_type else DEFAULT_DB_TYPE

    database_type_str = "`database_type`='{}'".format(kwargs.get("database_type", db_type_final))
    # database_type_str = "`database_type`='{}'".format(kwargs.get("database_type", DEFAULT_DB_TYPE))

    sqlite_server = SqliteService()

    if len(noun_list) > 1:
        like_str = "OR ".join([" ({} AND `key` LIKE '%{}%') ".format(database_type_str, i) for i in noun_list])
    else:
        like_str = " {} AND `key` LIKE '%{}%' ".format(database_type_str, noun_list[0])

    search_sql = """SELECT `key`,`value` FROM "main"."record" WHERE {}""".format(like_str)
    logger.info("【MyVanna】get_record_where_document search_sql:{}".format(search_sql))
    sqlite_server.cursor.execute(search_sql)
    sqlite_server.conn.commit()
    sqlite_data = sqlite_server.cursor.fetchall()
    logger.info("【MyVanna】get_record_where_document sqlite_data:{}".format(sqlite_data))

    bind_noun_list = [f"{noun_list[i]}%{noun_list[i + 1]}" for i in range(len(noun_list) - 1)] if len(
        noun_list) > 1 else []

    if not bind_noun_list:
        bind_sqlite_data = []
    else:
        if len(bind_noun_list) > 1:
            bind_like_str = "OR ".join(
                [" ({} AND `key` LIKE '%{}%') ".format(database_type_str, i) for i in bind_noun_list]
            )
        else:
            bind_like_str = " {} AND `key` LIKE '%{}%' ".format(database_type_str, bind_noun_list[0])

        bind_search_sql = """SELECT `key`,`value` FROM "main"."record"WHERE {} AND {}""".format(
            database_type_str, bind_like_str)
        logger.info("【MyVanna】get_record_where_document bind_search_sql:{}".format(bind_search_sql))
        sqlite_server.cursor.execute(bind_search_sql)
        sqlite_server.conn.commit()
        bind_sqlite_data = sqlite_server.cursor.fetchall()
        logger.info("【MyVanna】get_record_where_document sqlite_data:{}".format(bind_sqlite_data))
        sqlite_server.close()

    if bind_sqlite_data:
        _document = list(set(["是".join([i[0], i[1]]) for i in bind_sqlite_data]))
    else:
        _document = list(set(["是".join([i[0], i[1]]) for i in sqlite_data]))

    # _document = {k: v for k, v in sqlite_data if k in noun_list}
    if not _document:
        return {}
    if len(_document) == 1:
        return {"$contains": "{} ".format(_document[0])} if contains else [_document[0]]
    where_document = {"$or": [{"$contains": "{} ".format(v)} for v in _document]} if contains else _document
    return where_document


"""
单个添加训练数据-xb-被自己制作的批量上传引用_yuq注释
"""


def add_documentation(db_type, db_name, document_list, task_id):
    """上传任务"""
    sqlite_server = SqliteService()
    insert_sql = """INSERT INTO "main"."upload_document" ("task_id", "state") VALUES ('{}', '{}');""".format(
        task_id, "running"
    )
    sqlite_server.cursor.execute(insert_sql)
    sqlite_server.conn.commit()

    vn = MyVanna(
        db_type=db_type,
        db_name=db_name,
        create_vector=False,
    )
    success_doc_list = []
    error_doc_list = []

    for doc in document_list:
        try:
            id = vn.train(documentation=doc)
            if id:
                success_doc_list.append((task_id, "success", doc, "success", str(id)))
        except Exception as e:
            logger.error("【add_documentation】 train doc error:{},doc={}".format(e, doc))
            error_doc_list.append((task_id, "fail", doc, "fail", str(e)))

    batch_insert_sql = """INSERT INTO "main"."upload_document" ("task_id","state","doc","doc_state","error_message") VALUES (?,?,?,?,?);"""
    sqlite_server.cursor.executemany(batch_insert_sql, success_doc_list + error_doc_list)
    sqlite_server.conn.commit()

    if not success_doc_list:
        state = "fail"
    else:
        state = "success"

    update_sql = """UPDATE "main"."upload_document" SET "state" = "{}" WHERE "task_id" = {}""".format(state, task_id)
    sqlite_server.cursor.execute(update_sql)

    sqlite_server.conn.commit()
    sqlite_server.close()


def get_upload_task_state(task_id):
    fail_data = []
    state = "running"
    sqlite_server = SqliteService()
    sql = """SELECT "state" FROM "main"."upload_document" WHERE "task_id" = '{}';""".format(task_id)
    sqlite_data = sqlite_server.cursor.execute(sql).fetchall()

    if not sqlite_data:
        state = "fail"
        fail_data = []
    if sqlite_data[0][0] == "fail":
        fail_sql = """SELECT "doc","error_message" FROM "main"."upload_document" WHERE "task_id" = '{}' AND "doc_state"="fail";""".format(
            task_id)
        sql_data = sqlite_server.cursor.execute(fail_sql).fetchall()
        fail_data = [{"doc": _da[0], "error_message": _da[1]} for _da in sql_data]
        state = "fail"
    elif sqlite_data[0][0] == "success":
        state = "success"
        fail_data = []
    sqlite_server.close()
    return state, fail_data

# -----------------------------------引入徐宾修改的方法-----------------------------------
