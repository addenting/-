import telebot
from telebot import types
import csv
import os
import re
from glob import glob
import time
from dotenv import load_dotenv

load_dotenv()
# Конфигурация
BOT_TOKEN = "7753002573:AAEPGMtrrAQ3SkPC0d2eZdXwpw6um64063M"
CSV_FILES_PATTERN = "data/*.csv"  # Шаблон для поиска CSV файлов
WHITELIST_FILE = "data/whitelist.csv"  # Файл с доверенными пользователями

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def is_in_whitelist(query):
    """Проверяет, есть ли пользователь в whitelist"""
    if not os.path.exists(WHITELIST_FILE):
        return False
    
    try:
        with open(WHITELIST_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'text' in row and query.lower() in row['text'].lower():
                    return True
    except Exception as e:
        print(f"Ошибка проверки whitelist: {e}")
    return False

def get_all_csv_files():
    """Получаем список всех CSV файлов в директории data, исключая whitelist"""
    all_files = glob(CSV_FILES_PATTERN)
    return [f for f in all_files if not f.endswith('whitelist.csv')]

def get_records_count():
    """Подсчет общего количества записей во всех CSV файлах, исключая whitelist"""
    total = 0
    for csv_file in get_all_csv_files():
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                total += sum(1 for _ in f) - 1  # Вычитаем заголовок
        except Exception as e:
            print(f"Ошибка подсчета в файле {csv_file}: {e}")
    return total

def search_in_all_csv(query):
    """Поиск по всем CSV файлам, исключая whitelist"""
    results = []
    for csv_file in get_all_csv_files():
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'text' in row and query.lower() in row['text'].lower():
                        results.append(row)
                        if len(results) >= 5:  # Ограничиваем 5 результатами
                            return results
        except Exception as e:
            print(f"Ошибка поиска в файле {csv_file}: {e}")
    return results

def generate_response(query):
    """Генерирует ответное сообщение на основе запроса"""
    if is_in_whitelist(query):
        return {
            'text': f"*🟢 Пользователь:* `{query}`\n\n🛡 *Данный пользователь является доверенным лицом нашего бота.*",
            'parse_mode': 'Markdown'
        }

    results = search_in_all_csv(query)
    
    if not results:
        return {
            'text': f"*🟡 Пользователь:* `{query}`\n\n🔓 *Пользователь не найден в базе мошенников, несмотря на это рекомендуем проводить сделки с помощью гаранта.*",
            'parse_mode': 'Markdown'
        }
    else:
        response = "*🔴 ВНИМАНИЕ! Пользователь найден в базе мошенников*\n\n"
        response += f"🆔 *Искомый ID:* `{query}`\n\n"
        response += "*Найденные записи:*\n\n"
        
        for row in results:
            channel = row.get('channel', '')
            message_id = row.get('message_id', '')
            link = f"[Ссылка на пост](https://t.me/{channel}/{message_id})"
            
            response += (
                f"📅 *Дата:* `{row.get('date', '')}`\n"
                f"📢 *Канал:* `{channel}`\n"
                f"🔗 {link}\n"
                "────────────────────\n"
            )
        
        response += (
            "_Добавьте этого пользователя в черный список, чтобы избежать проблем!_\n\n"
            "*❗ ОБРАТИТЕ ВНИМАНИЕ: Бот может ошибочно выдавать упоминание человека как внесение его в скам базу "
            "(в некоторых случаях). Нажмите на текст 'Ссылка на пост' и убедитесь, что пользователь действительно "
            "находится в скам-базе.*"
        )
        return {
            'text': response,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }

@bot.message_handler(commands=['start'])
def send_welcome(message):
    records_count = get_records_count()
    
    # Создаем клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup()
    btn_support = types.InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/clubshowman")
    btn_add = types.InlineKeyboardButton(text="☎ Добавить в базу", url="https://t.me/sendscammerbot")
    markup.row(btn_support, btn_add)
    
    bot.send_message(
        message.chat.id,
        "*🔍 Поиск в скам базе*\n"
        "*В базе моего бота находятся самые крупные и актуальные скамеры сети.*\n\n"
        "*🔍 Примеры запросов:*\n"
        "`🆔 7750581694`\n"
        "`🔗 @vetementsup`\n\n"
        "*📥 INLINE-Поиск*:\n"
        "`@aptonscambot 7865237782`\n"
        "`@aptonscambot ducktrust`\n\n"
        "*✨ Анимированный поиск*:\n"
        "`/animation 7865237782`\n\n"
        f"*📝 Количество записей в базе:* `{records_count}`",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(commands=['animation'])
def animation_search(message):
    query = message.text.replace('/animation', '').strip()
    if not query:
        bot.send_message(message.chat.id, "❌ _Введите ID для поиска после команды /animation._", parse_mode="Markdown")
        return
    
    # Список кадров анимации лупы
    animation_frames = [
        "🔍⃠", 
        "🔍⃘", 
        "🔍⃝", 
        "🔍⃟",
        "🔍⃞",
        "🔍⃛",
        "🔍⃜"
    ]
    
    # Отправляем начальное сообщение
    msg = bot.send_message(message.chat.id, "*Поиск в базе...*", parse_mode="Markdown")
    
    # Проигрываем анимацию
    for frame in animation_frames * 2:  # Повторяем анимацию 2 раза
        try:
            time.sleep(0.2)
            bot.edit_message_text(
                f"{frame} *Поиск в базе...*",
                chat_id=message.chat.id,
                message_id=msg.message_id,
                parse_mode="Markdown"
            )
        except:
            pass
    
    # Добавляем финальный кадр с увеличением
    try:
        time.sleep(0.3)
        bot.edit_message_text(
            "🔎 *Анализируем результаты...*",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="Markdown"
        )
        time.sleep(0.5)
    except:
        pass
    
    # Получаем и показываем результат
    try:
        response = generate_response(query)
        bot.edit_message_text(
            text=response['text'],
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode=response.get('parse_mode', None),
            disable_web_page_preview=response.get('disable_web_page_preview', False)
        )
    except Exception as e:
        bot.edit_message_text(
            f"❌ _Ошибка при поиске: {e}_",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda m: True)
def search_messages(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ _Введите ID для поиска._", parse_mode="Markdown")
        return

    csv_files = get_all_csv_files()
    if not csv_files:
        bot.send_message(message.chat.id, "❌ _Базы данных не найдены. Запустите парсер._", parse_mode="Markdown")
        return

    try:
        response = generate_response(query)
        bot.send_message(
            message.chat.id,
            **response
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ _Ошибка: {e}_", parse_mode="Markdown")

@bot.inline_handler(func=lambda query: True)
def handle_inline_query(inline_query):
    try:
        query = inline_query.query.strip()
        if not query:
            return
            
        response = generate_response(query)
        
        # Создаем InlineQueryResultArticle
        r = types.InlineQueryResultArticle(
            id='1',
            title=f'Результат поиска: {query}',
            description='Нажмите чтобы отправить результат в чат',
            input_message_content=types.InputTextMessageContent(
                message_text=response['text'],
                parse_mode=response.get('parse_mode', None),
                disable_web_page_preview=response.get('disable_web_page_preview', False)
            ),
            thumbnail_url='https://img.icons8.com/color/48/000000/search--v1.png'
        )
        
        bot.answer_inline_query(inline_query.id, [r], cache_time=1)
    except Exception as e:
        print(f"Ошибка в inline режиме: {e}")

if __name__ == "__main__":
    print("🔎 Бот запущен...")
    bot.infinity_polling()
