import mysql.connector

class MySQLHandler:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.cnx = None

    def connect(self):
        self.cnx = mysql.connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        return self.cnx

    def execute_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    # def fetch_all(self, query):
    #     cursor = self.cnx.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()
    #     cursor.close()
    #     return result

    # def fetch_one(self, query):
    #     cursor = self.cnx.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchone()
    #     cursor.close()
    #     return result

    def fetch_all(self, query, params=None):
        if not self.cnx or not self.cnx.is_connected():
            self.connect()  # Seu método para reconectar
        cursor = self.cnx.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_one(self, query, params=None):
        cursor = self.cnx.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    def insert(self, table, data):
        query = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s'] * len(data))})"
        cursor = self.cnx.cursor()
        cursor.execute(query, tuple(data.values()))
        self.cnx.commit()
        cursor.close()

    def update(self, table, data, condition):
        query = f"UPDATE {table} SET {', '.join([f'{key} = %s' for key in data.keys()])} WHERE {condition}"
        cursor = self.cnx.cursor()
        cursor.execute(query, tuple(data.values()))
        self.cnx.commit()
        cursor.close()

    def delete(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        cursor = self.cnx.cursor()
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def close(self):
        self.cnx.close()