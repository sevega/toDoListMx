import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["sample_mflix"]
collection = db["tasks"]

# 1. Traer los datos
datos = list(collection.find())

# 2. Crear DataFrame directo (sin pasar por texto/json)
if datos:
    df = pd.DataFrame(datos)
    
    # Convertir el _id a texto para que no estorbe
    df['_id'] = df['_id'].astype(str)

    print("--- Primeros 5 registros ---")
    print(df.head())
    #print(df)

    print("\n--- Estadísticas ---")
    total = len(df)
    completadas = df[df['completed'] == True].shape[0]
    pendientes = total - completadas

    print(f"Total: {total}")
    print(f"Completadas: {completadas}")
    print(f"Pendientes: {pendientes}")
    
    # Evitar división por cero si no hay datos
    if total > 0:
        print(f"Porcentaje completado: {(completadas/total)*100:.2f}%")

        # EXPORTAR A EXCEL
        while True:
            resp_excel = input("\n¿Deseas exportar el reporte a Excel? (S/N): ").strip().upper()
            if resp_excel == 'S':
                # 1. Obtenemos la fecha y hora actual con tu formato AAMMDDhhmm
                timestamp = datetime.now().strftime("%y%m%d%H%M")
                
                # 2. Creamos el nombre dinámico usando una f-string
                nombre_archivo = f"Reporte_Tareas_{timestamp}.xlsx"
                # index=False evita que se guarde la columna de números 0,1,2... a la izquierda
                df.to_excel(nombre_archivo, index=False)
                print(f"✅ ¡Listo! Archivo guardado como '{nombre_archivo}' en esta carpeta.")
                break
            elif resp_excel == 'N':
                print("Omitiendo exportación a Excel.")
                break
            else:
                print("⚠️  Opción no válida. Por favor utiliza 'S' o 'N'.")


    while True:
        # .strip() quita espacios accidentales (ej: " S ")
        # .upper() convierte todo a mayúsculas para aceptar 's' o 'S'
        mensaje = input("\n¿Deseas que elabore la gráfica? (S/N): ").strip().upper()

        if mensaje == 'S':
            print("Generando gráfica...")
            
            etiquetas = ['Completadas', 'Pendientes']
            valores = [completadas, pendientes]
            colores = ['#4CAF50', '#FF5722']

            plt.figure(figsize=(6, 6))
            plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=colores, startangle=140)
            plt.title('Estado de mis Tareas en MongoDB')
            plt.show()
            
            break

        elif mensaje == 'N':
            print("Entendido. No se generará la gráfica.")
            break

        else:
            # Si no es S ni N, imprimimos error y el ciclo vuelve a empezar automáticamente
            print("⚠️  Opción no válida. Por favor utiliza 'S' o 'N'.")

else:
    print("No se encontraron datos en la base de datos.")
