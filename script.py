from flask import Flask, request, jsonify, send_file
import os
import yt_dlp
import logging

app = Flask(__name__)

# Установим логирование
logging.basicConfig(level=logging.DEBUG)

# Корневой маршрут для проверки работы сервера
@app.route('/')
def home():
    return 'Сервер работает! Бот готов к работе.', 200

# Основной маршрут для обработки вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Проверяем, что запрос содержит данные
        data = request.json
        if not data or 'message' not in data:
            logging.debug('Пустые данные или отсутствует "message".')
            return jsonify({'error': 'Invalid data'}), 400

        # Извлекаем ссылку из сообщения
        youtube_url = data['message'].get('text')
        if not youtube_url or 'youtube.com' not in youtube_url and 'youtu.be' not in youtube_url:
            logging.debug(f'Неверная ссылка: {youtube_url}')
            return jsonify({'error': 'No valid YouTube URL provided'}), 400

        # Загружаем MP3 файл
        logging.debug(f'Загружаем MP3 из ссылки: {youtube_url}')
        mp3_file = download_youtube_audio(youtube_url)
        if not mp3_file:
            logging.error('Не удалось загрузить MP3 файл.')
            return jsonify({'error': 'Failed to download audio'}), 500

        # Отправляем MP3 файл в ответ
        logging.debug(f'Успешно загрузили MP3: {mp3_file}')
        return send_file(mp3_file, as_attachment=True, mimetype='audio/mpeg', download_name='audio.mp3')

    except Exception as e:
        logging.exception('Ошибка при обработке вебхука:')
        return jsonify({'error': 'Internal server error'}), 500

# Функция для загрузки MP3 с YouTube
def download_youtube_audio(url):
    try:
        # Папка для временного хранения файлов
        output_dir = 'downloads'
        os.makedirs(output_dir, exist_ok=True)

        # Настройки загрузки
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            logging.debug(f'Скачанный файл: {filename}')
            return filename

    except Exception as e:
        logging.exception('Ошибка при загрузке аудио:')
        return None

# Запуск приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
