#!/bin/bash

# Create Grafana Service
echo "Create Grafana Service..."
docker compose up -d
echo " "
echo "completing start of service..."
echo " "

# Verify Grafana Service
echo "Verifying Grafana Service..."
sleep 20
if [ $? -ne 0 ]; then
    # Mostrar la salida específica de cada contenedor
    docker compose logs

    # Ejecutar docker-compose down
    docker compose down
fi
echo " "
echo "Completing service verification..."
echo " "

# Nombre del contenedor que deseas verificar
CONTAINER_NAME="python-report"

# Bucle hasta que el contenedor esté detenido
while [ "$(docker inspect -f '{{.State.Running}}' "python-report" 2>/dev/null)" == "true" ]; do
    echo "El contenedor python-report está en ejecución. Esperando..."
    sleep 5  # Puedes ajustar el tiempo de espera según tus necesidades
done

echo "El contenedor python-report está detenido."


# Stop Grafana Service
echo "Stoping Grafana Service..."
docker compose down
echo " "
echo "completing stop of service..."
echo " "