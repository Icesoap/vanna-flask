import  sqlite3


if __name__ == '__main__':
    sqlite3.connect('../db/vector_manage.sqlite3')
    print("Hello World!")