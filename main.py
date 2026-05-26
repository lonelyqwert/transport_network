import base
import queries
import analysis
import algorithm


def main():
    print("=== Загрузка базы данных ===")
    base.load_all()

    print("\n=== SQL-запросы ===")
    print("1. Остановки в Center:", queries.query1('Center'))
    print("2. Районы с >8 остановками:", queries.query2())
    print("3. Первые 10 связей:", queries.query3())
    print("4. Остановки без исходящих связей:", queries.query4())
    print("5. Остановки с маршрутами >10 мин:", queries.query5())

    print("\n=== Pandas-анализ и графики ===")
    analysis.run_analysis()

    print("\n=== Дейкстра ===")
    algorithm.main()

if __name__ == "__main__":
    main()