import time
import json
import socket
import psutil
import GPUtil
import os
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# --- CONFIGURACIÓN ---
# Reemplaza esto con tu ID de proyecto real (lo puedes ver en la terminal con: gcloud config get-value project)
PROJECT_ID = "main-dashboard-personal" 
TOPIC_ID = "linux-metrics-topic"

# Ruta a tu llave de seguridad (la que pusiste en el gitignore)
KEY_PATH = "gcp-keys/monitor-key.json" # Asegúrate que el nombre del archivo coincida

# Autenticación: Le decimos a Python dónde está la llave
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

def get_gpu_info():
    """Intenta obtener info de la GPU NVIDIA si existe."""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].name, gpus[0].load * 100
        return None, 0.0
    except:
        return None, 0.0

def get_top_processes(limit=5):
    """Obtiene los 5 procesos que más RAM consumen."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            # Convertimos a dict y limpiamos datos nulos
            p_info = proc.info
            if p_info['memory_percent']:
                procs.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Ordenar por uso de memoria (mayor a menor) y tomar los top N
    top_procs = sorted(procs, key=lambda p: p['memory_percent'] or 0, reverse=True)[:limit]
    return top_procs

def collect_metrics():
    """Recopila todas las métricas del sistema en un diccionario."""
    gpu_name, gpu_load = get_gpu_info()
    
    # Estructura que coincide con tu Schema de BigQuery
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_name": socket.gethostname(),
        "cpu_model": "Generic x86_64", # Python nativo no da el modelo fácil sin librerías extra
        "cpu_usage_total": psutil.cpu_percent(interval=1),
        "ram_usage_mb": psutil.virtual_memory().used / (1024 * 1024),
        "ram_total_mb": psutil.virtual_memory().total / (1024 * 1024),
        "gpu_model": gpu_name,
        "gpu_usage": gpu_load,
        "temperature": None, # Omitimos temp por compatibilidad simple
        "top_processes": json.dumps(get_top_processes()) # Convertimos array a string JSON para BigQuery
    }
    
    # Intento extra para sacar el modelo de CPU en Linux
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    data["cpu_model"] = line.split(":")[1].strip()
                    break
    except:
        pass

    return data

def publish_message(publisher, topic_path):
    metrics = collect_metrics()
    
    # Convertir diccionario a JSON string y luego a bytes (requerido por Pub/Sub)
    data_str = json.dumps(metrics)
    data_bytes = data_str.encode("utf-8")
    
    try:
        future = publisher.publish(topic_path, data_bytes)
        print(f"[{metrics['timestamp']}] Enviado: CPU {metrics['cpu_usage_total']}% - ID Mensaje: {future.result()}")
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

if __name__ == "__main__":
    # Crear el cliente de Pub/Sub
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    
    print(f"Iniciando agente de monitoreo en: {socket.gethostname()}")
    print(f"Enviando datos a: {topic_path}")
    print("Presiona Ctrl+C para detener.")
    
    try:
        while True:
            publish_message(publisher, topic_path)
            time.sleep(60) # Esperar 60 segundos antes del siguiente envío
    except KeyboardInterrupt:
        print("\nDeteniendo agente...")