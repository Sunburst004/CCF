import pandas as pd
import jieba.posseg as pseg
import jieba
import pkuseg
import re
import csv

jieba.load_userdict('./source/dictionary.txt')

seg = pkuseg.pkuseg(postag=True)


class Ccf:
    def __init__(self):
        self.stop_path = r'./source/stop_words.txt'
        self.stop_list = []

    @staticmethod
    def read_file():
        """
        read csv file
        :return:
        """
        with open(r'.\Train_Data.csv', encoding='utf-8-sig') as f:
            file_content = pd.read_csv(f)
        ids = file_content[:10]['id']
        text = file_content[:10]['text']
        title = file_content[:10]['title']
        unknown_entities = file_content[:10]['unknownEntities']

        content = []
        for i in range(len(ids)):
            # print(f'正在处理第{i}行：{ids[i]}---->{text[i]}')
            content.append([ids[i], title[i], text[i], unknown_entities[i]])
        return content

    def get_stop_word(self):
        with open(self.stop_path, 'r', encoding='utf-8') as f:
            self.stop_list = [line.strip('\n') for line in f.readlines()]

    def wash_data(self):
        """
        after wash data
        :return: content list
        """
        content = self.read_file()
        replace_character = ['?', '#', '【', '】', '&nbsp', '▽', '\u3000\u3000', '@']

        for i in content:
            for re_c in replace_character:
                i[2] = str(i[2]).replace(re_c, '')

            for x in range(20):
                i[2] = i[2].replace('{IMG:' + str(x) + '}', '')
        return content

    def extract_entity(self):
        """
        extract entity
        :return: id + entity
        """
        self.get_stop_word()
        content = self.wash_data()

        # 公司词
        company_flag = ['app', '公司', '有限公司', '集团', '中心', '之家', '新闻']

        # 最后所有的实体
        entity_list = []
        for i in content:
            parse_content = i[2]
            convert = [[word, flag] for word, flag in seg.cut(parse_content)]
            # 去除无用词
            result = []
            for word, flag in convert:
                if word not in self.stop_list:
                    result.append([word, flag])

            # print(result)
            company_result = []
            for one in range(len(result)):
                # print(result[one], end=' ')
                if result[one][0] in company_flag and one - 1 >= 0:  # 由于python语言的特性 0 - 1 = -1 而result[-1]早python中是可以的所以必须排除
                    combine = result[one - 1][0] + result[one][0]
                    company_result.append(combine)
            print(company_result)


if __name__ == '__main__':
    ccf = Ccf()
    ccf.extract_entity()