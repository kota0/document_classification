# Naive Bayes Classifier
ナイーブベイズを用いて記事のカテゴリを分類するアプリです。

## Build this app on docker
このアプリの実行方法に関して説明します。（Dockerがインストールされていることは前提）

1.ターミナルを開く

2.git cloneでローカル環境にリポジトリをクローン
```
git clone https://f386246be7e5233a024064bd11db59604fb52c20:x-oauth-basic@github.com/kota0/naive_bayes_classifier
```

3.Dockerfileからイメージをビルド
（カレントディレクトリが正しいことを確認した上で）
```
docker-compose up
```

4.ターミナルで新規画面を開き、3で作成したコンテナに入ってください。
```
docker exec -it <コンテナID> bash
```
その後マイグレーションを実行します。
```
python manage.py migrate
```

5.これでDocker環境でアプリが実行できるようになったはずなので、次はアプリの機能の利用方法を解説していきます。

## Function in this app
### 1.データ収集（スクレイピング）
こちらは、「gunosy.com」から記事をスクレイピングする機能です。
```「エンタメ」、「スポーツ」、「おもしろ」、「国内」、「海外」、「コラム」、「IT・科学」、「グルメ」```の8カテゴリから各40記事ずつ（合計320記事）「URL」、「記事タイトル」、「記事本文」をスクレイピングし、データベースに保存します。<br>
【実行方法】<br>
（コンテナに入っていることを確認後）<br>
1.データの収集を行っていきます。以下のコードを打ちこむとスクレイピングが始まります。
```
python manage.py scrape
```
2.スクレイピングが完了するまでお待ちください。

### 2.モデルのトレーニング（ナイーブベイズ分類機の活用）
こちらは先程スクレイピングしたデータを使ってナイーブベイズ分類機を作成する機能です。
```
1.スクレイピングしたデータを160記事データベースから取り出し、Mecabを使って形態素解析する。
2.形態素解析したものから名詞のみを取り出し、独自に実装したナイーブベイズ分類機に学習させる。
3.分類機の評価を行いたいので、別の160記事のデータでテストを行います。
4.私が利用したデータでは、カテゴリの分類の正答率は0.69375％となりました。
```

【実行方法】<br>
（コンテナに入っていることを確認後）<br>
1.以下のコードを打ちこむと学習を開始します。<br>
```
python manage.py classifier_original
```
2.ナイーブベイズ分類機の正答率が表示されます。

### 3.記事URLを入れると記事カテゴリを返す、ナイーブベイズを使った教師あり文書分類器Webアプリ
```
URLを入力すると、そのURLの記事が「エンタメ」、「スポーツ」、「おもしろ」、「国内」、「海外」、「コラム」、「IT・科学」、「グルメ」のどのカテゴリに近いのか判別し、結果を表示します。
```

【実行方法】<br>
（コンテナを起動させていること・スクレイピングを行ったこと。を確認後）<br>
```
1.0.0.0.0:8000にアクセスして下さい。
2.URLを入力するフォームがあるので、URLを入力してください。
3.分類ボタンをクリックすると、カテゴリの判別が始まります。
4.カテゴリが表示されます。
```

なお、機能1,2に関しては上記で説明した通り、Djangoのカスタムコマンドとして利用可能です。<br>
以下カスタムコマンドとなります。

```
1:python manage.py scrape
2:python manage.py classifier_original
```

## Improve classification performance
```
gensimやscikit-learnを用いた手法も試したが、「独自実装したナイーブベイズ分類機」が一番精度が良かったので採用している。
そこで、既存のナイーブベイズ分類機の精度を上げる方法を模索した。
gensimで特徴語辞書を作成した際に、明らかに不必要である記号や数字が含まれていたので、Mecabで形態素解析されたデータを確認すると、「Mecabの仕様で名詞に分類されてしまっている記号」、「数字」が含まれていた。
そこで、正規表現を用いてそれらを除去する事にした。
その結果、精度が約2％ほど上がった。
```
