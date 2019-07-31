from django.shortcuts import render
from django.http.response import HttpResponse
import os
import requests
from bs4 import BeautifulSoup
import MeCab
from . import naive_bayes


# Create your views here.
def index(request):

    url = request.GET.get('url')

    if url is None:
        d = {
            'category': "urlを入力して下さい。"
        }
    elif url == '':
        d = {
            'category': "urlを入力して下さい。"
        }
    else:
        # 入力されたURLでの本文を取得する。
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        doc = soup.find_all('p')

        # 取得した本文を形態素解析し、名詞のみ抽出
        word_list = ''
        for text in doc:
            m = MeCab.Tagger()
            m_text = m.parse(text.text)
            for row in m_text.split("\n"):
                word = row.split("\t")[0]  # タブ区切りになっている１つ目を取り出す。ここには形態素が格納されている
                if word == "EOS":
                    break
                else:
                    pos = row.split("\t")[1]  # タブ区切りになっている2つ目を取り出す。ここには品詞が格納されている
                    slice = pos[:2]
                    if slice == "名詞":
                        word_list = word_list + " " + word

        # 分類機を用いてカテゴリを予測
        category_number = naive_bayes.predict_category(word_list)

        # カテゴリの番号を文字に変換
        if category_number == '1':
            answer = 'エンタメ'
        elif category_number == '2':
            answer = 'スポーツ'
        elif category_number == '3':
            answer = 'おもしろ'
        elif category_number == '4':
            answer = '国内'
        elif category_number == '5':
            answer = '海外'
        elif category_number == '6':
            answer = 'コラム'
        elif category_number == '7':
            answer = 'IT・科学'
        else:
            answer = 'グルメ'

        d = {
            'category': 'この記事のカテゴリは' + answer + 'です。'
        }

    return render(request, 'classifier/index.html', d)
