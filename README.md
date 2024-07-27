以下に、プロジェクトの使用方法を説明する README ファイルの内容を示します。

### README.md

````markdown
# Streamlit 会議要約アプリ

このプロジェクトは、会議の動画をアップロードし、音声を文字起こしし、要約を生成する Streamlit アプリケーションです。音声認識には`reazonspeech`ライブラリを使用し、要約生成には Amazon Bedrock の`anthropic.claude-3-sonnet-20240229-v1:0:200k`モデルを使用しています。

## 必要なファイル

- `app.py`: Streamlit アプリケーションのメインスクリプト
- `requirements.txt`: 必要な Python パッケージを指定するファイル
- `.env`: AWS のアクセスキーとシークレットキーを設定するファイル
- `Dockerfile`: Docker イメージをビルドするためのファイル

## 事前準備

1. **`.env`ファイルの作成**  
   プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の内容を記述します。

   ```dotenv
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   ```

2. **Python スクリプトと依存関係の準備**  
   プロジェクトのルートディレクトリに以下のファイルを配置します。

   - `app.py`:

     ```python
     import streamlit as st
     from reazonspeech.nemo.asr import transcribe, audio_from_path, load_model
     from moviepy.editor import VideoFileClip
     import tempfile
     import boto3
     import os
     import json
     from dotenv import load_dotenv

     # .envファイルを読み込む
     load_dotenv()

     def draw_progress_bar(status_text, progress_bar, percent):
         status_text.text(f'Progress: {percent}%')
         progress_bar.progress(percent)

     def transcribe_video_generate_mtg_docs(input_video):
         st.write("---")
         st.write("アップロードされた動画ファイル名:", input_video.name)
         st.write("---")

         status_text = st.empty()
         status_text.text('Progress: 0%')
         progress_bar = st.progress(0)
         st.success("会議の要約生成中...")

         model = load_model()

         st.success("1.音声認識モデルのロード完了", icon="✅")
         draw_progress_bar(status_text, progress_bar, 25)

         with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
             temp_video_file.write(input_video.read())
             temp_video_file.seek(0)

             video_clip = VideoFileClip(temp_video_file.name)
             with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
                 video_clip.audio.write_audiofile(temp_audio_file.name, codec='mp3')
                 audio = audio_from_path(temp_audio_file.name)

                 st.success("2.動画データから音声データへ変換完了", icon="✅")
                 draw_progress_bar(status_text, progress_bar, 50)
                 ret = transcribe(model, audio)
                 st.success("3.音声データから文字起こし完了", icon="✅")
                 draw_progress_bar(status_text, progress_bar, 75)

         client = boto3.client('bedrock-runtime')

         response = client.invoke_model(
             modelId='anthropic.claude-3-sonnet-20240229-v1:0:200k',
             contentType='application/json',
             body=json.dumps({
                 "prompt": "以下の会議の内容を要約してください：\n\n" + ret.text,
                 "maxTokens": 4000,
                 "temperature": 0.5
             })
         )

         message = json.loads(response['body'].read())

         draw_progress_bar(status_text, progress_bar, 100)
         st.success("4.会議の要約作成完了", icon="✅")

         st.download_button(
             label="会議の要約ダウンロード",
             data=message['choices'][0]['text'],
             file_name='mtg_docs.txt',
             mime='text/plain'
         )

     st.title("会議要約アプリ(仮)")

     input_video = st.file_uploader("会議の動画をアップロードしてください", type=["mp4", "wav"])

     if st.button("会議の要約開始"):
         if input_video:
             transcribe_video_generate_mtg_docs(input_video)
         else:
             st.error("会議の動画をアップロードしてください")
     ```

   - `requirements.txt`:

     ```text
     streamlit
     reazonspeech
     moviepy
     boto3
     python-dotenv
     ```

   - `Dockerfile`:

     ```Dockerfile
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
     ```

## Docker イメージのビルドとコンテナの実行

### Docker イメージのビルド

ターミナルで以下のコマンドを実行して Docker イメージをビルドします。

```sh
docker build -t streamlit-app .
```
````

### Docker コンテナの実行

ビルドが完了したら、以下のコマンドで Docker コンテナを実行します。

```sh
docker run --env-file .env -p 8501:8501 streamlit-app
```

ブラウザで `http://localhost:8501` にアクセスすると、Streamlit アプリケーションが表示されます。

## 環境変数の設定

AWS の認証情報を`.env`ファイルに設定することで、アプリケーションが正常に動作するために必要な環境変数を提供します。`.env`ファイルは以下の形式で作成してください。

```dotenv
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。詳細については LICENSE ファイルを参照してください。

```

このREADMEファイルは、プロジェクトのセットアップ手順、必要なファイル、Dockerイメージのビルドと実行方法について詳しく説明しています。これにより、他の開発者がプロジェクトを簡単にセットアップし、使用することができます。
```
