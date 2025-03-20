from models import Base, engine

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

print("Base de datos y tabla creadas correctamente.")
