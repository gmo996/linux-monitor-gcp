🚀 Despliegue como Servicio (Systemd)

Para ejecutar este agente en segundo plano automáticamente al iniciar el sistema (Ubuntu/Debian), configuramos un servicio de Systemd.

1. Obtener Rutas Absolutas

El servicio necesita las rutas completas. Ejecuta esto en la terminal del proyecto para obtenerlas:
Bash

echo "Ruta Proyecto: $PWD"
echo "Ruta Python: $PWD/.venv/bin/python"
echo "Ruta Script: $PWD/main.py"

2. Crear archivo de servicio

Crear el archivo de configuración en el sistema:
Bash

sudo nano /etc/systemd/system/linux-monitor.service

3. Configuración del Servicio

Reemplazar <TU_USUARIO> y <TU_RUTA_DEL_PROYECTO> con los valores obtenidos en el paso 1.

Ini, TOML

[Unit]
Description=GCP Linux Monitor Agent
After=network.target

[Service]
Type=simple
# Reemplazar con tu usuario de Linux
User=<TU_USUARIO>

# Reemplazar con la ruta raíz del proyecto
WorkingDirectory=<TU_RUTA_DEL_PROYECTO>

# Reemplazar con la ruta al Python del entorno virtual y al main.py
ExecStart=<TU_RUTA_DEL_PROYECTO>/.venv/bin/python <TU_RUTA_DEL_PROYECTO>/main.py

# Reiniciar automáticamente si falla (ej. error de red)
Restart=on-failure
RestartSec=10

# Evitar buffer en logs para ver prints en tiempo real
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target



4. Activar el Servicio
Comandos para registrar y encender el servicio:

Bash
# Recargar configuración de systemd
sudo systemctl daemon-reload
# Habilitar inicio automático al arrancar PC
sudo systemctl enable linux-monitor.service
# Iniciar el servicio ahora mismo
sudo systemctl start linux-monitor.service



5. Comandos de Gestión y Logs
    
Ver estado:
bash
sudo systemctl status linux-monitor.service

Ver logs en tiempo real (Salida del script):
Bash
journalctl -u linux-monitor.service -f

Reiniciar (tras cambios en el código):
Bash
sudo systemctl restart linux-monitor.service

Detener:
Bash
sudo systemctl stop linux-monitor.service