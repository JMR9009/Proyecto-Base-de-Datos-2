import pyodbc

try:
          connection=pyodbc.connect('DRIVER={SQL Server};SERVER=MANUEL\MSSQL2022;DATABASE=ClinicaMedica')
          print('Conexion Exitosa')
          cursor=connection.cursor()
          cursor.execute('SELECT @@version;')
          row=cursor.fetchone()
          for row in rows:
                  print(row)
          print(row)
except Exception as next:
          print(exec)
finally: 
        connection.close()
        print('Conexion Finalizada')
