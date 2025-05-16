from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):


    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def get_single_training_data_custom(self, question: str | None, documentation: str | None, sql: str | None,
                                        ddl: str | None, **kwargs):
        if sql is not None:
            collection_get = self.sql_collection.get(where_document={"$contains": "select * from orders"})


        collection_get = self.sql_collection.get(where_document={"$contains": "select * from orders"})
        ids_ = collection_get["ids"]
        print(ids_)
        collection_get1 = self.sql_collection.get(where_document={"$contains": "rty"})
        ids1 = collection_get1["ids"]
        print(len(ids1))
        # collection_query = self.sql_collection.query(query_texts=["select * from orders"],where={"sql": "select * from orders"})
        sql_data = self.sql_collection.get()

        # df = pd.DataFrame()
        #
        # if sql_data is not None:
        #     # Extract the documents and ids
        #     documents = [json.loads(doc) for doc in sql_data["documents"]]
        #     ids = sql_data["ids"]
        #
        #     # Create a DataFrame
        #     df_sql = pd.DataFrame(
        #         {
        #             "id": ids,
        #             "question": [doc["question"] for doc in documents],
        #             "content": [doc["sql"] for doc in documents],
        #         }
        #     )
        #
        #     df_sql["training_data_type"] = "sql"
        #
        #     df = pd.concat([df, df_sql])
        #
        # ddl_data = self.ddl_collection.get()
        #
        # if ddl_data is not None:
        #     # Extract the documents and ids
        #     documents = [doc for doc in ddl_data["documents"]]
        #     ids = ddl_data["ids"]
        #
        #     # Create a DataFrame
        #     df_ddl = pd.DataFrame(
        #         {
        #             "id": ids,
        #             "question": [None for doc in documents],
        #             "content": [doc for doc in documents],
        #         }
        #     )
        #
        #     df_ddl["training_data_type"] = "ddl"
        #
        #     df = pd.concat([df, df_ddl])
        #
        # doc_data = self.documentation_collection.get()
        #
        # if doc_data is not None:
        #     # Extract the documents and ids
        #     documents = [doc for doc in doc_data["documents"]]
        #     ids = doc_data["ids"]
        #
        #     # Create a DataFrame
        #     df_doc = pd.DataFrame(
        #         {
        #             "id": ids,
        #             "question": [None for doc in documents],
        #             "content": [doc for doc in documents],
        #         }
        #     )
        #
        #     df_doc["training_data_type"] = "documentation"
        #
        #     df = pd.concat([df, df_doc])
        #
        # return df