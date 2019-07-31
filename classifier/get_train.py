import time
import sqlite3
import requests
from bs4 import BeautifulSoup
import MeCab

# カテゴリー別のURL
main_url_list = [
    "https://gunosy.com/categories/1",  # エンタメ
    "https://gunosy.com/categories/2",  # スポーツ
    "https://gunosy.com/categories/3",  # おもしろ
    "https://gunosy.com/categories/4",  # 国内
    "https://gunosy.com/categories/5",  # 海外
    "https://gunosy.com/categories/6",  # コラム
    "https://gunosy.com/categories/7",  # IT・科学
    "https://gunosy.com/categories/8",  # グルメ
]

"""
カテゴリー別のURLにて記事のURLをスクレイピング
その後、各記事へアクセスし、タイトル・本文をスクレイピング
上記でスクレイピングしたデータはデータベースに保存される
"""

for url_number in range(1, 3):
    for main_url in main_url_list:
        # 全カテゴリーで最新100記事中の最新20記事URLをスクレイピング
        print(main_url + '?page=' + str(url_number) + 'からのスクレイピングを開始')
        r = requests.get(main_url + '?page=' + str(url_number))
        soup = BeautifulSoup(r.text, 'lxml')
        main = soup.find(class_='main')
        list_title = main.find_all(class_='list_title')

        # 取得したいデータのリストを作成
        url = []
        title = []
        text = []
        category = []

        for i in list_title:
            # 記事カテゴリの取得
            article_category = main_url[-1]
            category.append(article_category)
            # 記事URLの取得
            article_url = i.a.get('href')
            url.append(article_url)
            # 記事URLにアクセスし、スクレイピング
            r = requests.get(article_url)
            soup = BeautifulSoup(r.text, 'lxml')
            # 記事タイトルの取得
            article_title = soup.find('h1')
            title.append(article_title.text)
            # 記事本文の取得＆形態素解析
            article_text = soup.find(class_='article gtm-click')
            text.append(article_text.text)

        # データベースに接続
        con = sqlite3.connect('../db.sqlite3')
        cur = con.cursor()
        # SQLを実行
        for a, b, c, d in zip(url, title, text, category):
            cur.execute("INSERT INTO classifier_article_data(url, title, text, category) VALUES(?,?,?,?);", (a, b, c, d))
        # データベースへの変更を保存
        con.commit()

        # 1秒間処理を停止
        time.sleep(1)
