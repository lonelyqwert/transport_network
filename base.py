import sqlite3
import csv
import os

DB_NAME = 'transport.db'
STOPS_CSV = 'stops.csv'
LINKS_CSV = 'links.csv'


def create_schema(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops (
            stop_id INTEGER PRIMARY KEY,
            name TEXT,
            district TEXT,
            lat REAL,
            lon REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            link_id INTEGER PRIMARY KEY,
            from_stop_id INTEGER,
            to_stop_id INTEGER,
            travel_minutes INTEGER,
            line_number INTEGER,
            FOREIGN KEY (from_stop_id) REFERENCES stops(stop_id),
            FOREIGN KEY (to_stop_id) REFERENCES stops(stop_id)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_from_stop ON links(from_stop_id)')
    conn.commit()


def load_stops(conn, csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stops = []
        for row in reader:
            stop_id = int(row['stop_id'])
            name = row['name'] if row['name'] else None
            district = row['district'] if row['district'] else None
            lat = float(row['lat']) if row['lat'] else None
            lon = float(row['lon']) if row['lon'] else None
            stops.append((stop_id, name, district, lat, lon))

    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO stops (stop_id, name, district, lat, lon)
        VALUES (?, ?, ?, ?, ?)
    ''', stops)
    conn.commit()
    print(f"Загружено {len(stops)} остановок.")


def load_links(conn, csv_path):

    cursor = conn.cursor()
    cursor.execute("SELECT stop_id FROM stops")
    valid_stop_ids = {row[0] for row in cursor.fetchall()}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        links = []
        skipped = 0
        for row in reader:
            from_id = int(float(row['from_stop_id']))
            to_id = int(float(row['to_stop_id']))
            if from_id not in valid_stop_ids or to_id not in valid_stop_ids:
                skipped += 1
                continue
            link_id = int(row['link_id'])
            travel_minutes = int(float(row['travel_minutes'])) if row['travel_minutes'] else None
            line_number = int(row['line_number']) if row['line_number'] else None
            links.append((link_id, from_id, to_id, travel_minutes, line_number))

    cursor.executemany('''
        INSERT OR REPLACE INTO links (link_id, from_stop_id, to_stop_id, travel_minutes, line_number)
        VALUES (?, ?, ?, ?, ?)
    ''', links)
    conn.commit()
    print(f"Загружено {len(links)} связей. Пропущено (неверные stop_id): {skipped}")


def load_all():
    try:
        if not os.path.exists(STOPS_CSV) or not os.path.exists(LINKS_CSV):
            raise FileNotFoundError("stops.csv или links.csv не найдены")

        conn = sqlite3.connect(DB_NAME)
        create_schema(conn)
        load_stops(conn, STOPS_CSV)
        load_links(conn, LINKS_CSV)
        conn.close()
        print("База данных готова.")
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")


if __name__ == '__main__':
    load_all()