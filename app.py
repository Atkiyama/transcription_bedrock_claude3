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
    status_text.text(f"Progress: {percent}%")
    progress_bar.progress(percent)


def transcribe_video_generate_mtg_docs(input_video):
    st.write("---")
    st.write("アップロードされた動画ファイル名:", input_video.name)
    st.write("---")

    status_text = st.empty()
    status_text.text("Progress: 0%")
    progress_bar = st.progress(0)
    st.success("会議の要約生成中...")

    model = load_model()

    st.success("1.音声認識モデルのロード完了", icon="✅")
    draw_progress_bar(status_text, progress_bar, 25)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(input_video.read())
        temp_video_file.seek(0)

        video_clip = VideoFileClip(temp_video_file.name)
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".mp3"
        ) as temp_audio_file:
            video_clip.audio.write_audiofile(temp_audio_file.name, codec="mp3")
            audio = audio_from_path(temp_audio_file.name)

            st.success("2.動画データから音声データへ変換完了", icon="✅")
            draw_progress_bar(status_text, progress_bar, 50)
            ret = transcribe(model, audio)
            st.success("3.音声データから文字起こし完了", icon="✅")
            draw_progress_bar(status_text, progress_bar, 75)

    client = boto3.client("bedrock-runtime")

    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0:200k",
        contentType="application/json",
        body=json.dumps(
            {
                "prompt": "以下の会議の内容を要約してください：\n\n" + ret.text,
                "maxTokens": 4000,
                "temperature": 0.5,
            }
        ),
    )

    message = json.loads(response["body"].read())

    draw_progress_bar(status_text, progress_bar, 100)
    st.success("4.会議の要約作成完了", icon="✅")

    st.download_button(
        label="会議の要約ダウンロード",
        data=message["choices"][0]["text"],
        file_name="mtg_docs.txt",
        mime="text/plain",
    )


st.title("会議要約アプリ(仮)")

input_video = st.file_uploader(
    "会議の動画をアップロードしてください", type=["mp4", "wav"]
)

if st.button("会議の要約開始"):
    if input_video:
        transcribe_video_generate_mtg_docs(input_video)
    else:
        st.error("会議の動画をアップロードしてください")
