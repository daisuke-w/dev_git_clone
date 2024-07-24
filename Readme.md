# アプリケーション名
オリジナルアプリ確認自動化ツール

# アプリケーション概要
オリジナルアプリをローカル環境にクローン、  
Rails環境のセットアップ、サーバー起動、停止作業を
Streamlitアプリ上でボタン操作のみで可能にしたツールです。

# アプリケーションを作成した背景
他の受講生やオンライン受講生の作成したオリジナルアプリを見れる機会が少ない為、  
簡単に確認できるアプリがあるとよいなと思い作成しました。

# 利用方法
- 自身のPCにPythonがインストールされていることが前提です。  
- クローンする対象のリポジトリはTECH CAMPのカリキュラムに則って、  
ruby on railsで作成されたアプリケーションを対象としています。

# 注意点
- クローンするアプリケーションがBasic認証を設定している場合、  
自身のPCの環境変数にIDとPWを設定している必要があります。  

- 全てのアプリケーションを網羅している訳ではない為、起動に失敗する場合があります。

# デモ動画
![git_clone](https://github.com/user-attachments/assets/4ba2fcbe-c76c-425b-a46d-4b6bfccc4381)

## ローカル環境で本ツールを起動する際に使用するコマンド
### 1.本ツールをローカル環境にクローン
git clone https://github.com/daisuke-w/dev_git_clone.git

### 2.dev_git_cloneに移動
cd dev_git_clone/

### 3.仮想環境をアクティブ
source venv/bin/activate

### 4.appに移動
cd app/

### 5.streamlitアプリ起動
streamlit run app.py


## その他コマンド
### 仮想環境から抜ける
deactivate

### ポートを指定してプロセスを確認(本ツールはポート4000を指定してサーバーを起動します)
lsof -i:4000

### プロセスを終了させる
kill id

### ディレクトリを削除
rm -rf dir_name
