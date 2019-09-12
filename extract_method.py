import pandas as pd
import jieba.posseg as pseg
import jieba
import re
import csv

jieba.load_userdict('./source/dictionary.txt')


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

        ids = file_content[:500]['id']
        text = file_content[:500]['text']
        title = file_content[:500]['title']
        unknown_entities = file_content[:500]['unknownEntities']
        content = []

        for i in range(len(ids)):
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

        new_text = []
        sum_n_entity = []
        entity_list = []
        flag = ['博览会','联盟','app', '公司', '有限公司', '集团', '中心', '之家','股权','理财','平台','场所','交易所','终端']
        nn = ['n', 'nr', 'ns', 'nt', 'nz']
        nn_entity = ['nr', 'nz', 'nt', 'ns', 'vn']

        content = self.wash_data()

        for i in content:
            before_num = []
            after_num = []
            middle = []
            middle0 = []
            chunk = pseg.cut(i[2])
            middle_entity = []
            n_entity = []


            # print(content.index(i))

            for j, k in chunk:
                middle.append([j, k])
                middle0.append([j, k])
            index = 0
            new_text.append(middle)
            for word in middle:
                if word[0] in self.stop_list:
                    del middle[middle.index(word)]


            for word in middle:
                if word[1] == 'n':
                    n_entity.append(word[0])

            n_entity = list(set(n_entity))
            sum_n_entity.append(n_entity)

            #-------------------------------合并 s + NN --------------------------------------------

            index_sNN = 0
            for a in range(len(middle)):
                if a > 0:
                    if middle[a][1] in nn_entity and middle[a - 1][1] == 's':
                        index_sNN += 1
            for j in range(index_sNN * 2):
                for a in range(len(middle)):
                    if a > 0:
                        if middle[a][1] in nn_entity and middle[a - 1][1] == 's':
                            middle[a - 1] = [middle[a - 1][0] + middle[a][0], middle[a][1]]
                            del middle[a]
                            break

            #-------------------------------合并 s + n ---------------------------------------------

            index_sn = 0
            for a in range(len(middle)):
                if a > 0:
                    if middle[a][1] == 'n' and middle[a - 1][1] == 's':
                        index_sn += 1
            for j in range(index_sn * 2):
                for a in range(len(middle)):
                    if a > 0:
                        if middle[a][1] == 'n' and middle[a - 1][1] == 's':
                            middle[a - 1] = [middle[a - 1][0] + middle[a][0], 'ns']
                            del middle[a]
                            break

            # ------------------------------添加词性为NN_entity的实体--------------------------------

            for word in middle:
                if word[1] in nn_entity and word[0]:
                    middle_entity.append(word[0])

            # --------------------------------------合并公司等实体----------------------------------------

            for a in range(len(middle)):
                if middle[a][0] in flag:
                    middle[a][1] = 'entity'
                    before_num.append(a)
                    for b in range(6):
                        if middle[a - b - 1][1] in nn and a >= 1 + b:
                            index = index + 1

            for a in range(index):
                for b in range(len(middle)):
                    if middle[b][1] == 'entity':
                        if middle[b - 1][1] in nn and b >= 1:
                            a = middle[b - 1][0] + middle[b][0]
                            middle[b - 1] = [a, 'entity']
                            del middle[b]
                            break

            # ----------------------------------------------将flag里未处理的词性还原------------------------

            for a in range(len(middle)):
                if middle[a][0] in flag:
                    middle[a][1] = 'entity'
                    after_num.append(a)

            lentha = len(after_num)
            for a in range(lentha):
                if middle0[before_num[a]][0] == middle[after_num[a]][0]:
                    middle[after_num[a]][1] = 'n'

            for word in middle:
                if word[0] in flag:
                    word[1] = 'n'
            # ------------------------------------合并一次名词---------------------------------------------

            index_n = 0
            for a in range(len(middle)):
                if a > 0:
                    if a < len(middle) - 1:
                        if middle[a][1] == 'n' and middle[a - 1][1] == 'n' and middle[a + 1][1] != 'n' :
                            index_n = index_n + 1
                            continue
                    elif middle[a][1] == 'n' and middle[a - 1][1] == 'n' and a == len(middle):
                        index_n = index_n + 1
                        continue

            for j in range(index_n):
                for d in range(len(middle)):
                    if d >= 1:
                        if middle[d][1] == 'n' and middle[d - 1][1] == 'n':
                            new_value = middle[d - 1][0] + middle[d][0]
                            middle[d - 1] = [new_value, 'entity']
                            del middle[d]
                            break

            # -------------------------------------识别网站------------------------------------------------

            tp_tr = re.compile(r'[http|https]+://\w+\.\w+\.\w+/[a-zA-Z0-9]+/[a-zA-Z0-9]+', re.S).findall(
                i[2])  # 两个点的两个反斜杆

            tp_or = []
            if not tp_tr:
                tp_or = re.compile(r'[http|https]+://\w+\.\w+\.\w+/[a-zA-Z0-9]+', re.S).findall(i[2])  # 两个点的一个反斜杆
            op_tr = re.compile(r'[http|https]+://\w+\.\w+/[a-zA-Z0-9]+/[a-zA-Z0-9]+', re.S).findall(i[2])  # 一个点的两个反斜杠

            op_or = []
            if not op_tr:
                op_or = re.compile(r'[http|https]+://\w+\.\w+/[a-zA-Z0-9]+', re.S).findall(i[2])  # 一个点的一个反斜杠
            book_name = list(set(re.compile(r'《\w+》', re.S).findall(i[2])))
            result_pre = re.compile(r"[\d|\d.\d]+\b%", re.S).findall(i[2])

            #--------------------------------------合并 m + m ---------------------------------------------

            index_mm = 0
            for a in range(len(middle)):
                if a > 0 :
                    if middle[a][1] == 'm' and middle[a - 1][1] == 'm':
                        index_mm += 1
            for j in range(index_mm*2):
                for a in range(len(middle)):
                    if a > 0:
                        if middle[a][1] == 'm' and middle[a-1][1] =='m':
                            middle[a-1] = [middle[a-1][0]+middle[a][0],'m']
                            del middle[a]
                            if a < len(middle):
                                if middle[a][1] != 'n':
                                    middle_entity.append(middle[a-1][1])
                            break

            #--------------------------------------合并 m + n ---------------------------------------------
            index_mn = 0
            for a in range(len(middle)):
                if a > 0 :
                    if middle[a][1] == 'n' and middle[a - 1][1] == 'm':
                        index_mn += 1
            for j in range(index_mn*2):
                for a in range(len(middle)):
                    if a > 0:
                        if middle[a][1] == 'n' and middle[a-1][1] =='m':
                            middle[a-1] = [middle[a-1][0]+middle[a][0],'entity']
                            del middle[a]
                            break

            #----------------------------------------- s + entity --------------------------------------

            index_sentity = 0
            for a in range(len(middle)):
                if a > 0:
                    if middle[a][1] == 'entity' and middle[a - 1][1] == 's':
                        index_sentity += 1

            for j in range(index_sentity * 2):
                for a in range(len(middle)):
                    if a > 0:
                        if middle[a][1] == 'entity' and middle[a - 1][1] == 's':
                            middle[a - 1] = [middle[a - 1][0] + middle[a][0], 'entity']
                            del middle[a]
                            break

            # -------------------------------------添加实体------------------------------------------------

            for word in middle:
                if word[1] == 'entity':
                    middle_entity.append(word[0])

            # ------------------------------------去重----------------------------------------------------

            middle_entity = list(set(middle_entity))

            total_entity = middle_entity + tp_tr + tp_or + op_tr + op_or + book_name + result_pre
            entity_list.append([i[0], ';'.join(total_entity)])

        for i in range(len(content)):
            print(new_text[i])
            print(entity_list[i])
            # print(content[i])

        return entity_list

    def store_csv(self):

        """
        convert structure and store csv
        :return:
        """

        new_text = self.extract_entity()

        try:
            with open("result_0.csv", "w", encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file)
                # 先写入columns_name
                writer.writerow(["id", "unknownEntities"])
                for i in new_text:
                    # print(f'正在写入第{new_text.index(i)+1}行：{i}')
                    # 写入多行用writerows
                    writer.writerow(i)

        except IOError:
            print("Write wrong!")


if __name__ == '__main__':
    ccf = Ccf()
    ccf.store_csv()
