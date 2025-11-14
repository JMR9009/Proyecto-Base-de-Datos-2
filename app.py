from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)


def conexion():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=ClinicaMedica;'
        'UID=usuario_sql;'
        'PWD=beatriz1902'
    )


@app.route('/api/pacientes', methods=['GET'])
def obtener_pacientes():
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes")
    columnas = [col[0] for col in cursor.description]
    pacientes = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return jsonify(pacientes)


@app.route('/api/pacientes/<int:id>', methods=['GET'])
def obtener_paciente(id):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE IdPaciente = ?", (id,))
    fila = cursor.fetchone()
    conn.close()
    if fila:
        columnas = [col[0] for col in cursor.description]
        paciente = dict(zip(columnas, fila))
        return jsonify(paciente)
    else:
        return jsonify({"mensaje": "Paciente no encontrado"}), 404


@app.route('/api/pacientes', methods=['POST'])
def agregar_paciente():
    datos_lista = request.get_json()  # Esto ahora será una lista de diccionarios
    conn = conexion()
    cursor = conn.cursor()
    
    for datos in datos_lista:  # Iteramos sobre cada paciente
        cursor.execute("""
            INSERT INTO Pacientes (Nombre, Apellido, FechaNacimiento, Sexo, Telefono, Direccion, Email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datos['Nombre'], datos['Apellido'], datos['FechaNacimiento'], datos['Sexo'],
            datos.get('Telefono', None), datos.get('Direccion', None), datos.get('Email', None)
        ))
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": f"{len(datos_lista)} pacientes agregados correctamente"}), 201


@app.route('/api/pacientes/<int:id>', methods=['PUT'])
def actualizar_paciente(id):
    datos = request.json
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Pacientes
        SET Nombre=?, Apellido=?, FechaNacimiento=?, Sexo=?, Telefono=?, Direccion=?, Email=?
        WHERE IdPaciente=?
    """, (
        datos['Nombre'], datos['Apellido'], datos['FechaNacimiento'], datos['Sexo'],
        datos['Telefono'], datos['Direccion'], datos['Email'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Paciente actualizado correctamente"})


@app.route('/api/pacientes/<int:id>', methods=['DELETE'])
def eliminar_paciente(id):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pacientes WHERE IdPaciente = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Paciente eliminado correctamente"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
