from datetime import datetime
from glob import glob
import subprocess
import requests
import json
import time
import csv
import os

# URL API New Relic
API = "https://insights-api.newrelic.com/v1/accounts/194074/query?nrql="

# Encabezados de la solicitud (ajusta según tus necesidades)
headersList = {
    "Accept": "application/json",
    "X-Query-Key": "IftEAgH1JTbVGtI19-ToCm35sQyVITXH"
}

# Variable Date to day
current_date = datetime.now().strftime("%d-%m-%Y")

# Lista de supervisores para consulta NRQL
supervisores = ["Giselle Gonzalez", "Jonathan Otero", "Marta Rexach"]

# Variable Dashboard
dashboard_id = "b0bce249-e631-4440-8aaa-2085538372d8"

# Variable List of Dashboard IDs
# dashboard_ids = [
#     "c44c5b4c-8991-48bb-a1cc-83db700cd755",
#     "a0edf538-ae7a-48c2-be26-56be40fd50c3",
#     "d0d8aade-fed0-42b7-ad72-e7dcf09ef28e",
#     "b7d1426a-376a-4b0b-b798-41737f506071"
# ]

# Lista de ambientes para iterar
entornos = ["Test", "Development", "Production"]

# Longitud Variable Supervisors
num_supervisors = len(supervisores)

# Ruta para guardar archivos CSV
path_files = "csv/"



# Loop to iterate through Supervisors
for i in range(num_supervisors):
    supervisor = supervisores[i]
    # dashboard_id = dashboard_ids[i]

    # Reemplaza espacios en el nombre del supervisor con guiones bajos para el nombre del archivo
    supervisor_filename = supervisor.replace(" ", "_")

    for entorno in entornos:

        # Ruta de almacenamiento
        csv_filepath = os.path.join(path_files, f'{entorno}.csv')

        # Crea un archivo CSV para el supervisor y entorno actual
        with open(csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['App Name', 'Executions'])  # Encabezado

            # Consulta NRQL en New Relic con el supervisor actual y entorno
            NRQL = f"SELECT count(appName) as 'Executions' FROM devsecops_kiuwan_report_last_analysis WHERE supervisor = '{supervisor}' AND environment = '{entorno}' FACET appName LIMIT max SINCE 1 month ago"
            
            # Realiza la solicitud GET
            reqUrl = API + NRQL
            response = requests.get(reqUrl, headers=headersList)

            if response.status_code == 200:
                data = json.loads(response.text)
                facets = data['facets']

                for facet in facets:
                    name = facet['name']
                    count = facet['results'][0]['count']
                    csv_writer.writerow([name, count])

            else:
                print(f'Error al obtener los resultados para {supervisor} en el entorno {entorno}: {response.status_code} - {response.text}')

    # Creación del reporte PDF después de generar el CSV
    command = [
        "docker",
        "exec",
        "grafana-reporter",
        "grafana-reporter",
        "-cmd_template",
        "main",
        "-cmd_enable=1",
        "-ip",
        "grafana:3000",
        "-cmd_dashboard",
        str(dashboard_id),
        "-cmd_o",
        f"/reports/{supervisor}_{current_date}.pdf",
    ]

    subprocess.run(command)

    # Eliminar el archivo CSV después de crear el reporte PDF
    for csv_files in glob(os.path.join(path_files, f'*.csv')):
        os.remove(csv_files)

