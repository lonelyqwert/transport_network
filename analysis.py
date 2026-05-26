import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import Counter

DB_NAME = 'transport.db'

def run_analysis():
    try:
        conn = sqlite3.connect(DB_NAME)
        stops_df = pd.read_sql_query("SELECT * FROM stops", conn)
        links_df = pd.read_sql_query("SELECT * FROM links", conn)
        conn.close()

        if stops_df.empty or links_df.empty:
            print("Ошибка: таблицы stops или links пусты. Сначала запусти db.py")
            return

        center_stops = stops_df[stops_df['district'] == 'Center']
        print("Остановки в центре:", len(center_stops))
        links_with_district = links_df.merge(stops_df[['stop_id', 'district']],
                                             left_on='from_stop_id',
                                             right_on='stop_id')
        avg_travel_by_district = links_with_district.groupby('district')['travel_minutes'].agg(['mean', 'count'])
        print("\nСреднее время перегонов по районам:")
        print(avg_travel_by_district)

        print("\nПропуски в links_df:\n", links_df.isnull().sum())

        district_counts = stops_df['district'].value_counts()
        print("\nКоличество остановок по районам:\n", district_counts)

        links_df['travel_hours'] = links_df['travel_minutes'] / 60
        print("\nПервые 5 строк links_df с новым столбцом travel_hours:\n",
              links_df[['link_id', 'travel_minutes', 'travel_hours']].head())
        os.makedirs('report', exist_ok=True)

        # график bar - количество остановок по районам
        plt.figure(figsize=(8, 5))
        district_counts.plot(kind='bar', color='skyblue')
        plt.title('Количество остановок по районам')
        plt.xlabel('Район')
        plt.ylabel('Количество остановок')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig('report/stop_districts.png')
        plt.close()

        # график  hist - распределение travel_minutes
        plt.figure(figsize=(8, 5))
        plt.hist(links_df['travel_minutes'], bins=10, color='lightgreen', edgecolor='black')
        plt.title('Распределение времени перегонов (минуты)')
        plt.xlabel('Время в минутах')
        plt.ylabel('Частота')
        plt.tight_layout()
        plt.savefig('report/travel_hist.png')
        plt.close()

        # график subplots -  степени входящих и исходящих узлов
        in_degrees = Counter(links_df['to_stop_id'])
        out_degrees = Counter(links_df['from_stop_id'])

        in_deg_vals = list(in_degrees.values())
        out_deg_vals = list(out_degrees.values())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        if in_deg_vals:
            ax1.hist(in_deg_vals, bins=range(1, max(in_deg_vals) + 2), color='salmon', edgecolor='black')
        else:
            ax1.text(0.5, 0.5, 'Нет данных', transform=ax1.transAxes, ha='center')
        ax1.set_title('Распределение входящих степеней')
        ax1.set_xlabel('Количество входящих связей')
        ax1.set_ylabel('Количество остановок')

        if out_deg_vals:
            ax2.hist(out_deg_vals, bins=range(1, max(out_deg_vals) + 2), color='lightblue', edgecolor='black')
        else:
            ax2.text(0.5, 0.5, 'Нет данных', transform=ax2.transAxes, ha='center')
        ax2.set_title('Распределение исходящих степеней')
        ax2.set_xlabel('Количество исходящих связей')
        ax2.set_ylabel('Количество остановок')

        plt.tight_layout()
        plt.savefig('report/degrees.png')
        plt.close()

        print("\nГрафики сохранены в папку report/")

    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    except KeyError as e:
        print(f"Ошибка: столбец {e} не найден в данных. Проверь структуру таблиц.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    run_analysis()