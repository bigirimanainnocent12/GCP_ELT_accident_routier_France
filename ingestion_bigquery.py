
from  google.cloud import storage, bigquery
import logging
import io
from datetime import datetime


PROJET_ID = "extractionroutier" # Projet ID
BUCKET_NAME = f"{PROJET_ID}_accident_routier" # Nom du bucket

GCP_FOLDER = "fihcier_routier/donnees/" # Dossier dans lequel les fichiers seront stockés

GCP_FOLDER_LOG = "fihcier_routier/logs/"  # Dossier dans lequel les logs seront stockés

storage_client = storage.Client(project=PROJET_ID) # Porte d'entrée dans GCS
bucket = storage_client.bucket(BUCKET_NAME) # Porte d'entrée dans un bucket

client_bigquery=bigquery.Client(project=PROJET_ID,location="US")


log_stream=io.StringIO()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger=logging.getLogger(__name__)

# Handler pour capturer les logs en mémoire (pour GCS)
memory_handler=logging.StreamHandler(log_stream)
memory_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


today=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
def upload_log_to_gcs():
    """Télécharger le fichier de logs dans GCStorage"""    
    gcs_log_path=f"{GCS_FOLDER_LOGS}/chargement_log_{today}.parquet"
    blob=BUCKET.blob(gcs_log_path)
    blob.upload_from_string(log_stream.getvalue())
    logger.info(f"✔ Log enregistre dans GCStorage : {gcs_log_path}")





def creation_database():
    """ Fonction pour  créer les bases de données et les tables si elles n'existent pas """


dataset=[]
for data in  client_bigquery.list_datasets():

    dataset.append(data.dataset_id)

if routes_accident_db not in dataset:
    data=bigquery.Dataset("routes_accident_db")
    data.location="US"
    client_bigquery.create_dataset(routes_accident_db)
    caracteristiques=bigquery.Table("caracteristiques")
    caracteristiques_schema=[

    bigquery.SchemaField("Num_Acc","STRING"),
    bigquery.SchemaField("jour","SMALLINT"),
    bigquery.SchemaField("mois","SMALLINT"),
    bigquery.SchemaField("an","SMALLINT"),
    bigquery.SchemaField("hrmn","STRING"),
    bigquery.SchemaField("lum","STRING"),
    bigquery.SchemaField("agg","STRING"),
    bigquery.SchemaField("int","STRING"),
    bigquery.SchemaField("atm","STRING"),
    bigquery.SchemaField("col","STRING"),
    bigquery.SchemaField("adr","STRING"),
    bigquery.SchemaField("com","STRING"),
    bigquery.SchemaField("adr","STRING"),
    bigquery.SchemaField("gps","STRING"),
    bigquery.SchemaField("lat","STRING"),
    bigquery.SchemaField("long","STRING"),
    bigquery.SchemaField("dep","STRING") 

    ]

    bigquery_client.create_table(caracteristiques,schema=caracteristiques_schema)
    lieux=bigquery.Table("lieux")

    lieux_schema=[
        bigquery.SchemaField("Num_Acc","STRING"),
        bigquery.SchemaField("catr","STRING"),
        bigquery.SchemaField("voie","STRING"),
        bigquery.SchemaField("v1","STRING"),
        bigquery.SchemaField("v2","STRING"),
        bigquery.SchemaField("circ","STRING"),
        bigquery.SchemaField("nbv","STRING"),
        bigquery.SchemaField("pr","STRING"),
        bigquery.SchemaField("pr1","STRING"),
        bigquery.SchemaField("vosp","STRING"),
        bigquery.SchemaField("prof","STRING"),
        bigquery.SchemaField("plan","STRING"),
        bigquery.SchemaField("lartpc","STRING"),
        bigquery.SchemaField("larrout","STRING"),
        bigquery.SchemaField("surf","STRING"),
        bigquery.SchemaField("infra","STRING"),
        bigquery.SchemaField("situ","STRING"),
        bigquery.SchemaField("env1","STRING"),

    ]
    bigquery_client.create_table(lieux,schema=lieux_schema)




    usagers=bigquery.Table("usagers")
    usagers_schema=[
        bigquery.SchemaField("Num_Acc","STRING"),
        bigquery.SchemaField("place","STRING"),
        bigquery.SchemaField("catu","STRING"),
        bigquery.SchemaField("grav","STRING"),
        bigquery.SchemaField("sexe","STRING"),
        bigquery.SchemaField("trajet","STRING"),
        bigquery.SchemaField("secu","STRING"),
        bigquery.SchemaField("locp","STRING"),
        bigquery.SchemaField("actp","STRING"),
        bigquery.SchemaField("etatp","STRING"),
        bigquery.SchemaField("an_nais","STRING"),
        bigquery.SchemaField("num_veh","STRING")
    ]

    bigquery_client.create_table(usagers,schema=usagers_schema)


    vehicules=bigquery.Table("vehicules")
    vehicules_schema=[
        bigquery.SchemaField("Num_Acc","STRING"),
        bigquery.SchemaField("num_veh","STRING"),
        bigquery.SchemaField("senc","STRING"),  
        bigquery.SchemaField("catv","STRING"),
        bigquery.SchemaField("obs","STRING"),
        bigquery.SchemaField("obsm","STRING"),
        bigquery.SchemaField("choc","STRING"),
        bigquery.SchemaField("manv","STRING"),
        bigquery.SchemaField("num_veh","STRING")
    ]

    bigquery_client.create_table(vehicules,schema=vehicules_schema) 

else: logger.info("-> La base de données routes_accident_db existe déjà dans biqquery")     




if __name__=="__main__":

    logger.info("Début du chargement dans BIGQUERY") 
    chargement_fichier()  
    logger.info("Fin de chargement dans BIGQUERY") 
    upload_log_to_gcs()     

