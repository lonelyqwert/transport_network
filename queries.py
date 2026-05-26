import sqlite3

DB_NAME = 'transport.db'

def run_query(query, params=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"Ошибка SQL: {e}")
        return []

def query1(district):
    sql = '''
        SELECT name, district
        FROM stops
        WHERE district = ?
        ORDER BY name
        LIMIT 5
    '''
    return run_query(sql, (district,))

def query2():
    sql = '''
        SELECT district, COUNT(*) as cnt
        FROM stops
        GROUP BY district
        HAVING cnt > 8
    '''
    return run_query(sql)

def query3(limit=10):
    sql = '''
        SELECT l.link_id, 
               s1.name AS from_stop, 
               s2.name AS to_stop, 
               l.travel_minutes, 
               l.line_number
        FROM links l
        INNER JOIN stops s1 ON l.from_stop_id = s1.stop_id
        INNER JOIN stops s2 ON l.to_stop_id = s2.stop_id
        LIMIT ?
    '''
    return run_query(sql, (limit,))

def query4():
    sql = '''
        SELECT s.stop_id, s.name
        FROM stops s
        LEFT JOIN links l ON s.stop_id = l.from_stop_id
        WHERE l.link_id IS NULL
    '''
    return run_query(sql)

def query5():
    sql = '''
        SELECT name
        FROM stops
        WHERE stop_id IN (
            SELECT DISTINCT from_stop_id
            FROM links
            WHERE travel_minutes > 10
        )
    '''
    return run_query(sql)

