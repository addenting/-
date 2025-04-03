from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel
import pandas as pd

api_id = 28498140  # Ваш API ID (my.telegram.org)
api_hash = "b89416509108bf0931497220a301ed37"   # Ваш API Hash
channel_username = 'giftsmarketspace'  # Юзернейм канала
thread_id = 499  # ID темы из URL (t.me/c/ASTGifts/392)

client = TelegramClient('session_name', api_id, api_hash)
client.start()

all_messages = []

try:
    # Получаем сущность канала
    channel = client.get_entity(channel_username)
    
    # Для форумов используем reply_to вместо thread_id
    for message in client.iter_messages(
        entity=channel,
        reply_to=thread_id  # Ключевое изменение здесь!
    ):
        if message:  # Фильтруем пустые сообщения
            all_messages.append({
                'channel': channel_username,
                'message_id': message.id,
                'text': message.text or "",
                'date': message.date.strftime('%Y-%m-%d %H:%M:%S')
            })
except Exception as e:
    print(f'❌ Ошибка: {e}')

if all_messages:
    df = pd.DataFrame(all_messages)
    df.to_csv('messages.csv', index=False)
    print(f'✅ Сохранено {len(df)} сообщений из темы {thread_id}')
else:
    print('❌ Не удалось получить сообщения. Проверьте:')
    print('1. Доступ бота к каналу')
    print('2. Существование темы')
    print('3. Правильность thread_id')