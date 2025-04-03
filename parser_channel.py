from telethon import TelegramClient
import csv
import asyncio
import os
from datetime import datetime

# Конфигурация
API_ID = 28498140
API_HASH = "b89416509108bf0931497220a301ed37"
SESSION_NAME = "session_name"
CHANNELS = ["GID_ScamBase", "metka_RO", "s_c_a_m_e_r_s_s", "scambase_nft"]
CSV_FILE = "base2.csv"

def read_existing_messages():
    if not os.path.exists(CSV_FILE):
        return set()
    
    existing = set()
    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Создаем уникальный ключ из channel + message_id
            unique_key = f"{row['channel']}_{row['message_id']}"
            existing.add(unique_key)
    return existing

def save_messages(messages, existing_keys):
    # Фильтруем новые сообщения
    new_messages = []
    for msg in messages:
        unique_key = f"{msg['channel']}_{msg['message_id']}"
        if unique_key not in existing_keys:
            new_messages.append(msg)
    
    if not new_messages:
        print("ℹ️ Нет новых сообщений для сохранения")
        return
    
    # Записываем в файл
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["text", "date", "channel", "message_id"])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(new_messages)
    
    print(f"✅ Сохранено {len(new_messages)} новых сообщений")

async def parse_channels(client):
    print("🔄 Парсинг каналов...")
    
    existing_keys = read_existing_messages()
    all_messages = []
    
    for channel in CHANNELS:
        try:
            print(f"⏳ Обработка канала: {channel}")
            channel_messages = []
            async for message in client.iter_messages(channel):
                if message.text:
                    channel_messages.append({
                        "text": message.text.replace('\n', ' ').replace('\r', ' '),
                        "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "channel": channel,
                        "message_id": str(message.id)
                    })
            
            all_messages.extend(channel_messages)
            print(f"✓ {channel}: получено {len(channel_messages)} сообщений")
        except Exception as e:
            print(f"❌ Ошибка в {channel}: {str(e)}")

    save_messages(all_messages, existing_keys)

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await parse_channels(client)

if __name__ == "__main__":
    print("🚀 Запуск парсера...")
    asyncio.run(main())
    print("🛑 Парсер завершил работу")