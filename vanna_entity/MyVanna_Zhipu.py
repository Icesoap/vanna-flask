# from vanna.openai.openai_chat import OpenAI_Chat
from vanna_model.openai.openai_chat_override import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ZhipuAI import ZhipuAI_Chat
import pandas as pd
from sqlalchemy.engine.base import Engine

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
        #修改chromadb_vanna路径
        config['path'] = "./chromadb_vanna"
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
