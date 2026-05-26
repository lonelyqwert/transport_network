import sqlite3
import heapq
import os
from typing import List, Tuple, Dict

DB_NAME = 'transport.db'

def get_neighbors(stop_id: int) -> List[Tuple[int, int]]:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT to_stop_id, travel_minutes
            FROM links
            WHERE from_stop_id = ? AND travel_minutes IS NOT NULL
        ''', (stop_id,))
        neighbors = cursor.fetchall()
        conn.close()
        return neighbors
    except sqlite3.Error as e:
        print(f"Ошибка БД в get_neighbors: {e}")
        return []

def dijkstra(from_id: int, to_id: int) -> Tuple[List[int], int]:
    if from_id == to_id:
        return [from_id], 0

    heap = [(0, from_id, [from_id])]
    best_time: Dict[int, int] = {from_id: 0}

    while heap:
        time, current, path = heapq.heappop(heap)

        if current == to_id:
            return path, time

        if time > best_time.get(current, float('inf')):
            continue

        for neighbor, travel in get_neighbors(current):
            if travel is None:
                continue
            new_time = time + travel
            if new_time < best_time.get(neighbor, float('inf')):
                best_time[neighbor] = new_time
                heapq.heappush(heap, (new_time, neighbor, path + [neighbor]))

    return [], float('inf')

def format_path(stop_ids: List[int]) -> None:
    if not stop_ids:
        print("Путь не найден")
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    names = []
    for sid in stop_ids:
        cursor.execute('SELECT name FROM stops WHERE stop_id = ?', (sid,))
        row = cursor.fetchone()
        if row and row[0]:
            names.append(row[0])
        else:
            names.append(f"Остановка {sid} (имя отсутствует)")
    conn.close()
    print(" -> ".join(names))

def main():
    if not os.path.exists(DB_NAME):
        print(f"База {DB_NAME} не найдена. Сначала запусти db.py")
        return

    print("Доступные остановки (первые 10):")
    try:
        conn = sqlite3.connect(DB_NAME)
        stops = conn.execute('SELECT stop_id, name FROM stops LIMIT 10').fetchall()
        for sid, name in stops:
            print(f"  {sid}: {name}")
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return

    try:
        from_id = int(input("\nВведите stop_id начальной остановки: "))
        to_id = int(input("Введите stop_id конечной остановки: "))
    except ValueError:
        print("Ошибка: введите целое число")
        return

    path, total_time = dijkstra(from_id, to_id)
    if path:
        print(f"\nКратчайший путь (время: {total_time} мин):")
        format_path(path)
    else:
        print("Путь не найден. Проверьте корректность ID.")

if __name__ == "__main__":
    main()