from flask import Flask, request, jsonify
import yt_dlp
import requests
import txt
import os
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
app.route('/')
def home():
    return 'Сервер работает!'



app = Flask(__name__)

YOAI_API_KEY = 'ваш_api_ключ'
YOAI_SEND_MESSAGE_URL = 'https://yoai.yophone.com/api/pub/sendMessage'

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'audio.mp3'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', '')
    chat_id = data.get('chat', {}).get('id', '')
    print(data)  # Логируем данные для проверки
    return 'Webhook received', 200

    if 'youtube.com' in message or 'youtu.be' in message:
        mp3_file = download_audio(message)
        files = {'file': open(mp3_file, 'rb')}
        headers = {'X-YoAI-API-Key': YOAI_API_KEY}
        payload = {'chat_id': chat_id, 'caption': 'Ваш MP3 файл'}
        response = requests.post(YOAI_SEND_MESSAGE_URL, headers=headers, data=payload, files=files)
        return jsonify(response.json())
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

