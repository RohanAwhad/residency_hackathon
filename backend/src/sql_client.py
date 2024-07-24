# #postgress client
#
# import psycopg2
#
#
# '''
# import psycopg2
#
# conn = psycopg2.connect(
#     database="geeks", user='postgres',
#   password='root', host='localhost', port='5432'
# )
#
# conn.autocommit = True
# cursor = conn.cursor()
#
# sql = ''''''CREATE TABLE employees(emp_id int,emp_name varchar, \
# salary decimal); ''''''
#
# cursor.execute(sql)
#
# conn.commit()
# conn.close()
# '''
#
# class PostgresClient:
#
#     def __init__(self, host, database, user, password):
#         self.host = host
#         self.database = database
#         self.user = user
#         self.password = password
#
#     def get_connection(self):
#         return psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
#
#
#     def get_cursor(self, connection):
#         return connection.cursor()
#
#     def init_connection_and_cursor(self):
#         connection = self.get_connection()
#         cursor = self.get_cursor(connection)
#         return connection, cursor
#
#     def execute_query(self, query):
#         connection, cursor = self.init_connection_and_cursor()
#         cursor.execute(query)
#         return cursor
#