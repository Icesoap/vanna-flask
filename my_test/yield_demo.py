# encoding:UTF-8
def yield_test(n):
    print('first')
    for i in range(n):
        print(f'yield_test--before-yield')
        yield call(i)
        print("i=", i)
        # 做一些其它的事情
    print("do something.")
    print("end.")


def call(i):
    print(f'call--i:{i}')
    return i * 2

    # 使用for循环


def yield_test2():
    print('before')
    yield '123'
    print('after')


if __name__ == '__main__':
    test = yield_test2()


    print(test)
    # print(test.next())

    # for i in yield_test(5):
    #     print(i, ",")
