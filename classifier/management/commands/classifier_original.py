from django.core.management.base import BaseCommand
import sys
import math
import sqlite3
import MeCab
import numpy as np
import pandas as pd
import re

# DBファイル準備
db_name = 'db.sqlite3'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

df1 = pd.read_sql('select text,category from classifier_article_data limit 160', conn)
df2 = pd.read_sql('select text,category from classifier_article_data limit 159,160', conn)
df1_array = np.array(df1)
df2_array = np.array(df2)


# ナイーブベイズ実装
class NaiveBayes:
    # コンストラクタ
    def __init__(self):
        # 学習データの全単語の集合
        self.vocabularies = set()
        # 学習データのカテゴリーごとの単語セット用
        self.word_count = {}
        # 学習データのカテゴリーごとの記事数セット
        self.category_count = {}

    # 学習
    def train(self, document, category):
        # 学習文書を形態素解析
        word_list = ""
        m = MeCab.Tagger()
        # 正規表現により文章中の記号・数字を削除
        fix = re.sub(re.compile("[!-/:-@[-`{-~]"), '', document)
        m_article = m.parse(fix)
        for row in m_article.split("\n"):
            word = row.split("\t")[0]  # タブ区切りになっている１つ目を取り出す。ここには形態素が格納されている
            if word == "EOS":
                break
            else:
                pos = row.split("\t")[1]  # タブ区切りになっている2つ目を取り出す。ここには品詞が格納されている
                slice = pos[:2]
                if slice == "名詞":
                    word_list = word_list + " " + word

        for word in word_list:
            # カテゴリー内の単語出現回数をUP
            self.__word_count_up(word, category)
        # カテゴリーの文書数をUP
        self.__category_count_up(category)

    # 学習データのカテゴリー内の単語出現回数をUP
    def __word_count_up(self, word, category):
        # 新カテゴリーなら追加
        self.word_count.setdefault(category, {})
        # カテゴリー内で新単語なら追加
        self.word_count[category].setdefault(word, 0)
        # カテゴリー内の単語出現回数をUP
        self.word_count[category][word] += 1
        # 学習データの全単語集合に加える(重複排除)
        self.vocabularies.add(word)

    # 学習データのカテゴリーの文書数をUP
    def __category_count_up(self, category):
        # 新カテゴリーなら追加
        self.category_count.setdefault(category, 0)
        # カテゴリーの文書数をUP
        self.category_count[category] += 1

    # 分類
    def classifier(self, document):
        # もっとも近いカテゴリ
        best_category = None
        # 最小整数値を設定
        max_prob = -sys.maxsize
        # 学習文書を形態素解析
        word_list = ""
        m = MeCab.Tagger()
        # 正規表現により文章中の記号・数字を削除
        fix = re.sub(re.compile("[!-/:-@[-`{-~]"), '', document)
        m_article = m.parse(fix)
        for row in m_article.split("\n"):
            word = row.split("\t")[0]  # タブ区切りになっている１つ目を取り出す。ここには形態素が格納されている
            if word == "EOS":
                break
            else:
                pos = row.split("\t")[1]  # タブ区切りになっている2つ目を取り出す。ここには品詞が格納されている
                slice = pos[:2]
                if slice == "名詞":
                    word_list = word_list + " " + word
        # カテゴリ毎に文書内のカテゴリー出現率P(C|D)を求める
        for category in self.category_count.keys():
            # 文書内のカテゴリー出現率P(C|D)を求める
            prob = self.__score(word_list, category)
            if prob > max_prob:
                max_prob = prob
                best_category = category

        return best_category

    # 文書内のカテゴリー出現率P(C|D)を計算
    def __score(self, word_list, category):
        # カテゴリー出現率P(C)を取得 (アンダーフロー対策で対数をとり、加算)
        score = math.log(self.__prior_prob(category))
        # カテゴリー内の単語出現率を文書内のすべての単語で求める
        for word in word_list:
            # カテゴリー内の単語出現率P(Wn|C)を計算 (アンダーフロー対策で対数をとり、加算)
            score += math.log(self.__word_prob(word, category))

        return score

    # カテゴリー出現率P(C)を計算　
    def __prior_prob(self, category):
        # 学習データの対象カテゴリーの文書数　/ 学習データの文書数合計
        return float(self.category_count[category] / sum(self.category_count.values()))

    # カテゴリー内の単語出現率P(Wn|C)を計算
    def __word_prob(self, word, category):
        # 単語のカテゴリー内出現回数 + 1 / カテゴリー内単語数 + 学習データの全単語数 (加算スムージング)
        prob = (self.__in_category(word, category) + 1.0) / (sum(self.word_count[category].values()) + len(self.vocabularies) * 1.0)
        return prob

    # 単語のカテゴリー内出現回数を返す
    def __in_category(self, word, category):
        if word in self.word_count[category]:
            # 単語のカテゴリー内出現回数
            return float(self.word_count[category][word])
        return 0.0


class Command(BaseCommand):

    def handle(self, *args, **options):
        nb = NaiveBayes()
        i = 0
        # 訓練
        for i in range(160):
            nb.train(df1_array[i][0], df1_array[i][1])
            i += 1

        j = 0
        # カテゴリの分類が成功した数をカウントするための値
        correct = 0
        # 分類機の性能評価
        for j in range(160):
            nb.classifier(df2_array[j][0])
            if nb.classifier(df2_array[j][0]) == df2_array[j][1]:
                correct += 1
            else:
                pass
        print(correct / 160)
