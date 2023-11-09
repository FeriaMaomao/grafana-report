import requests
import csv
import os
import json

# URL API New Relic
API = "https://insights-api.newrelic.com/v1/accounts/194074/query?nrql="

# Encabezados de la solicitud (ajusta según tus necesidades)
headersList = {
    "Accept": "application/json",
    "X-Query-Key": "IftEAgH1JTbVGtI19-ToCm35sQyVITXH"
}

# Lista de supervisores para iterar
supervisores = ["Giselle Gonzalez", "Jonathan Otero", "Marta Rexach"]


# Lista de ambientes para iterar
entornos = ["Test", "Development", "Production"]

# Ruta para guardar archivos CSV
path_files = "csv/"

for supervisor in supervisores:

    # Reemplaza espacios en el nombre del supervisor con guiones bajos para el nombre del archivo
    supervisor_filename = supervisor.replace(" ", "_")

    for entorno in entornos:

        # Ruta de almacenamiento
        csv_filepath = os.path.join(path_files, f'{supervisor_filename}_{entorno}_resultados.csv')

        # Crea un archivo CSV para el supervisor y entorno actual
        with open(csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['App Name', 'Executions'])  # Encabezado

            # Consulta NRQL en New Relic con el supervisor actual y entorno
            if supervisor == "Jonathan Otero" and entorno == "Test":
                NRQL = f"SELECT count(appName) as 'Executions' FROM devsecops_kiuwan_report_last_analysis WHERE supervisor = 'Jonathan Otero' AND environment = 'Test' FACET appName LIMIT max SINCE 1 month ago"
            else:
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
