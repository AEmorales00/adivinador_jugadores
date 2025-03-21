from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'clave-secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="copa_mundial_jugadores"
    )

# Banco de preguntas (puedes agregar más)
PREGUNTAS = [
    {"texto": "¿El jugador ganó después del año 2000?", "campo": "ano", "operador": ">", "valor": 2000},
    {"texto": "¿El jugador es delantero?", "campo": "posicion", "operador": "=", "valor": "Delantero"},
    {"texto": "¿El jugador es de Brasil?", "campo": "pais", "operador": "=", "valor": "Brasil"},
    {"texto": "¿El equipo con el que ganó es el FC Barcelona?", "campo": "equipo", "operador": "=", "valor": "FC Barcelona"},
]

@app.route('/')
def inicio():
    session['pregunta_actual'] = 0
    session['filtros'] = []
    return render_template('index.html', pregunta=PREGUNTAS[0]['texto'])

@app.route('/respuesta', methods=['POST'])
def respuesta():
    respuesta_usuario = request.json.get('respuesta')
    i = session.get('pregunta_actual', 0)
    filtros = session.get('filtros', [])

    # Guardar filtro si la respuesta fue sí
    if respuesta_usuario == 'si':
        filtros.append(PREGUNTAS[i])

    session['filtros'] = filtros
    session['pregunta_actual'] = i + 1

    # Si ya no hay más preguntas, hacer predicción
    if i + 1 >= len(PREGUNTAS):
        jugadores = filtrar_jugadores(filtros)
        if len(jugadores) == 1:
            return jsonify({"fin": True, "mensaje": f"¿Estás pensando en {jugadores[0]['nombre']}?"})
        elif len(jugadores) > 1:
            nombres = ', '.join([j['nombre'] for j in jugadores])
            return jsonify({"fin": True, "mensaje": f"Pude reducir a varios: {nombres}"})
        else:
            return jsonify({"fin": True, "mensaje": "No encontré coincidencias."})

    # Siguiente pregunta
    return jsonify({"fin": False, "pregunta": PREGUNTAS[i + 1]['texto']})

def filtrar_jugadores(filtros):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM jugadores_campeones"
    condiciones = []
    valores = []

    for f in filtros:
        condiciones.append(f"{f['campo']} {f['operador']} %s")
        valores.append(f['valor'])

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    cursor.execute(query, tuple(valores))
    jugadores = cursor.fetchall()

    cursor.close()
    conn.close()
    return jugadores

if __name__ == '__main__':
    app.run(debug=True)
