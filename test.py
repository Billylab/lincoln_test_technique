from google.cloud import storage
import pandas as pd

source_gcs_project_id = "test01-lincoln-project"
source_gcs_bucket_name = "exercice-python-de-bucket"

gcs_client = storage.Client(project=source_gcs_project_id)
bucket=gcs_client.get_bucket(source_gcs_bucket_name);  
blob=bucket.blob('0_landing/pubmed/pubmed.json')

json_content = blob.download_as_string()
print(json_content)
try:
    df = pd.read_json(path_or_buf=json_content)
except: 
    print(f"Error when reading the JSON file :'{blob.name}'")
    error_file = True
    description = 'Error when reading the JSON file'


print(df)
