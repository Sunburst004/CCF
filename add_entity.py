import csv

import pandas as pd
import re


def read_file():
    stop = ['nan','钱包','策略']
    with open(r'.\Train_Data.csv', encoding='utf-8-sig') as f:
        file_content = pd.read_csv(f, error_bad_lines=False)

    unknown_entities = file_content[:5013]['unknownEntities']
    content = []

    for i in range(len(unknown_entities)):
        content.append(unknown_entities[i])

    # for i in content:
    #     print(i)
    entity = []
    for i in content:
        if ';' not in str(i) and i not in stop:
            a = str(i) + ' ' + 'entity'
            entity.append(a)
        else:
            i = re.split(r';', i)
            for j in range(len(i)) :
                if i[j] not in stop:
                    b = i[j] + ' ' + 'entity'
                    entity.append(b)

    return entity


def write_entity():
    new_text = read_file()

    try:
        with open(r"", 'w', encoding='utf-8-sig', ) as csv_file:
            for i in new_text:
                csv_file.write(i + '\n')
            # 先写入columns_name

    except IOError:
        print("Write wrong!")


write_entity()
