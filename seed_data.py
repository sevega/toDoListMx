from pymongo import MongoClient
import os
from dotenv import load_dotenv
import random

# 1. Cargar variables de entorno (para usar tu clave segura)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# 2. Conexión (Usamos MongoClient estándar, no Async)
client = MongoClient(MONGO_URI)
db = client["sample_mflix"]
collection = db["tasks"]

# 3. Generar 20 tareas ficticias en una lista
nuevas_tareas = []
for i in range(1, 21):
    tarea = {
        "title": f"Tarea generada {i}",
        "description": f"Esta es una descripción automática para el registro número {i}",
        "completed": random.choice([True, False]) # Aleatorio entre cumplida o no
    }
    nuevas_tareas.append(tarea)

# 4. Insertar de un solo golpe (Bulk Insert)
resultado = collection.insert_many(nuevas_tareas)

print(f"¡Éxito! Se insertaron {len(resultado.inserted_ids)} documentos.")
print("IDs generados:", resultado.inserted_ids[:3], "...") # Muestra los primeros 3
