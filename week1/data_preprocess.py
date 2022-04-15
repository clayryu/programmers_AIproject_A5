import numpy as np
import pandas as pd
import copy

class data_preprocess:
    '''
    data : 종목 별로 넣어주어야 합니다.
    전체 data를 불러와서 원하시는 종목코드로 한번 걸러준 data를 넣어주세요.
    data = pd.read_csv("data/kaggletype_nlp_stocknews_202101_202202.csv", encoding='utf-8-sig'
                    ,dtype={'base_time':np.str,
                            '단축코드':np.str,
                            '종목명':np.str,
                            '종가':np.str,
                            '시가':np.str,
                            '고가':np.str,
                            '저가':np.str,
                            '전일대비':np.str,
                            '등락율':np.str,
                            '매도체결수량':np.str,
                            '매수체결수량':np.str,
                            '순매수체결수량':np.str,
                            '매도체결건수':np.str,
                            '매수체결건수':np.str,
                            '순체결건수':np.str,
                            '거래량':np.str,
                           })
    '''
    def __init__(self, data):
        self.data = data

        # 데이터의 Nan을 채워주고 필요없는 column을 정리하기
        data = self.data.fillna(0)
        drop_list = ['source','title','종가','시가','고가','저가','전일대비','매도체결수량','매수체결수량','순매수체결량',
                    '매도체결건수','매수체결건수','순체결건수','거래량']
        data = data.drop(drop_list, axis = 1)

        # base_time을 str에서 datetime으로 바꿔줍니다.
        data['base_time'] = data['base_time'].apply(lambda x : str(x))
        data['base_time'] = data['base_time'].apply(lambda x : x[:4]+'-'+x[4:6]+'-'+x[6:8]+'-'+x[8:10]+'-'+x[10:])
        data['base_time'] = pd.to_datetime(data['base_time'], format="%Y-%m-%d-%H-%M")
        data = data.sort_values(by = 'base_time')

        #등락율도 float으로 바꿔줍니다.
        data['등락율'] = data['등락율'].astype(float)

        # index를 reset해줍니다.
        data = data.reset_index()
        data = data.drop(['index'], axis = 1)

        # 뉴스 내용에서 불필요한 내용들을 제거하기
        # .space로 마지막 문장을 제거하기
        data['content'] = data['content'].apply(lambda x : x.split(". ")[:-1] if x != 0 else x)
        data['content'] = data['content'].apply(lambda x : ". ".join(x) if x != 0 else x)

        self.data = data

    # 90분봉 차이나는 상황과의 등락율 차이를 label로 만들어 봅시다.
    def to_csv(self, name):
        data = self.data

        # 차이값을 계산해줍니다.
        data_label = copy.deepcopy(data)
        temp_list = data_label['등락율'].diff(periods = 90)
        temp_list = list(temp_list)
        no_nan = temp_list[90:] + temp_list[:90]
        data_label['label'] = no_nan

        # label을 0과 1의 값을 가지도록 바꿔줍니다.
        data_label['labels'] = data_label['label'].apply(lambda x : 1 if x>0 else 0)

        # 기사 content가 있는 데이터만 남겨둡니다.
        data_label = data_label[data_label['content']!=0]

        # csv파일로 만들어줍니다.
        data_label.to_csv(f"./{name}.csv", index=False)

