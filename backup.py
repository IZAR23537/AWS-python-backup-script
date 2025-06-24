# AWS version of backup script
import os
import zipfile
import datetime
import yaml
import logging
import boto3

logging.basicConfig(filename='backup.log', level=logging.INFO)

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def create_backup_zip(source_dir, output_dir="backups"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_name = f"{output_dir}/backup-{timestamp}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), source_dir))
    logging.info(f"Created archive: {zip_name}")
    return zip_name

def upload_to_s3(file_path, bucket, region):
    s3 = boto3.client("s3", region_name=region)
    s3.upload_file(file_path, bucket, os.path.basename(file_path))
    logging.info(f"Uploaded to bucket: {bucket}")

def main():
    try:
        config = load_config()
        path = create_backup_zip(config["backup_dir"])
        upload_to_s3(path, config["s3_bucket"], config.get("region", "us-east-1"))
    except Exception as e:
        logging.error(f"Failed backup: {e}")

if __name__ == "__main__":
    main()
