import json
# pip install pymssql

from flask import Flask, jsonify, Response, request, redirect, url_for
import flask
from vanna_model.vanna_chromadb_openai import VannaChromaDBOpenai
from sqlalchemy import create_engine
from common.common_result import ApiResponse
import datetime
from urllib.parse import quote_plus as urlquote

from vanna_entity.MyVanna import MyVanna
import yaml
from vanna_entity.MyVanna_Zhipu import MyVanna_ZhipuAI

from constant.sql_constant import DEFAULT_DB_TYPE, DB_TYPE, DB_STR, DB_DOCUMENTATION, DB_DIALECT

from entity.logging import logger


# class GeneratePlotlyHTML:
#     def __init__(self):
#         pass

# 自然语言查询SQL 生成图表HTML
def query_for_chart_html() -> jsonify:
    """
    自然语言查询SQL 生成图表HTML
    从Flask的请求中获取问题参数，并返回一个包含问题和HTML内容的JSON响应。
    参数:
    question: 用户输入的问题
    返回值:
    jsonify: 返回一个JSON响应对象，包含问题（question）和HTML内容（html）。
    """

    api_response = ApiResponse(500, "请求出错")

    # # dump = json.dumps(api_response)
    # # print(dump)
    # json = api_response.json()
    # print(json)
    # return api_response

    try:
        # question = flask.request.form.get('question')  # 从请求的表单数据中获取问题
        # # 数据库链接字符串 ex:'oracle://iqms:iqms@192.168.110.73:1521/IQORA'
        # db_url = flask.request.form.get('db_url')
        # # 数据库描述 ex:"This is a Oracle database"
        # db_desc = flask.request.form.get('db_desc')

        input_json = flask.request.get_json()

        print(f'{datetime.datetime.now()}:{input_json}')

        if input_json is None or len(input_json) <= 0:
            api_response.set_error("请输入参数")
            return jsonify(api_response.__dict__)

        question = input_json['question'] if 'question' in input_json else None
        # ex:{"type":0,"uid":"IQMS","pwd":"iqms","server":"192.168.110.74","port":"1521","database":"IQORA"}
        db_url = input_json['db_url'] if "db_url" in input_json else None
        # db_desc = input_json['db_desc'] if "db_desc" in input_json else None
        if question is None or len(question) <= 0:
            api_response.set_error("请输入要查询的问题")
            return jsonify(api_response.__dict__)
        if db_url is None or len(db_url) <= 0:
            api_response.set_error("请输入要链接的数据库链接字符串")
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
        db_type = db_url['type']
        server = db_url['server']
        port = db_url['port']
        database = db_url['database']
        uid = db_url['uid']
        pwd = db_url['pwd']

        if db_type is None:
            api_response.set_error("请输入数据库类型")
            return jsonify(api_response.__dict__)
        if server is None or len(server) <= 0:
            api_response.set_error("请输入数据库地址")
            return jsonify(api_response.__dict__)
        if port is None or len(port) <= 0:
            api_response.set_error("请输入数据库端口号")
            return jsonify(api_response.__dict__)
        if database is None or len(database) <= 0:
            api_response.set_error("请输入数据库名称")
            return jsonify(api_response.__dict__)
        if uid is None or len(uid) <= 0:
            api_response.set_error("请输入数据库登录名")
            return jsonify(api_response.__dict__)
        if pwd is None or len(pwd) <= 0:
            api_response.set_error("请输入数据库密码")
            return jsonify(api_response.__dict__)

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

        # return jsonify({"code": "test"})

        # vn = VannaChromaDBOpenai(config={'api_key': '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', 'model': 'gpt-3.5-turbo'
        #                                  # , 'path': 'E:\\work-space\\demo-workspace\\github\\fork\\vanna_entity\\chroma.sqlite3'
        #                                  })
        # #使用DeepSeek官网
        # vn = MyVanna(config={'api_key': 'sk-ee3afad6ea0a42c29d55bffe613394df', 'model': 'deepseek-chat', 'base_url': config_global['ai']['ollama']['base-url']})

        # 使用ChatGLM官网
        # vn = MyVanna_ZhipuAI(config={'api_key': '6f0d34f959d88e4cd620b29bba666bd6.GW6udYqR8faOSIaT', 'model': 'glm-4', 'base_url': config_global['ai']['ollama']['base-url']})
        vn = MyVanna_ZhipuAI(config={'api_key': '6f0d34f959d88e4cd620b29bba666bd6.GW6udYqR8faOSIaT', 'dialect': DB_DIALECT[db_type],
                                     'model': config_global['ai']['ollama']['chat']['model'], 'base_url': config_global['ai']['ollama']['base-url']})

        # vn = VannaChromaDBOpenai(config={'api_key': 'sk-ee3afad6ea0a42c29d55bffe613394df', 'model': 'gpt-3.5-turbo'
        #                                  # , 'path': 'E:\\work-space\\demo-workspace\\github\\fork\\vanna_entity\\chroma.sqlite3'
        #                                  })

        # vn.test_ref()

        # This gives the package a function that it can use to run the SQL
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

        # engine = None
        # if db_url is not None:
        #     engine = create_engine(db_url)
        # else:
        #     engine = create_engine('oracle://iqms:iqms@192.168.110.74:1521/IQORA')

        # engine = create_engine('oracle://iqms:iqms@192.168.110.73:1521/IQORA')

        # 生成sql
        sql = vn.generate_sql(question=question)
        # 执行sql取数据
        df = vn.run_sql(sql=sql, db=engine)
        code = vn.generate_plotly_code(question=question, sql=sql, df_metadata=f"Running df.dtypes gives:\n {df.dtypes}")
        fig = vn.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
        fig_html = fig.to_html()

        data = {
            "question": question,
            "html": fig_html
        }
        api_response.set_success("请求成功", data)

    except Exception as e:
        print(e.__str__())
        logger.error(e)
        return e.__str__(), 500, {'Content-Type': 'text/plain'}
        api_response.set_error(e.__str__())

    return fig_html, 200, {'Content-Type': 'text/plain'}

    # to_dict = api_response.__dict__
    #
    # return jsonify(
    #     to_dict
    # )
