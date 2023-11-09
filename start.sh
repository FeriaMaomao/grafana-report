#!/bin/bash

# Variable Date to day
current_date=$(date +"%d-%m-%Y")

# Variable List of Dashboard Supervisor
supervisors=("giselle-gonzalez" "jonathan-otero" "marta-rexach" "luis-benitez")

# Variable List of Dashboard IDs
dashboard_ids=("c44c5b4c-8991-48bb-a1cc-83db700cd755" "a0edf538-ae7a-48c2-be26-56be40fd50c3" "d0d8aade-fed0-42b7-ad72-e7dcf09ef28e" "b7d1426a-376a-4b0b-b798-41737f506071")

# Longitud Variable Supervisors
num_supervisors=${#supervisors[@]}

# Execute Request NRQL to New Relic
echo " "
echo "Create report CSV for Supervisor and Environment"
python3 request-nrql.py
echo " "
echo "Finish Report CSV"
sleep 5
echo " "

# Create Grafana Service
echo "Create Grafana Service..."
docker-compose up -d
echo " "
echo "completing start of service..."
sleep 40
echo " "

# Loop Create Report on PDF
echo "Loop Create Report on PDF..."
sleep 10
# Loop to iterate through Supervisors
for ((i = 0; i < num_supervisors; i++)); do
    supervisor="${supervisors[i]}"
    dashboard_id="${dashboard_ids[i]}"
    # Docker Command on Grafana Reporter
    docker exec -it grafana-reporter grafana-reporter -cmd_template ${supervisor} \
    -cmd_enable=1 -ip grafana:3000 -cmd_dashboard ${dashboard_id} \
    -cmd_o /reports/${supervisor}_${current_date}.pdf
done
echo " "
echo "Create Completed..."
sleep 3
echo " "

# Delete Grafana Service
echo "Stop and Delete Grafana Service..."
sleep 2
docker-compose down
echo " "
echo "Stop and Delete Completed..."
echo " "