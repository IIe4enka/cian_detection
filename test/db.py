import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'wvTreaEwj9ks934',
    'host': 'localhost',
    'port': '5432'
}

# URLs to populate the 'images' table
URLS = [
    "https://avatars.mds.yandex.net/get-bunker/50064/654a49e9c26bd4fb30bbff4d5ffc6228678dd82d/orig",
    "https://images.cdn-cian.ru/images/torgovoe-pomeshcenie-moskva-ulica-sushcevskiy-val-2197645438-1.jpg",
    "https://images.cdn-cian.ru/images/torgovoe-pomeshcenie-moskva-ulica-sushcevskiy-val-2180866246-1.jpg",
    "https://images.cdn-cian.ru/images/torgovoe-pomeshcenie-moskva-ulica-sushcevskiy-val-2181123316-1.jpg",
    "https://images.cdn-cian.ru/images/torgovoe-pomeshcenie-moskva-ulica-sushcevskiy-val-2181116403-1.jpg"
]

def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            is_processed BOOLEAN DEFAULT FALSE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()

def populate_images_table(conn, urls):
    cursor = conn.cursor()
    for url in urls:
        for i in range(20):
            cursor.execute("INSERT INTO images (url) VALUES (%s)", (url,))
    conn.commit()
    cursor.close()

def main():
    conn = connect_to_db()
    if conn:
        create_tables(conn)
        populate_images_table(conn, URLS)
        conn.close()

if __name__ == "__main__":
    main()