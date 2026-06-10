import mysql.connector

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class WeatherDatabase:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

    def test_connection(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True

    def get_all(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id,
                weather_date,
                province,
                region,
                temperature,
                humidity,
                precipitation,
                wind_speed,
                pressure,
                weather_code
            FROM weather_data
            ORDER BY id ASC
            LIMIT 300;
        """)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def search_weather(self, province="", region="", from_date="", to_date=""):
        query = """
            SELECT 
                id,
                weather_date,
                province,
                region,
                temperature,
                humidity,
                precipitation,
                wind_speed,
                pressure,
                weather_code
            FROM weather_data
            WHERE 1 = 1
        """
        params = []

        if province:
            query += " AND province LIKE %s"
            params.append(f"%{province}%")

        if region:
            query += " AND region LIKE %s"
            params.append(f"%{region}%")

        if from_date:
            query += " AND weather_date >= %s"
            params.append(from_date)

        if to_date:
            query += " AND weather_date <= %s"
            params.append(to_date)

        query += " ORDER BY weather_date ASC, province ASC LIMIT 300"

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def insert_weather(self, data):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO weather_data
            (
                weather_date,
                province,
                region,
                temperature,
                humidity,
                precipitation,
                wind_speed,
                pressure,
                weather_code,
                source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["weather_date"],
            data["province"],
            data["region"],
            data["temperature"],
            data["humidity"],
            data["precipitation"],
            data["wind_speed"],
            data["pressure"],
            data["weather_code"],
            "GUI"
        ))
        self.connection.commit()
        cursor.close()

    def update_weather(self, record_id, data):
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE weather_data
            SET 
                weather_date = %s,
                province = %s,
                region = %s,
                temperature = %s,
                humidity = %s,
                precipitation = %s,
                wind_speed = %s,
                pressure = %s,
                weather_code = %s
            WHERE id = %s
        """, (
            data["weather_date"],
            data["province"],
            data["region"],
            data["temperature"],
            data["humidity"],
            data["precipitation"],
            data["wind_speed"],
            data["pressure"],
            data["weather_code"],
            record_id
        ))
        self.connection.commit()
        cursor.close()

    def delete_weather(self, record_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM weather_data WHERE id = %s", (record_id,))
        self.connection.commit()
        cursor.close()

    def get_statistics(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_records,
                COUNT(DISTINCT province) AS total_provinces,
                ROUND(AVG(temperature), 2) AS avg_temperature,
                ROUND(AVG(humidity), 2) AS avg_humidity,
                ROUND(MAX(precipitation), 2) AS max_precipitation,
                ROUND(AVG(pressure), 2) AS avg_pressure
            FROM weather_data;
        """)
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_regions(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT region
            FROM weather_data
            WHERE region IS NOT NULL AND region <> ''
            ORDER BY region;
        """)
        rows = cursor.fetchall()
        cursor.close()
        return [row[0] for row in rows]
    

    def get_all_for_export(self):
        cursor = self.connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                 weather_date,
                province,
                region,
                temperature,
                humidity,
                precipitation,
                wind_speed,
                pressure,
                weather_code
            FROM weather_data
            ORDER BY weather_date
        """)

        rows = cursor.fetchall()
        cursor.close()

        return rows
    
    def clear_table(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            DELETE FROM weather_data
        """)

        self.connection.commit()
        cursor.close()


    def insert_many(self, records):
        cursor = self.connection.cursor()

        sql = """
        INSERT INTO weather_data
        (
            weather_date,
            province,
            region,
            temperature,
            humidity,
            precipitation,
            wind_speed,
            pressure,
            weather_code,
            source
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = []

        for row in records:
            values.append((
                row["weather_date"],
                row["province"],
                row["region"],
                row["temperature"],
                row["humidity"],
                row["precipitation"],
                row["wind_speed"],
                row["pressure"],
                row["weather_code"],
                "RESTORE"
            ))

        cursor.executemany(sql, values)

        self.connection.commit()
        cursor.close()

    