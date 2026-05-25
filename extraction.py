from google.cloud import storage, bigquery
import logging
import io
from datetime import datetime
import requests
import json



# CONFIGURATION

PROJET_ID = "extractionroutier" # Projet ID
BUCKET_NAME = f"{PROJET_ID}_accident_routier" # Nom du bucket

GCP_FOLDER = "fihcier_routier/donnees/" # Dossier dans lequel les fichiers seront stockés

GCP_FOLDER_LOG = "fihcier_routier/logs/"  # Dossier dans lequel les logs seront stockés

API_URL = "https://www.data.gouv.fr/api/1/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/" # URL de l'api routier en France

storage_client = storage.Client(project=PROJET_ID) # Porte d'entrée dans GCS
bucket = storage_client.bucket(BUCKET_NAME) # Porte d'entrée dans un bucket


today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_stream = io.StringIO()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Handler pour capturer les logs en mémoire (pour GCS)
memory_handler = logging.StreamHandler(log_stream)
memory_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(memory_handler)

# FONCTIONS


def fichier_exists(bucket, gcp_path):
    """ Vérifie si un fichier existe dans un bucket Google Cloud Storage.
    Args:
        bucket (Bucket): Instance du bucket GCS dans lequel chercher le fichier.
        gcp_path (str): Chemin complet du fichier dans le bucket.

    Returns:
        bool: True si le fichier existe, False sinon.
    """
    blob = bucket.blob(gcp_path)
    return blob.exists()


def upload_log_to_gcs():
    """Télécharge le fichier de logs dans GCS"""
    gcs_log_path = f"{GCP_FOLDER_LOG}extract_log_{today}.txt"
    blob = bucket.blob(gcs_log_path)
    blob.upload_from_string(log_stream.getvalue())
    logger.info(f"✔ Log uploadé dans GCStorage : {gcs_log_path}")

def extraction_fichier_routier(API_URL:str):
    """Télécharge directement depuis URL vers GCS en streaming (sans stockage local)
    Args:
        API_URL (str): URL de l'api routier en France

    """
    
    response=requests.get(API_URL)
    data=response.json().get("resources", [])
    for resource in data:
        title=resource.get("title") # Titre du fichier
        url=resource.get("url") # URL du fichier
        gcp_path=f"{GCP_FOLDER}{title}" # Chemin complet du fichier dans le bucket
        if fichier_exists(bucket, gcp_path): # Vérifie si le fichier existe déjà
            logger.info(f"-> Le fichier {title} existe déjà dans GCStorage.")
            continue

        try:  
            logger.info(f"-> Téléchargement direct  du fichier {title} vers GCS (streaming)...")
            
            response_fichier=requests.get(url, stream=True, timeout=20)
            if response_fichier.status_code==200:
                blob = bucket.blob(gcp_path)
                with blob.open("wb") as f:
                    for chunk in response_fichier.iter_content(chunk_size=1024 * 1024):
                         if chunk:
                            f.write(chunk)

                logger.info(f"->Téléchargement du {title} réussi dans GCStorage")   

        except requests.exceptions.RequestException as e:
                logger.error(f"-> Erreur réseau pour {title} : {e}")
                continue
        except Exception as e:
                logger.error(f"-> Erreur inattendue pour {title} : {e}")
                continue                                                                                

if __name__ == "__main__":
    logger.info("===== Début de l'extraction =====")
    extraction_fichier_routier(API_URL)
    logger.info("===== Extraction terminée =====")
    upload_log_to_gcs()