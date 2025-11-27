# 🐧 GCP Linux Monitor

Un agente de monitoreo IoT ligero para Linux (Ubuntu 24.04) que extrae métricas del sistema en tiempo real y las envía a Google Cloud Platform para su análisis histórico.

## 🏗️ Arquitectura
**Linux PC (Python + Systemd)** -> **Cloud Pub/Sub (Schema Avro)** -> **BigQuery Subscription** -> **Looker Studio**

## 🚀 Características
* **Resiliente:** Funciona como un servicio Systemd (Daemon) que arranca automáticamente y se recupera de fallos.
* **Eficiente:** Envío de datos optimizado usando Google Pub/Sub.
* **Seguro:** Autenticación mediante Service Account con principio de menor privilegio.
* **Serverless:** Ingesta directa a BigQuery sin servidores intermedios (Cost-effective).

## 🛠️ Requisitos
* Python 3.12+
* Cuenta de Google Cloud Platform

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/linux-monitor-gcp.git](https://github.com/TU_USUARIO/linux-monitor-gcp.git)
   cd linux-monitor-gcp