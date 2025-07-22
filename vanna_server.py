# -*- coding: utf-8 -*-
# pip install gunicorn
# pip install gevent

# from gevent import pywsgi

from urllib.parse import quote_plus as urlquote
import datetime
from common.common_result import ApiResponse
import sys
import yaml

from dao.training_record_dao import TrainingRecordDao
from entity.schema.vector_db_schema import VectorDBSchema

type = sys.getfilesystemencoding()
from dotenv import load_dotenv

load_dotenv()
import pandas as pd
from functools import wraps
from flask import Flask, jsonify, Response, request, redirect, url_for
import flask
import os
from cache import MemoryCache
from vanna_entity.MyVanna import MyVanna
from vanna_entity.MyVanna_Zhipu import MyVanna_ZhipuAI
from sqlalchemy import create_engine
from controller.generate_plotly_html import query_for_chart_html
import cx_Oracle
from constant.sql_constant import DB_DIALECT
from services.sqlite_service import SqliteService
from entity.logging import logger

from constant.sql_constant import DEFAULT_DB_TYPE, DB_TYPE, DB_STR, DB_DOCUMENTATION, DB_DIALECT

from dao.vector_db_dao import VectorDBDao
from entity.models import VectorDB, TrainingRecord

from services.chromadb.chromadb_service import ChromaDBService

from utils.sqlalchemy_utils import SqlalchemyUtils
import json

from dataclasses import asdict

# 获取yaml文件路径
yamlPath = 'config.yml'
config_global = None
cx_oracle_path = ""

try:
    with open(yamlPath, 'rb') as f:
        # yaml文件通过---分节，多个节组合成一个列表
        # data = yaml.safe_load_all(f)
        config_global = yaml.load(f.read(), Loader=yaml.FullLoader)
        # print(result, type(result))
        # print(result['path'], type(result['path']))

        cx_oracle_path = config_global['path']['cx_oracle']
except Exception as e:
    print('config.yml not found')
    print(e)

    # # salf_load_all方法得到的是一个迭代器，需要使用list()方法转换为列表
    # print(list(data))
    # print(data['path']['cx_oracle'])

# 解决问题(cx_Oracle.DatabaseError) DPI-1047: Cannot locate a 64-bit Oracle Client library:
# "E:\Development\oracle\product\11.2.0\client_1\bin\oci.dll is not the correct architecture"
cx_Oracle.init_oracle_client(lib_dir=cx_oracle_path)
# cx_Oracle.init_oracle_client(lib_dir=r"E:\Development\PremiumSoft\Navicat Premium 15\instantclient_11_2")

app = Flask(__name__, static_url_path='')

# 自 然语言查询SQL 生成图表HTML
app.add_url_rule("/api/query_for_chart_html", view_func=query_for_chart_html, methods=['POST'])

# # flask 传参方式
# # 1.'/test1/<question_url>' 加 def route_test(question_url: str):
# # 2. flask.request.args.get('question')
# # 3. flask.request.form.get('question')
# @app.route('/test1/<question_url>', methods=['GET', 'POST'])
# def route_test(question_url: str):
#     question = flask.request.args.get('question')
#     question = flask.request.form.get('question')
#     return f"test:{question},question_url:{question_url}"


# SETUP
cache = MemoryCache()

# from vanna_entity.local import LocalContext_OpenAI
# vn = LocalContext_OpenAI()

# from vanna_entity.remote import VannaDefault
# vn = VannaDefault(model=os.environ['VANNA_MODEL'], api_key=os.environ['VANNA_API_KEY'])


# vn = MyVanna(config={'api_key': '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', 'model': 'gpt-3.5-turbo'
# , 'path': 'E:\\work-space\\demo-workspace\\github\\fork\\vanna_entity\\chroma.sqlite3'
# })
# 连接ChatGLM3
# vn = MyVanna(config={'api_key': 'EMPTY', 'model': 'chatglm3-6b', 'base_url': 'http://127.0.0.1:8009/v1/'})
# 连接本地Ollama_Deepseek
# vn = MyVanna(config={'api_key': 'ollama', 'model': 'deepseek-r1:8b', 'base_url': config_global['ai']['ollama']['base-url']})

# #使用DeepSeek官网
# vn = MyVanna(config={'api_key': 'sk-ee3afad6ea0a42c29d55bffe613394df', 'model': 'deepseek-chat', 'base_url': config_global['ai']['ollama']['base-url']})
# vn = MyVanna(config={'api_key': 'sk-ee3afad6ea0a42c29d55bffe613394df', 'model': 'deepseek-reasoner', 'base_url': config_global['ai']['ollama']['base-url']})

# 使用ChatGLM官网
# vn = MyVanna_ZhipuAI(config={'api_key': '6f0d34f959d88e4cd620b29bba666bd6.GW6udYqR8faOSIaT', 'dialect': DB_DIALECT[1],
#                              'model': config_global['ai']['ollama']['chat']['model'], 'base_url': config_global['ai']['ollama']['base-url']})

# vn = MyVanna_ZhipuAI(api_key='ollama', base_url=config_global['ai']['ollama']['base-url']
#                      , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[2], create_vector=False
#                      , db_type=2, db_name='IQORA')

# vn = MyVanna_ZhipuAI(api_key='ollama', base_url=config_global['ai']['ollama']['base-url']
#                      , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[1], create_vector=True
#                      , db_type=1, db_name='SRC')

# 测试火山引擎 ds
# vn = MyVanna_ZhipuAI(api_key=config_global['ai']['models']['deepseek-v3-250324']['api_key'], base_url=config_global['ai']['ollama']['base-url']
#                      , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[1], create_vector=False
#                      , db_type=1, db_name='SRC')

# 测试qwen3
vn = MyVanna_ZhipuAI(api_key=config_global['ai']['models']['qwen3:14b']['api_key'], base_url=config_global['ai']['ollama']['base-url']
                     , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[1], create_vector=False
                     , db_type=1, db_title='SRC')

# vn = MyVanna(config={'api_key': 'ollama', 'model': 'deepseek-r1:8b', 'base_url': 'http://localhost:11434/v1/'})

argv = sys.argv
print(argv)

# db_str = 'oracle://iqms:iqms@192.168.110.74:1521/IQORA'
# if len(argv) > 1:
#     arg_key = argv[1]
#     if arg_key == '--dbstr':
#         db_str = argv[2]

db_str = config_global["db_str"]["local"]

# oracle
# engine = create_engine('oracle://iqms:iqms@192.168.110.254:1521/IQORA')
pwd = '2660000532-83096695!@#$%'
engine = create_engine(f'mssql+pymssql://sa:{urlquote(pwd)}@117.78.49.23:1604/SRC')
# db_url_final = f"{db_type_result}://{uid}:{urlquote(pwd)}@{server}:{port}/{database}"

# engine = create_engine(db_str)

userName = 'root'
password = 'a@12345'
dbHost = '127.0.0.1'
dbPort = 3306
dbName = 'robot'


# SQLServer
# engine = create_engine('mssql+pymssql://sa:a@12345@Test-Data:1433/SPLMBak', pwd=None)
# engine = create_engine(f'mssql+pymssql://sa:{urlquote(password)}@Test-Data:1433/SPLMBak')
# engine = create_engine(f'mssql+pymssql://sa:sensnow100%@192.168.110.74:1433/ScenePLM')


# engine = create_engine('mssql+pymssql://sa:server2008@sensnow-hfj:1433/SCENEPLM220615')


# You define a function that takes in a SQL query as a string and returns a pandas dataframe
def run_sql(sql: str) -> pd.DataFrame:
    if len(sql) > 0:
        sql = sql.replace(";", "")
    df = pd.read_sql_query(sql, engine)
    return df


# This gives the package a function that it can use to run the SQL
vn.run_sql = run_sql
vn.run_sql_is_set = True
vn.static_documentation = "This is a Oracle database"


# # -------------------------------核心库初始化训练-------------------------------
# # training
# # The information schema query may need some tweaking depending on your database. This is a good starting point.
# # vanna原生不支持oracle 这里改造代码 使oracle可以匹配 vanna_entity
# # 具体代码在E:\Development\conda_env\vanna_entity\Lib\site-packages\vanna_entity\base\base.py里
# # table_catalog对应mysql的def; table_schema对应mysql的库名
#
# # 初始化SQLServer语句
# # df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
# df_information_schema = vn.run_sql("SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'")
#
# # This will break up the information schema into bite-sized chunks that can be referenced by the LLM
# plan = vn.get_training_plan_generic(df_information_schema)
# print(plan)
#
# # If you like the plan, then uncomment this and run it to train
# vn.train(plan=plan)
#
#
# # -------------------------------核心库初始化训练-------------------------------

#
# # You can also add SQL queries to your training data. This is useful if you have some queries already laying around. You can just copy and paste those from your editor to begin generating new SQL.
# vn.train(sql="select * from person")

# vn.ask(question="查询人员信息")


# vn.connect_to_snowflake(
#     account=os.environ['SNOWFLAKE_ACCOUNT'],
#     username=os.environ['SNOWFLAKE_USERNAME'],
#     password=os.environ['SNOWFLAKE_PASSWORD'],
#     database=os.environ['SNOWFLAKE_DATABASE'],
#     warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
# )

# 自己添加的方法,初始化数据库训练
@app.route('/api/init_training_db', methods=['GET', 'POST'])
def init_training_db():
    # db_type 数据库类型,1:mssql,2:oracle,3:mssql
    db_type = flask.request.args.get('db_type')

    # -------------------------------核心库初始化训练-------------------------------
    # training
    # The information schema query may need some tweaking depending on your database. This is a good starting point.
    # vanna原生不支持oracle 这里改造代码 使oracle可以匹配 vanna_entity
    # 具体代码在E:\Development\conda_env\vanna_entity\Lib\site-packages\vanna_entity\base\base.py里
    # table_catalog对应mysql的def; table_schema对应mysql的库名
    df_information_schema = None
    if db_type == '2':
        df_information_schema = vn.run_sql("SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'")
        vn.static_documentation = "This is a Oracle database"
    elif db_type == '1' or db_type == '3':
        vn.static_documentation = "This is a MsSQL database"
        if db_type == '3':
            vn.static_documentation = "This is a MySQL database"
        df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

    # 初始化SQLServer语句
    # df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    # df_information_schema = vn.run_sql("SELECT main.OWNER as table_catalog,main.OWNER as table_schema,main.* FROM all_tab_cols main where main.OWNER='IQMS'")

    # This will break up the information schema into bite-sized chunks that can be referenced by the LLM
    plan = vn.get_training_plan_generic(df_information_schema)
    print(plan)

    # If you like the plan, then uncomment this and run it to train
    vn.train(plan=plan)

    # -------------------------------核心库初始化训练-------------------------------
    return jsonify({
        "code": 200,
        "msg": "初始化数据库训练成功"
    })


# NO NEED TO CHANGE ANYTHING BELOW THIS LINE
def requires_cache(fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            id = request.args.get('id')

            if id is None:
                return jsonify({"type": "error", "error": "No id provided"})

            for field in fields:
                if cache.get(id=id, field=field) is None:
                    return jsonify({"type": "error", "error": f"No {field} found"})

            field_values = {field: cache.get(id=id, field=field) for field in fields}

            # Add the id to the field_values
            field_values['id'] = id

            return f(*args, **field_values, **kwargs)

        return decorated

    return decorator


@app.route('/api/v0/generate_questions', methods=['GET'])
def generate_questions():
    return jsonify({
        "type": "question_list",
        "questions": vn.generate_questions(),
        "header": "Here are some questions you can ask:"
    })


@app.route('/api/v0/generate_sql', methods=['GET'])
def generate_sql():
    question = flask.request.args.get('question')

    if question is None:
        return jsonify({"type": "error", "error": "No question provided"})

    id = cache.generate_id(question=question)
    sql = vn.generate_sql(question=question)

    cache.set(id=id, field='question', value=question)
    cache.set(id=id, field='sql', value=sql)

    return jsonify(
        {
            "type": "sql",
            "id": id,
            "text": sql,
        })


@app.route('/api/generate_sql_custom', methods=['POST'])
def generate_sql_custom():
    api_response = ApiResponse(500, "请求出错")
    try:

        input_json = flask.request.get_json()

        print(f'{datetime.datetime.now()}:{input_json}')

        if input_json is None or len(input_json) <= 0:
            api_response.set_error("请输入参数")
            return jsonify(api_response.__dict__)

        question = input_json['question'] if 'question' in input_json else None
        # ex:{"type":0,"uid":"IQMS","pwd":"iqms","server":"192.168.110.74","port":"1521","database":"IQORA"}
        # db_url = input_json['db_url'] if "db_url" in input_json else None
        db_id = input_json['db_id'] if "db_id" in input_json else None
        model_name = input_json['model_name'] if "model_name" in input_json else None
        # db_desc = input_json['db_desc'] if "db_desc" in input_json else None
        if question is None or len(question) <= 0:
            api_response.set_error("请输入要查询的问题")
            return jsonify(api_response.__dict__)
        if db_id is None or len(db_id) <= 0:
            api_response.set_error("请输入db_id")
            return jsonify(api_response.__dict__)
        # if db_url is None or len(db_url) <= 0:
        #     api_response.set_error("请输入要链接的数据库链接字符串")
        #     return jsonify(api_response.__dict__)
        if model_name is None or len(model_name) <= 0:
            api_response.set_error("请输入大模型的名称")
            return jsonify(api_response.__dict__)
        # if db_desc is None or len(db_desc) <= 0:
        #     api_response.set_error("请输入数据库类型描述")
        #     return jsonify(api_response.__dict__)

        # db_url_json = json.loads(db_url)
        # db_type = db_url_json['type']
        # server = db_url_json['server']
        # port = db_url_json['port']
        # database = db_url_json['database']
        # uid = db_url_json['uid']
        # pwd = db_url_json['pwd']

        # db_url_json = json.loads(db_url)

        # db_type = db_url['type']
        # server = db_url['server']
        # port = db_url['port']
        # database = db_url['database']
        # uid = db_url['uid']
        # pwd = db_url['pwd']
        #
        # if db_type is None:
        #     api_response.set_error("请输入数据库类型")
        #     return jsonify(api_response.__dict__)
        # if server is None or len(server) <= 0:
        #     api_response.set_error("请输入数据库地址")
        #     return jsonify(api_response.__dict__)
        # if port is None or len(port) <= 0:
        #     api_response.set_error("请输入数据库端口号")
        #     return jsonify(api_response.__dict__)
        # if database is None or len(database) <= 0:
        #     api_response.set_error("请输入数据库名称")
        #     return jsonify(api_response.__dict__)
        # if uid is None or len(uid) <= 0:
        #     api_response.set_error("请输入数据库登录名")
        #     return jsonify(api_response.__dict__)
        # if pwd is None or len(pwd) <= 0:
        #     api_response.set_error("请输入数据库密码")
        #     return jsonify(api_response.__dict__)

        # 获取yaml文件路径
        yamlPath = 'config.yml'
        config_global = None
        cx_oracle_path = ""

        try:
            with open(yamlPath, 'rb') as f:
                # yaml文件通过---分节，多个节组合成一个列表
                # data = yaml.safe_load_all(f)
                config_global = yaml.load(f.read(), Loader=yaml.FullLoader)
                # print(result, type(result))
                # print(result['path'], type(result['path']))

                cx_oracle_path = config_global['path']['cx_oracle']
        except Exception as e:
            print('config.yml not found')
            print(e)

        vector_db_dao = VectorDBDao()
        vector_db_return = vector_db_dao.get_entity_by_id(db_id)
        if not vector_db_return:
            api_response.set_error(f"未找到ID为[{db_id}]的训练库")
            return api_response.__dict__

        db_type = vector_db_return.db_type
        db_title = vector_db_return.db_title
        uid = vector_db_return.uid
        pwd = vector_db_return.pwd
        server = vector_db_return.server
        port = vector_db_return.port
        database = vector_db_return.data_base

        vn = MyVanna_ZhipuAI(api_key=config_global['ai']['models'][model_name]['api_key']
                             , base_url=config_global['ai']['models'][model_name]['base-url']
                             , model=config_global['ai']['models'][model_name]['model'], dialect=DB_DIALECT[db_type]
                             , create_vector=False, db_type=db_type, db_title=db_title)

        vn.run_sql = vn.run_sql
        vn.run_sql_is_set = True

        vn.static_documentation = DB_DOCUMENTATION[db_type]

        # if db_desc is not None:
        #     vn.static_documentation = db_desc
        # else:
        #     vn.static_documentation = "This is a Oracle database"

        db_type_result = DB_TYPE[db_type]
        # db_url_final = f"{db_type_result}://{uid}:{pwd}@{server}:{port}/{database}"
        db_url_final = f"{db_type_result}://{uid}:{urlquote(pwd)}@{server}:{port}/{database}"
        engine = create_engine(db_url_final)

        # 生成sql
        sql = vn.generate_sql(question=question, db_type=db_type)

        api_response.set_success("请求成功", None, sql)

        # question = flask.request.args.get('question')
        #
        # if question is None:
        #     return jsonify({"type": "error", "error": "No question provided"})
        #
        # id = cache.generate_id(question=question)
        # sql = vn.generate_sql(question=question)
        #
        # cache.set(id=id, field='question', value=question)
        # cache.set(id=id, field='sql', value=sql)

    except Exception as e:
        print(e.__str__())
        logger.error(e)
        return e.__str__(), 500, {'Content-Type': 'text/plain'}
        api_response.set_error(e.__str__())

    return api_response.__dict__

    # return jsonify(
    #     {
    #         "type": "sql",
    #         "id": id,
    #         "text": sql,
    #     })


@app.route('/api/v0/run_sql', methods=['GET'])
@requires_cache(['sql'])
def run_sql(id: str, sql: str):
    try:
        df = vn.run_sql(sql=sql)

        cache.set(id=id, field='df', value=df)

        return jsonify(
            {
                "type": "df",
                "id": id,
                "df": df.head(10).to_json(orient='records'),
            })

    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/v0/download_csv', methods=['GET'])
@requires_cache(['df'])
def download_csv(id: str, df):
    csv = df.to_csv()

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                     f"attachment; filename={id}.csv"})


@app.route('/api/v0/generate_plotly_figure', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_plotly_figure(id: str, df, question, sql):
    try:

        code = vn.generate_plotly_code(question=question, sql=sql, df_metadata=f"Running df.dtypes gives:\n {df.dtypes}")
        fig = vn.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
        fig_json = fig.to_json()
        cache.set(id=id, field='fig_json', value=fig_json)

        return jsonify(
            {
                "type": "plotly_figure",
                "id": id,
                "fig": fig_json,
            })
    except Exception as e:
        # Print the stack trace
        import traceback
        traceback.print_exc()

        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/v0/generate_plotly_figure_to_html_custom', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_plotly_figure_to_html_custom(id: str, df, question, sql):
    try:
        code = vn.generate_plotly_code(question=question, sql=sql, df_metadata=f"Running df.dtypes gives:\n {df.dtypes}")
        fig = vn.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
        fig_json = fig.to_json()

        cache.set(id=id, field='fig_json', value=fig_json)

        fig_html = fig.to_html()

        return jsonify(
            {
                "type": "plotly_figure",
                "id": id,
                "fig": fig_json,
                "html": fig_html
            })
    except Exception as e:
        # Print the stack trace
        import traceback
        traceback.print_exc()

        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/v0/test', methods=['GET'])
def test():
    try:
        code = vn.generate_plotly_code(question="test", sql="sql_test", df_metadata=f"Running df.dtypes gives:\n ")

        return jsonify(
            {
                "type": "plotly_figure",
                "id": id,
                "fig": 1,
                "html": 1
            })
    except Exception as e:
        # Print the stack trace
        import traceback
        traceback.print_exc()

        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/v0/get_training_data', methods=['GET'])
def get_training_data():
    df = vn.get_training_data()

    return jsonify(
        {
            "type": "df",
            "id": "training_data",
            # "df": df.head(25).to_json(orient='records'),
            "df": df.to_json(orient='records'),
        })


@app.route('/api/v0/remove_training_data', methods=['POST'])
def remove_training_data():
    # Get id from the JSON body
    id = flask.request.json.get('id')

    if id is None:
        return jsonify({"type": "error", "error": "No id provided"})

    if vn.remove_training_data(id=id):
        return jsonify({"success": True})
    else:
        return jsonify({"type": "error", "error": "Couldn't remove training data"})


"""
原始训练方法
"""
# @app.route('/api/v0/train', methods=['POST'])
# def add_training_data():
#     question = flask.request.json.get('question')
#     sql = flask.request.json.get('sql')
#     ddl = flask.request.json.get('ddl')
#     documentation = flask.request.json.get('documentation')
#
#     try:
#         id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)
#
#         return jsonify({"id": id})
#     except Exception as e:
#         print("TRAINING ERROR", e)
#         return jsonify({"type": "error", "error": str(e)})


"""
训练方法-自定义
"""


@app.route('/api/v0/train', methods=['POST'])
def add_training_data():
    question = flask.request.json.get('question')
    sql = flask.request.json.get('sql')
    ddl = flask.request.json.get('ddl')
    documentation = flask.request.json.get('documentation')
    db_type = flask.request.json.get('db_type')
    db_name = flask.request.json.get('db_name')
    # if not db_name or not db_type:
    #     return jsonify({"type": "error", "error": "Place check the parameter interface"})
    # vn = MyVanna(db_type=db_type, create_vector=False, db_name=db_name)
    sqlite_server = None
    try:
        if documentation:
            sqlite_server = SqliteService()
            _key, _value = documentation.split("是")[0], documentation.split("是")[-1]
            sqlite_server.insert_or_update_data({"key": _key, "value": _value, "database_type": 2})
            sqlite_server.close()
    except Exception as e:
        logger.error(f"【add_training_data】 error: {e}")
    finally:
        if sqlite_server is not None:
            sqlite_server.close()

    try:
        id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)

        return jsonify({"id": id})
    except Exception as e:
        print("TRAINING ERROR", e)
        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/add_training', methods=['POST'])
def add_training_data_custom():
    """
    向系统添加自定义的训练数据。

    接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
    结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。

    参数:
    - question: 训练数据中的问题部分，字符串类型。
    - sql: 对应于问题的结构化查询语言，字符串类型。
    - ddl: 数据定义语言，用于定义数据结构，字符串类型。
    - documentation: 对训练数据的文档说明，字符串类型。

    返回值:
    - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
    - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
    """
    api_response = ApiResponse(500, "请求出错")

    input_json = flask.request.get_json()

    print(f'{datetime.datetime.now()}--add_training_data_input_json:{input_json}')
    logger.info(f'add_training_data_custom-input_json:{input_json}')
    if input_json is None or len(input_json) <= 0:
        api_response.set_error("请输入参数")
        return api_response.json()

    # 从请求体中获取训练数据的四个部分
    question = input_json['question'] if 'question' in input_json else None
    sql = input_json['sql'] if 'sql' in input_json else None
    ddl = input_json['ddl'] if 'ddl' in input_json else None
    documentation = input_json['documentation'] if 'documentation' in input_json else None
    db_type = input_json.get('db_type')
    db_name = input_json.get('db_name')
    # if not db_name or not db_type:
    #     return jsonify({"type": "error", "error": "Place check the parameter interface"})
    # vn = MyVanna(db_type=db_type, create_vector=False, db_name=db_name)
    vn = MyVanna_ZhipuAI(api_key='ollama', base_url=config_global['ai']['ollama']['base-url']
                         , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[1], create_vector=False
                         , db_type=1, db_title='SRC')
    # vn = MyVanna_ZhipuAI(api_key='6f0d34f959d88e4cd620b29bba666bd6.GW6udYqR8faOSIaT', base_url=config_global['ai']['ollama']['base-url']
    #                      , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[2], create_vector=True
    #                      , db_type=2, db_name='IQORA')

    if question and not sql:
        api_response.set_error("输入了question必须有对应的sql语句")
        return api_response.__dict__

    if documentation is None and sql is None and ddl is None:
        api_response.set_error("请至少输入要训练的sql或documentation或ddl中的一个")
        return api_response.__dict__

    # 从请求体中获取训练数据的四个部分
    # question = flask.request.json.get('question')
    # sql = flask.request.json.get('sql')
    # ddl = flask.request.json.get('ddl')
    # documentation = flask.request.json.get('documentation')

    try:

        # collection_query = vn.sql_collection.query(query_texts=[question], n_results=50)
        # print(collection_query)
        # return

        training_data_single = vn.get_single_training_data_custom(question=question, sql=sql, ddl=ddl,
                                                                  documentation=documentation)

        single_ids = training_data_single["ids"]
        if len(single_ids) > 0:
            api_response.set_error(f"已存在id为{single_ids}的训练数据")
            return api_response.__dict__

        sqlite_server = None
        try:
            sqlite_server = SqliteService()
            if documentation:
                _key, _value = documentation.split("是")[0], documentation.split("是")[-1]
                sqlite_server.insert_or_update_data({"key": _key, "value": _value, "database_type": db_type})
            if question and sql:
                sqlite_server.insert_or_update_data({"key": question, "value": sql, "database_type": db_type})
            sqlite_server.close()
        except Exception as e:
            logger.error(f"【add_training_data_custom】 error: {e}")
        finally:
            if sqlite_server is not None:
                sqlite_server.close()

        # 尝试使用提供的训练数据进行训练，并获取训练的唯一标识符
        id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)

        data = {"id": id}
        api_response.set_success("添加训练数据成功", data)
        # return api_response.json()
        # 返回训练的唯一标识符
        # return jsonify({"id": id})
    except Exception as e:
        # 如果训练过程中出现异常，打印错误信息，并返回错误信息
        print("TRAINING ERROR", e)
        api_response.set_error(f"添加训练数据失败,{e.__str__()}")
        # return jsonify({"type": "error", "error": str(e)})
    return api_response.__dict__


# @app.route('/api/add_training', methods=['POST'])
# def add_training_data_custom():
#     """
#     向系统添加自定义的训练数据。
#
#     接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
#     结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。
#
#     参数:
#     - question: 训练数据中的问题部分，字符串类型。
#     - sql: 对应于问题的结构化查询语言，字符串类型。
#     - ddl: 数据定义语言，用于定义数据结构，字符串类型。
#     - documentation: 对训练数据的文档说明，字符串类型。
#
#     返回值:
#     - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
#     - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
#     """
#
#     api_response = ApiResponse(500, "请求出错")
#
#     input_json = flask.request.get_json()
#     print(f'{datetime.datetime.now()}--add_training_data_input_json:{input_json}')
#     if input_json is None or len(input_json) <= 0:
#         api_response.set_error("请输入参数")
#         return api_response.json()
#
#     # 从请求体中获取训练数据的四个部分
#     question = input_json['question'] if 'question' in input_json else None
#     sql = input_json['sql'] if 'sql' in input_json else None
#     ddl = input_json['ddl'] if 'ddl' in input_json else None
#     documentation = input_json['documentation'] if 'documentation' in input_json else None
#
#     if question and not sql:
#         api_response.set_error("输入了question必须有对应的sql语句")
#         return api_response.json()
#
#     if documentation is None and sql is None and ddl is None:
#         api_response.set_error("请至少输入要训练的sql或documentation或ddl中的一个")
#         return api_response.json()
#
#     # 从请求体中获取训练数据的四个部分
#     # question = flask.request.json.get('question')
#     # sql = flask.request.json.get('sql')
#     # ddl = flask.request.json.get('ddl')
#     # documentation = flask.request.json.get('documentation')
#
#     try:
#
#         # collection_query = vn.sql_collection.query(query_texts=[question], n_results=50)
#         # print(collection_query)
#         # return
#
#         '''
#         测试用户
#         '''
#
#         training_data_single = vn.get_single_training_data_custom(question=question, sql=sql, ddl=ddl, documentation=documentation)
#
#         single_ids = training_data_single["ids"]
#         if len(single_ids) > 0:
#             api_response.set_success(f"已存在id为{single_ids}的训练数据")
#             return api_response.model_dump_json()
#
#         # 尝试使用提供的训练数据进行训练，并获取训练的唯一标识符
#         id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)
#
#         data = {"id": id}
#         api_response.set_success("添加训练数据成功", data)
#         # return api_response.json()
#         # 返回训练的唯一标识符
#         # return jsonify({"id": id})
#     except Exception as e:
#         # 如果训练过程中出现异常，打印错误信息，并返回错误信息
#         print("TRAINING ERROR", e)
#         api_response.set_error(f"添加训练数据失败,{e.__str__()}")
#         # return jsonify({"type": "error", "error": str(e)})
#     return api_response.json()


@app.route('/api/v0/generate_followup_questions', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_followup_questions(id: str, df, question, sql):
    followup_questions = vn.generate_followup_questions(question=question, sql=sql, df=df)

    cache.set(id=id, field='followup_questions', value=followup_questions)

    return jsonify(
        {
            "type": "question_list",
            "id": id,
            "questions": followup_questions,
            "header": "Here are some followup questions you can ask:"
        })


@app.route('/api/v0/load_question', methods=['GET'])
@requires_cache(['question', 'sql', 'df', 'fig_json', 'followup_questions'])
def load_question(id: str, question, sql, df, fig_json, followup_questions):
    try:
        return jsonify(
            {
                "type": "question_cache",
                "id": id,
                "question": question,
                "sql": sql,
                "df": df.head(10).to_json(orient='records'),
                "fig": fig_json,
                "followup_questions": followup_questions,
            })

    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})


@app.route('/api/v0/get_question_history', methods=['GET'])
def get_question_history():
    return jsonify({"type": "question_history", "questions": cache.get_all(field_list=['question'])})


# 新建向量库
@app.route('/api/db/create_knowledge_db', methods=['POST'])
def create_knowledge_db():
    """
    用来新建或更新vanna的知识库,
    这个知识库是vanna用来训练或连接使用


    接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
    结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。

    参数:
    - question: 训练数据中的问题部分，字符串类型。
    - sql: 对应于问题的结构化查询语言，字符串类型。
    - ddl: 数据定义语言，用于定义数据结构，字符串类型。
    - documentation: 对训练数据的文档说明，字符串类型。

    返回值:
    - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
    - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
    """
    title = "新建向量库"
    api_response = ApiResponse(500, "请求出错")

    input_json = flask.request.get_json()

    print(f'{datetime.datetime.now()}--create_knowledge_db_input_json:{input_json}')
    logger.info(f'create_knowledge_db-input_json:{input_json}')
    if input_json is None or len(input_json) <= 0:
        api_response.set_error("请输入参数")
        return api_response.__dict__

    # 从请求体中获取训练数据的四个部分
    db_title = input_json['db_title'] if 'db_title' in input_json else None
    # ex:{"type":0,"uid":"IQMS","pwd":"iqms","server":"192.168.110.74","port":"1521","database":"IQORA"}
    db_type = input_json['db_type'] if "db_type" in input_json else None
    uid = input_json['uid'] if "uid" in input_json else None
    pwd = input_json['pwd'] if "pwd" in input_json else None
    server = input_json['server'] if "server" in input_json else None
    port = input_json['port'] if "port" in input_json else None
    database = input_json['database'] if "database" in input_json else None
    # db_desc = input_json['db_desc'] if "db_desc" in input_json else None
    if db_title is None or len(db_title) <= 0:
        api_response.set_error("请输入要数据库唯一标识")
        return jsonify(api_response.__dict__)
    if db_type is None:
        api_response.set_error("请输入数据库类型")
        return jsonify(api_response.__dict__)
    if uid is None or len(uid) <= 0:
        api_response.set_error("请输入数据库登录用户名")
        return jsonify(api_response.__dict__)
    if pwd is None or len(pwd) <= 0:
        api_response.set_error("请输入数据库登录密码")
        return jsonify(api_response.__dict__)
    if server is None or len(server) <= 0:
        api_response.set_error("请输入数据库连接地址(IP)")
        return jsonify(api_response.__dict__)
    if port is None or len(port) <= 0:
        api_response.set_error("请输入数据库连接端口号")
        return jsonify(api_response.__dict__)
    if database is None or len(database) <= 0:
        api_response.set_error("请输入要连接的数据库名字")
        return jsonify(api_response.__dict__)

    try:

        # collection_query = vn.sql_collection.query(query_texts=[question], n_results=50)
        # print(collection_query)
        # return

        vector_db_dao = VectorDBDao()
        # 检查是否已存在
        vector_db_return = vector_db_dao.get_entity_by_db_title(db_title)
        if vector_db_return:
            api_response.set_error(f"已存在名称为{db_title}的向量库")
            return api_response.__dict__

        vector_db = VectorDB(
            db_title=db_title,
            db_type=db_type,
            uid=uid,
            pwd=pwd,
            server=server,
            port=port,
            data_base=database
        )
        create_entity = vector_db_dao.create_entity(vector_db)

        # api_response.set_success(f"添加向量库[{db_title}]成功", {"db_id": create_entity.id})

        vn_local = MyVanna_ZhipuAI(api_key=config_global['ai']['models']['qwen3:14b']['api_key'], base_url=config_global['ai']['ollama']['base-url']
                                   , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[db_type], create_vector=False
                                   , db_type=db_type, db_title=db_title)
        chroma_db_service = ChromaDBService()
        engeine = SqlalchemyUtils.generate_sqlalchemy_engeine(db_type, server, port, uid, pwd, database)
        # chroma_db_service.init_training_db(db_type, vn_local, engeine)

        entity_return = vector_db_dao.update_entity(create_entity.id, {"status": 1})

        if entity_return:
            api_response.set_success(f"添加向量库[{db_title}]成功", {"db_id": create_entity.id})




    except Exception as e:
        # 如果训练过程中出现异常，打印错误信息，并返回错误信息
        print(f"{title}错误:", e)
        api_response.set_error(f"添加向量库失败,{e.__str__()}")
        # return jsonify({"type": "error", "error": str(e)})
    return api_response.__dict__


# 更新向量库
@app.route('/api/db/update_knowledge_db', methods=['POST'])
def update_knowledge_db():
    """
    用来新建或更新vanna的知识库,
    这个知识库是vanna用来训练或连接使用


    接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
    结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。

    参数:
    - question: 训练数据中的问题部分，字符串类型。
    - sql: 对应于问题的结构化查询语言，字符串类型。
    - ddl: 数据定义语言，用于定义数据结构，字符串类型。
    - documentation: 对训练数据的文档说明，字符串类型。

    返回值:
    - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
    - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
    """
    title = "更新向量库"
    api_response = ApiResponse(500, "请求出错")

    input_json = flask.request.get_json()

    print(f'{datetime.datetime.now()}--create_knowledge_db_input_json:{input_json}')
    logger.info(f'create_knowledge_db-input_json:{input_json}')
    if input_json is None or len(input_json) <= 0:
        api_response.set_error("请输入参数")
        return api_response.__dict__

    # 从请求体中获取训练数据的四个部分
    db_id = input_json['db_id'] if 'db_id' in input_json else None
    # ex:{"type":0,"uid":"IQMS","pwd":"iqms","server":"192.168.110.74","port":"1521","database":"IQORA"}
    uid = input_json['uid'] if "uid" in input_json else None
    pwd = input_json['pwd'] if "pwd" in input_json else None
    server = input_json['server'] if "server" in input_json else None
    port = input_json['port'] if "port" in input_json else None
    database = input_json['database'] if "database" in input_json else None
    # db_desc = input_json['db_desc'] if "db_desc" in input_json else None
    if db_id is None:
        api_response.set_error("请输入db_id")
        return jsonify(api_response.__dict__)
    if uid is None or len(uid) <= 0:
        api_response.set_error("请输入数据库登录用户名")
        return jsonify(api_response.__dict__)
    if pwd is None or len(pwd) <= 0:
        api_response.set_error("请输入数据库登录密码")
        return jsonify(api_response.__dict__)
    if server is None or len(server) <= 0:
        api_response.set_error("请输入数据库连接地址(IP)")
        return jsonify(api_response.__dict__)
    if port is None or len(port) <= 0:
        api_response.set_error("请输入数据库连接端口号")
        return jsonify(api_response.__dict__)
    if database is None or len(database) <= 0:
        api_response.set_error("请输入要连接的数据库名字")
        return jsonify(api_response.__dict__)

    try:

        # collection_query = vn.sql_collection.query(query_texts=[question], n_results=50)
        # print(collection_query)
        # return

        vector_db_dao = VectorDBDao()
        # 检查是否已存在
        vector_db_return = vector_db_dao.get_entity_by_id(db_id)
        if not vector_db_return:
            api_response.set_error(f"未发现要更新的ID为[{db_id}]的向量库")
            return api_response.__dict__

        vector_db_return.uid = uid
        vector_db_return.pwd = pwd
        vector_db_return.server = server
        vector_db_return.port = port
        vector_db_return.data_base = database
        vector_db_return.update_date = datetime.datetime.now()

        # vector_db_return._sa_instance_state = None
        # 去掉额外的属性
        if hasattr(vector_db_return, '_sa_instance_state'):
            del vector_db_return._sa_instance_state
        print(vector_db_return.__dict__)

        entity_return = vector_db_dao.update_entity(db_id, vector_db_return.__dict__)

        if entity_return:
            api_response.set_success(f"{title}[{db_id}]成功")
        # return api_response.json()
        # 返回训练的唯一标识符
        # return jsonify({"id": id})
    except Exception as e:
        # 如果训练过程中出现异常，打印错误信息，并返回错误信息
        print(title, e)
        api_response.set_error(f"{title}失败,{e.__str__()}")
        # return jsonify({"type": "error", "error": str(e)})
    return api_response.__dict__


# 更新向量库
@app.route('/api/db/get_knowledge_db_list', methods=['POST'])
def get_knowledge_db_list():
    """
    用来新建或更新vanna的知识库,
    这个知识库是vanna用来训练或连接使用


    接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
    结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。

    参数:
    - question: 训练数据中的问题部分，字符串类型。
    - sql: 对应于问题的结构化查询语言，字符串类型。
    - ddl: 数据定义语言，用于定义数据结构，字符串类型。
    - documentation: 对训练数据的文档说明，字符串类型。

    返回值:
    - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
    - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
    """
    title = "获取训练库列表"
    api_response = ApiResponse(500, "请求出错")

    input_json = flask.request.get_json()

    print(f'{datetime.datetime.now()}--create_knowledge_db_input_json:{input_json}')
    logger.info(f'create_knowledge_db-input_json:{input_json}')
    db_title = None
    if input_json:
        # 从请求体中获取训练数据的四个部分
        db_title = input_json['db_title'] if 'db_title' in input_json else None

    try:

        # collection_query = vn.sql_collection.query(query_texts=[question], n_results=50)
        # print(collection_query)
        # return

        vector_db_dao = VectorDBDao()
        # 检查是否已存在
        vector_db_return_list = vector_db_dao.query_entities(db_title)

        if not db_title:
            db_title = "所有"

        result_list_str = []
        # for vector_db_loop in vector_db_return_list:
        #     # 去掉额外的属性
        #     if hasattr(vector_db_loop, '_sa_instance_state'):
        #         del vector_db_loop._sa_instance_state
        #     result_list.append(vector_db_loop.__dict__)

        # result_list.append(json.dumps(asdict(vector_db_loop)))

        if vector_db_return_list:
            vector_db_schema = VectorDBSchema()
            result_list = vector_db_schema.dumps(vector_db_return_list, many=True)
            result_list_str = json.loads(result_list)

        # result_list = [vector_db.__dict__ for vector_db in vector_db_return_list]
        # result_list = [dict(vector_db.__dict__) for vector_db in vector_db_return_list]
        # data_list = json.dumps(result_list, indent=2)
        # 这里根据情况 如果result_list_str有值就返回json字符串,如果没值就返回空[]
        api_response.set_success(f"{title}[{db_title}]成功", data=result_list_str)
        # return api_response.json()
        # 返回训练的唯一标识符
        # return jsonify({"id": id})
    except Exception as e:
        # 如果训练过程中出现异常，打印错误信息，并返回错误信息
        print(title, e)
        api_response.set_error(f"{title}失败,{e.__str__()}")
        # return jsonify({"type": "error", "error": str(e)})
    return api_response.__dict__


@app.route('/api/db/add_training', methods=['POST'])
def add_training_single():
    """
    向系统添加自定义的训练数据。

    接收POST请求，请求体中包含训练数据的四个关键部分：问题（question）、
    结构化查询语言（SQL）、数据定义语言（DDL）和文档说明（documentation）。

    参数:
    - question: 训练数据中的问题部分，字符串类型。
    - sql: 对应于问题的结构化查询语言，字符串类型。
    - ddl: 数据定义语言，用于定义数据结构，字符串类型。
    - documentation: 对训练数据的文档说明，字符串类型。

    返回值:
    - 如果训练数据添加成功，返回一个包含训练数据唯一标识符（id）的JSON对象。
    - 如果添加过程中出现错误，返回一个包含错误信息的JSON对象。
    """
    title = "训练单条数据"
    api_response = ApiResponse(500, "请求出错")

    input_json = flask.request.get_json()

    print(f'{datetime.datetime.now()}--add_training_data_input_json:{input_json}')
    logger.info(f'add_training_data_custom-input_json:{input_json}')
    if input_json is None or len(input_json) <= 0:
        api_response.set_error("请输入参数")
        return api_response.__dict__

    # 从请求体中获取训练数据的四个部分
    db_id = input_json['db_id'] if 'db_id' in input_json else None
    question = input_json['question'] if 'question' in input_json else None
    sql = input_json['sql'] if 'sql' in input_json else None
    ddl = input_json['ddl'] if 'ddl' in input_json else None
    documentation = input_json['documentation'] if 'documentation' in input_json else None
    # db_type = input_json.get('db_type')
    # db_name = input_json.get('db_name')

    if db_id is None:
        api_response.set_error("请输入数据库ID")
        return api_response.__dict__
    if question and not sql:
        api_response.set_error("输入了question必须有对应的sql语句")
        return api_response.__dict__

    if documentation is None and sql is None and ddl is None:
        api_response.set_error("请至少输入要训练的sql或documentation或ddl中的一个")
        return api_response.__dict__

    # vn = MyVanna_ZhipuAI(api_key='6f0d34f959d88e4cd620b29bba666bd6.GW6udYqR8faOSIaT', base_url=config_global['ai']['ollama']['base-url']
    #                      , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[2], create_vector=True
    #                      , db_type=2, db_name='IQORA')

    # 从请求体中获取训练数据的四个部分
    # question = flask.request.json.get('question')
    # sql = flask.request.json.get('sql')
    # ddl = flask.request.json.get('ddl')
    # documentation = flask.request.json.get('documentation')

    try:

        vector_db_dao = VectorDBDao()
        vector_db_return = vector_db_dao.get_entity_by_id(db_id)
        if not vector_db_return:
            api_response.set_error(f"未找到ID为[{db_id}]的训练库")
            return api_response.__dict__

        db_type = vector_db_return.db_type
        db_title = vector_db_return.db_title

        vn = MyVanna_ZhipuAI(api_key='ollama', base_url=config_global['ai']['ollama']['base-url']
                             , model=config_global['ai']['ollama']['chat']['model'], dialect=DB_DIALECT[db_type], create_vector=False
                             , db_type=db_type, db_title=db_title)

        training_data_single = vn.get_single_training_data_custom(question=question, sql=sql, ddl=ddl,
                                                                  documentation=documentation)

        single_ids = training_data_single["ids"]
        if len(single_ids) > 0:
            api_response.set_error(f"已存在id为{single_ids}的训练数据")
            # return api_response.__dict__

        # 尝试使用提供的训练数据进行训练，并获取训练的唯一标识符
        id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)

        data = {"id": id}
        api_response.set_success("添加训练数据成功", data)

        # training_record_dao = None
        # 训练的时候记录 key 和 value
        try:

            update_data = dict
            if documentation:
                _key, _value = documentation.split("是")[0], documentation.split("是")[-1]
                update_data = {"key": _key, "value": _value}

            if question and sql:
                update_data = {"key": question, "value": sql}
            training_record_dao = TrainingRecordDao()
            training_record_dao.add_or_update_entity(db_id, update_data)

        except Exception as e1:
            logger.error(f"【add_training_single】 error: {e1}")

        # return api_response.json()
        # 返回训练的唯一标识符
        # return jsonify({"id": id})
    except Exception as e:
        # 如果训练过程中出现异常，打印错误信息，并返回错误信息
        print("TRAINING ERROR", e)
        api_response.set_error(f"添加训练数据失败,{e.__str__()}")
        # return jsonify({"type": "error", "error": str(e)})
    return api_response.__dict__


@app.route('/')
def root():
    """
    处理应用的根路由请求，返回静态文件index.html。

    参数:
    无

    返回值:
    返回服务器上的静态文件index.html。
    """
    return app.send_static_file('index.html')  # 发送静态文件作为响应


if __name__ == '__main__':
    # chroma_db_service = ChromaDBService()
    # chroma_db_service.init_chromadb_db('test库9')
    app.run(debug=False, host='0.0.0.0', port=5002)

# if __name__ == '__main__':
#     server = pywsgi.WSGIServer(('127.0.0.1', 5001), app)
#     server.serve_forever()
