@Grab(group='org.codehaus.groovy.modules.http-builder', module='http-builder', version='0.7.1')
import groovyx.net.http.RESTClient
import hudson.model.Result
import java.time.Year

def call(Map pipelineParams) {

    // Variable Date to day
    def current_date = new Date().format("dd-MM-yyyy")

    // Variable List of Dashboard Supervisor
    def supervisors = ["giselle-gonzalez", "jonathan-otero", "marta-rexach", "luis-benitez"]

    // Variable List of Dashboard IDs
    def dashboard_ids = [
        "c44c5b4c-8991-48bb-a1cc-83db700cd755",
        "a0edf538-ae7a-48c2-be26-56be40fd50c3",
        "d0d8aade-fed0-42b7-ad72-e7dcf09ef28e",
        "b7d1426a-376a-4b0b-b798-41737f506071"
    ]

    // Longitud Variable Supervisors
    def num_supervisors = supervisors.size()

    // URL API New Relic
    def API = "https://insights-api.newrelic.com/v1/accounts/194074/query?nrql="

    // Encabezados de la solicitud (ajusta según tus necesidades)
    def headersList = [
        "Accept": "application/json",
        "X-Query-Key": "IftEAgH1JTbVGtI19-ToCm35sQyVITXH"
    ]

    // Lista de ambientes para iterar
    def entornos = ["Test", "Development", "Production"]

    // Ruta para guardar archivos CSV
    def pathFiles = "csv/"

    pipeline {
        agent any

        stages {
            // Stage to Create Report
            stage('Create CSV Reports') {
                steps {
                    script {
                        echo "Creating CSV Reports..."
                        // Loop for Supervisor
                        supervisors.each { supervisor ->
                            // Replace spaces in the monitor name with underscores for the file name
                            def supervisorFilename = supervisor.replaceAll(" ", "_")
                            // Loop for Environment
                            entornos.each { entorno ->
                                // Storage path
                                def csvFilepath = "${pathFiles}${supervisorFilename}_${entorno}_resultados.csv"
                                def csvFile = new File(csvFilepath)
                                // Create a CSV file for the current supervisor and environment
                                csvFile.withWriter { writer ->
                                    writer.write "App Name,Executions\n"
                                    // Query NRQL in New Relic with current supervisor and environment
                                    def NRQL = "SELECT count(appName) as 'Executions' FROM devsecops_kiuwan_report_last_analysis WHERE supervisor = '${supervisor}' AND environment = '${entorno}' FACET appName LIMIT max SINCE 1 month ago"
                                    // Make the GET request
                                    def client = new RESTClient(API)
                                    def response = client.get(query: [nrql: NRQL], headers: headersList)
                                    if (response.status == 200) {
                                        def data = response.data
                                        def facets = data.facets
                                        facets.each { facet ->
                                            def name = facet.name
                                            def count = facet.results[0].count
                                            writer.write "${name},${count}\n"
                                        }
                                    } else {
                                        echo "Error obtaining results for ${supervisor} in the environment ${entorno}: ${response.status} - ${response.data}"
                                    }
                                }
                            }
                        }
                        echo "CSV Reports Created"
                    }
                }
            }

            // Create Grafana Service
            stage('Create Grafana Service') {
                steps {
                    echo "Creating Grafana Service..."
                    sh "docker-compose up -d"
                    sleep 20
                    echo "Completed start of Grafana Service"
                }
            }

            // Create PDF Reports
            stage('Create PDF Reports') {
                steps {
                    echo "Creating PDF Reports..."
                    sleep 3
                    // Loop Create Report on PDF
                    for (i in 0..<num_supervisors) {
                        def supervisor = supervisors[i]
                        def dashboard_id = dashboard_ids[i]
                        // Docker Command on Grafana Reporter
                        def cmd = "docker exec -it grafana-reporter grafana-reporter -cmd_template ${supervisor} " +
                                  "-cmd_enable=1 -ip grafana:3000 -cmd_dashboard ${dashboard_id} " +
                                  "-cmd_o ./reports/${supervisor}_${current_date}.pdf"
                        sh cmd
                    }
                    echo "PDF Reports Created"
                }
            }

            // Delete Grafana Service
            stage('Delete Grafana Service') {
                steps {
                    echo "Stopping and Deleting Grafana Service..."
                    sleep 2
                    sh "docker-compose down"
                    echo "Stopped and Deleted Grafana Service"
                }
            }

            stage("Clean Workspace") {
                steps {
                    echo "Deleting Workspace..."
                    sleep 2
                    sh "cd .. && rm -r grafana/"
                    echo "Deleted Workspace..."
                }
            }

            stage("Send Notifications") {
                steps {
                    script {
                        echo "Sending Notifications..."
                        // Agrega el código para enviar notificaciones por correo u otros medios
                        // ...
                        echo "Notifications Sent"
                        // Define si la etapa tuvo éxito o falló
                        // Agrega las etapas SUCCESS o FAILURE en función de los resultados
                        // ...
                    }
                }
            }

            // Asegúrate de gestionar los resultados y errores según tus necesidades

            stage("Finalize") {
                steps {
                    // Agrega cualquier acción de finalización que necesites
                }
            }
        }
    }
}
