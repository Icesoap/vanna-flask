# from vanna.openai.openai_chat import OpenAI_Chat
from vanna_model.openai.openai_chat_override import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ZhipuAI import ZhipuAI_Chat
import pandas as pd
from sqlalchemy.engine.base import Engine

from constant.sql_constant import DB_DIALECT

from chromadb.api.types import (
    URI,
    CollectionMetadata,
    DataLoader,
    Embedding,
    Embeddings,
    Embeddable,
    Include,
    Loadable,
    Metadata,
    Metadatas,
    Document,
    Documents,
    Image,
    Images,
    URIs,
    Where,
    IDs,
    EmbeddingFunction,
    GetResult,
    QueryResult,
    ID,
    OneOrMany,
    WhereDocument,
    # maybe_cast_one_to_many_ids,
    # maybe_cast_one_to_many_embedding,
    # maybe_cast_one_to_many_metadata,
    # maybe_cast_one_to_many_document,
    # maybe_cast_one_to_many_image,
    # maybe_cast_one_to_many_uri,
    validate_ids,
    validate_include,
    validate_metadata,
    validate_metadatas,
    validate_where,
    validate_where_document,
    validate_n_results,
    validate_embeddings,
    validate_embedding_function,
)


# import sys
# print("sys.path:---------------------------------------")
# print(sys.path)
# print("sys.path:---------------------------------------")


# class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
class MyVanna_ZhipuAI(ChromaDB_VectorStore, ZhipuAI_Chat):

    def __init__(self, config=None):
        # 修改chromadb_vanna路径
        config['path'] = "./chromadb_vanna"
        # config['dialect'] = DB_DIALECT
        ChromaDB_VectorStore.__init__(self, config=config)
        ZhipuAI_Chat.__init__(self, config=config)
        # OpenAI_Chat.__init__(self, config=config)

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

    def get_sql_prompt(
        self,
        initial_prompt : str,
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
            "Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "

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

