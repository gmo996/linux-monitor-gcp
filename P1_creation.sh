export PROJECT_ID="main-dashboard-personal"
export DATASET_NAME="system_metrics"
export TABLE_NAME="pc_performance"
export TOPIC_NAME="linux-metrics-topic"
export SUBSCRIPTION_NAME="linux-metrics-to-bq"
export SCHEMA_NAME="linux-metrics-schema"
export SA_NAME="linux-monitor-sa"

# 1. Crear el "folder" (Dataset) en BigQuery
bq --location=us-central1 mk -d $DATASET_NAME

# 2. Crear la tabla usando el archivo schema.json que acabas de crear
bq mk --table \
  --schema schema_bigquery.json \
  --time_partitioning_type=DAY \
  $PROJECT_ID:$DATASET_NAME.$TABLE_NAME

# 3.1. Crear el esquema de Pub/Sub usando el archivo pubsub_schema.json
gcloud pubsub schemas create $SCHEMA_NAME \
    --type=AVRO \
    --definition-file=pubsub_schema.json

# 3.2 Crear el tópico de Pub/Sub
gcloud pubsub topics create $TOPIC_NAME \
    --schema=$SCHEMA_NAME \
    --message-encoding=JSON




# 7. Crear la cuenta de servicio
gcloud iam service-accounts create $SA_NAME --display-name="Linux Monitor Sender"

# 8. Asignar rol de Publicador al Tópico
gcloud pubsub topics add-iam-policy-binding $TOPIC_NAME \
    --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# 9. Descargar la llave con el NOMBRE y RUTA correctos para tu script
gcloud iam service-accounts keys create ./gcp-keys/monitor-key.json \
    --iam-account="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"





# 4. Obtener el email del servicio de Pub/Sub de Google
export PUBSUB_SERVICE_ACCOUNT="service-$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@gcp-sa-pubsub.iam.gserviceaccount.com"


# 10. Darle permiso a ese servicio para escribir en BigQuery
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SERVICE_ACCOUNT" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SERVICE_ACCOUNT" \
    --role="roles/bigquery.jobUser"

# 5. Crear la suscripción de Pub/Sub que enviará los datos a BigQuery
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
    --topic=$TOPIC_NAME \
    --bigquery-table=$PROJECT_ID:$DATASET_NAME.$TABLE_NAME \
    --use-topic-schema \
    --write-metadata