import jieba.posseg as pseg

"""
切名词-xb_yuq注释
"""


def cut_sentence(sentence: str) -> list:
    """
    分句
    """
    return_list = []
    sentence_find = None
    if "表" in sentence:
        sentence = sentence.split("表")
        return_list.append(sentence[0])
        sentence_find = sentence[0]
    else:
        return_list.append(sentence)
        sentence_find = sentence
    return_list += [i for i in sentence_find]
    # words = pseg.cut(sentence[0])
    # for word, flag in words:
    #     # if flag in ['n', 'nr', 'ns', 'nt', 'nz', 'vn']:
    #     if flag in ['n', 'eng'] and len(word) > 1:
    #         return_list.append(word)

    for sent in sentence:
        for word, flag in pseg.cut(sent):
            # if flag in ['n', 'nr', 'ns', 'nt', 'nz', 'vn']:
            if flag in ['n', 'eng'] and len(word) > 1:
                return_list.append(word)
    return list(set(return_list))


def split_sentence(sentences: list, documentation_type: str = "table", database_type: str = "0") -> list:
    """
    拆分句子，区分表信息和字段信息
    """
    sentences_list = []
    if documentation_type == "table":
        for sentence in sentences:
            _key, _value = sentence.split("是")
            if _key == _value:
                continue
            sentences_list.append((database_type, _key, _value))
    elif documentation_type == "column":
        for sentence in sentences:
            _, column_value = sentence.split("的"), sentence.split("的")[-1]
            _key, _value = column_value.split("字段是")
            if _key == _value:
                continue
            sentences_list.append((database_type, _key, _value))
            print(_key, _value)
    return sentences_list


if __name__ == '__main__':
    # 示例用法
    # _sentence = "结合三季度的销售清单和现存物料，输出四季度的方案"
    # print--> ['三季度', '销售', '销售清单', '三季度销售清单物料', '四季度', '三季度销售清单物料四季度方案']
    # _sentence = '给我十条物料'
    # print--> ['物料']
    # keyword = extract_keywords(_sentence)
    # _sentence = "工程报价主表的报价日期-到期日期字段是DUE_DATE"
    _sentence = "物料库存组表的前十条的物料id"
    keyword = cut_sentence(_sentence)
    print(keyword)
