from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ajusta si tienes contraseña
        database="copa_mundial_jugadores"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adivinar', methods=['POST'])
def adivinar():
    nombre_usuario = request.form['nombre'].strip().lower()
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)

    # Ejecutamos la consulta
    cursor.execute("SELECT * FROM jugadores_campeones WHERE LOWER(nombre) = %s", (nombre_usuario,))
    jugador = cursor.fetchone()  # Tomar el primer resultado

    # Consumimos los resultados para evitar el error "Unread result found"
    cursor.fetchall()  

    cursor.close()
    conn.close()

    if jugador:
        mensaje = f"¡Correcto! {jugador['nombre']} ganó en {jugador['ano']} con {jugador['equipo']}."
    else:
        mensaje = "Incorrecto, intenta de nuevo."

    return jsonify({"mensaje": mensaje})

if __name__ == '__main__':
    app.run(debug=True)