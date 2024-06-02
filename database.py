import json
import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='official_website',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def load_attraction_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['result']['results']

def filter_image_urls(attraction_data):
    for attraction in attraction_data:
        attraction['images'] = [url for url in attraction['file'].split(',') if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

def save_attractions_to_db(attraction_data):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    for attraction in attraction_data:
        sql = "INSERT INTO attractions (rate, direction, name, date, longitude, REF_WP, avBegin, langinfo, MRT, SERIAL_NO, RowNumber, CAT, MEMO_TIME, POI, file, idpt, latitude, description, avEnd, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (
            attraction['rate'], attraction['direction'], attraction['name'], attraction['date'], attraction['longitude'], attraction['REF_WP'],
            attraction['avBegin'], attraction['langinfo'], attraction['MRT'], attraction['SERIAL_NO'], attraction['RowNumber'], attraction['CAT'],
            attraction['MEMO_TIME'], attraction['POI'], attraction['file'], attraction['idpt'], attraction['latitude'], attraction['description'],
            attraction['avEnd'], attraction['address']
        )
        cursor.execute(sql, val)
        db_connection.commit()

    cursor.close()
    db_connection.close()

def main():
    filename = 'data/taipei-attractions.json'
    attraction_data = load_attraction_data(filename)
    filter_image_urls(attraction_data)
    save_attractions_to_db(attraction_data)

if __name__ == "__main__":
    main()