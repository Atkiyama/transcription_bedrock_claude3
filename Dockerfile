# ベースイメージとしてUbuntuを使用
FROM ubuntu:20.04

# 非対話モードを設定
ENV DEBIAN_FRONTEND=noninteractive

# 必要なライブラリとツールをインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    tzdata \
    && apt-get clean

# 作業ディレクトリを作成
WORKDIR /app

# 必要なファイルを作業ディレクトリにコピー
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY .env .env

# Cythonとmoviepyをインストール
RUN pip install Cython moviepy

# ReazonSpeechリポジトリをクローン
RUN git clone https://github.com/reazon-research/ReazonSpeech

# ReazonSpeechのnemo-asrパッケージをインストール
RUN pip install ReazonSpeech/pkg/nemo-asr

# 必要なPythonパッケージをインストール
RUN pip3 install --no-cache-dir -r requirements.txt

# Streamlitアプリケーションを起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
