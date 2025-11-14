import pyodbc

try:
   
    connection = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=BEATRIZ;UID=usuario_sql;PWD=beatriz1902'
    )
    print("Conexión exitosa al servidor SQL")
    cursor=connection.cursor()
    cursor.execute("SELECT @@version;")
    row=cursor.fetchone()
    print(row)

  

except pyodbc.Error as e:
    print("No se pudo conectar:", e)

