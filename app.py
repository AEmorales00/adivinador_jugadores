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

# Banco de preguntas ampliado
PREGUNTAS = [
    {"texto": "¿El jugador ganó después del año 2000?", "campo": "ano", "operador": ">", "valor": 2000},
    {"texto": "¿El jugador ganó antes del año 1990?", "campo": "ano", "operador": "<", "valor": 1990},
    {"texto": "¿El jugador ganó en el año 2010?", "campo": "ano", "operador": "=", "valor": 2010},
    {"texto": "¿El jugador es delantero?", "campo": "posicion", "operador": "=", "valor": "Delantero"},
    {"texto": "¿El jugador es mediocampista?", "campo": "posicion", "operador": "=", "valor": "Mediocampista"},
    {"texto": "¿El jugador es defensor?", "campo": "posicion", "operador": "=", "valor": "Defensor"},
    {"texto": "¿El jugador es portero?", "campo": "posicion", "operador": "=", "valor": "Portero"},
    {"texto": "¿El jugador es de Brasil?", "campo": "pais", "operador": "=", "valor": "Brasil"},
    {"texto": "¿El jugador jugó para Argentina?", "campo": "pais", "operador": "=", "valor": "Argentina"},
    {"texto": "¿El jugador jugó para Alemania?", "campo": "pais", "operador": "=", "valor": "Alemania"},
    {"texto": "¿El equipo con el que ganó es el FC Barcelona?", "campo": "equipo", "operador": "=", "valor": "FC Barcelona"},
    {"texto": "¿El jugador ganó con el Real Madrid?", "campo": "equipo", "operador": "=", "valor": "Real Madrid"},
    {"texto": "¿El jugador ganó con el Bayern Múnich?", "campo": "equipo", "operador": "=", "valor": "Bayern Múnich"},
    {"texto": "¿El jugador ganó con el PSG?", "campo": "equipo", "operador": "=", "valor": "PSG"},
]

@app.route('/')
def inicio():
    session['pregunta_actual'] = 0
    session['filtros'] = []
    session['preguntas_disponibles'] = list(range(len(PREGUNTAS)))
    return render_template('index.html', pregunta=PREGUNTAS[0]['texto'])

@app.route('/respuesta', methods=['POST'])
def respuesta():
    respuesta_usuario = request.json.get('respuesta')
    i = session.get('pregunta_actual', 0)
    filtros = session.get('filtros', [])
    preguntas_disponibles = session.get('preguntas_disponibles', list(range(len(PREGUNTAS))))

    pregunta_actual = PREGUNTAS[preguntas_disponibles[i]]

    # Guardar filtro si la respuesta fue sí
    if respuesta_usuario == 'si':
        filtros.append(pregunta_actual)

    session['filtros'] = filtros
    session['pregunta_actual'] = i + 1

    # Si ya no hay más preguntas, hacer predicción
    if i + 1 >= len(preguntas_disponibles):
        jugadores = filtrar_jugadores(filtros)
        if len(jugadores) == 1:
            return jsonify({"fin": True, "mensaje": f"¿Estás pensando en {jugadores[0]['nombre']}?"})
        elif len(jugadores) > 1:
            nombres = ', '.join([j['nombre'] for j in jugadores])
            return jsonify({"fin": True, "mensaje": f"Pude reducir a varios: {nombres}"})
        else:
            return jsonify({"fin": True, "mensaje": "No encontré coincidencias."})

    # Siguiente pregunta
    siguiente_pregunta = PREGUNTAS[preguntas_disponibles[i + 1]]['texto']
    session['preguntas_disponibles'] = preguntas_disponibles
    return jsonify({"fin": False, "pregunta": siguiente_pregunta})

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
