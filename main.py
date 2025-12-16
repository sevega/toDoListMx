from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv # <--- 2. Importar dotenv

# 3. Cargar las variables del archivo .env
load_dotenv()

# 4. Obtener la URI desde el entorno (ya no está escrita aquí)
MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["sample_mflix"]
tasks_collection = db.tasks  # nombre de la colección

app = FastAPI(title="To-Do API con MongoDB")

# Modelo Pydantic para las tareas
class TaskBase(BaseModel):
    title: str
    description: str = None
    completed: bool = False

class Task(TaskBase):
    id: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

# Utilidad para convertir ObjectId a str
def task_serializer(task) -> dict:
    task["id"] = str(task["_id"])
    del task["_id"]
    return task

# Rutas de la API

@app.get("/")
async def root():
    return {"mensaje": "¡Bienvenido a mi API de Tareas con MongoDB!"}

@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    new_task = await tasks_collection.insert_one(task.dict())
    created_task = await tasks_collection.find_one({"_id": new_task.inserted_id})
    return task_serializer(created_task)

@app.get("/tasks/", response_model=List[Task])
async def get_tasks():
    tasks = []
    async for task in tasks_collection.find():
        tasks.append(task_serializer(task))
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    from bson import ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task_serializer(task)

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    from bson import ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    return task_serializer(updated_task)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    from bson import ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return
