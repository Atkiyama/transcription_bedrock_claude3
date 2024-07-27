# ベースイメージとしてPythonを使用
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app

# 必要なファイルを作業ディレクトリにコピー
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY .env .env

# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Streamlitアプリケーションを起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
