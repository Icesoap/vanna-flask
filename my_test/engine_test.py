from sqlalchemy import create_engine

import pandas as pd

import pymssql
import os

os.environ['TDSDUMP'] = 'stdout'  # 用于打印连接详细过程







def pymssql_test():

    try:

        # import _mssql

        conn = pymssql.connect(server='117.78.49.23', port='1604', user='sa',
                               password='2660000532-83096695%21%40%23%24%25', database='SRC', charset='GBK')
        # conn = pymssql.connect(server='117.78.49.23', port='1604', user='sa', password='2660000532-83096695!@#$%', database='SRC', charset='GBK')
        # conn = pymssql.connect(server='PC-202205240905', port='1433', user='sa', password='123456', database='master', charset='CP936')
        # conn = pymssql.connect(server='PC-202205240905', port='1433', user='sa', password='123456', database='pdm-test2')
        # # conn = _mssql.connect(server='.', user='sa', password='123', database='test')
        #
        cur = conn.cursor()

        # cur.execute('select top 10 * from "Sportsoul-PDM".dbo.FileExtension')
        cur.execute('select top 10 * from FileExtension')
        print(cur.fetchall())

        cur.close()

        conn.close()

    except Exception as e:
        print(e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def pandas_test():

    try:

        db_url_final = 'mssql+pymssql://sa:2660000532-83096695%21%40%23%24%25@117.78.49.23:1604/SRC'
        # db_url_final = 'mssql+pymssql://sa:2660000532-83096695%21%40%23%24%25@117.78.49.23:1604/master'
        # db_url_final = "mssql+pymssql://sa:123456@PC-202205240905:1433/pdm-test2"
        # # db_url_final = "mssql+pymssql://sa:123456@PC-202205240905:1433/master"
        engine = create_engine(db_url_final)
        sql = 'select top 10 * from FileExtension'
        df = pd.read_sql_query(sql, engine)
        print(df)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        pandas_test()
    except Exception as e:
        print(e)