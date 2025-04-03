import pandas as pd

# Укажите путь к вашему CSV-файлу
CSV_FILE = "messages.csv"

# Загружаем данные
df = pd.read_csv(CSV_FILE)

# Удаляем символ '@' в столбце 'channel'
df['channel'] = df['channel'].str.replace('@', '', regex=False)

# Сохраняем обратно в CSV
df.to_csv(CSV_FILE, index=False)

print(f"✅ Символ '@' удалён из столбца 'channel' в файле {CSV_FILE}")