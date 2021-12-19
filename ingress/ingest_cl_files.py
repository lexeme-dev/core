import gzip
import io
import os
import tarfile
import threading
import urllib.request

from helpers import get_full_path

JURISDICTIONS = ['scotus', 'ca1', 'ca2', 'ca3', 'ca4', 'ca5', 'ca6',
                 'ca7', 'ca8', 'ca9', 'ca10', 'ca11', 'cadc', 'cafc']

BASE_URL = "https://courtlistener.com/api/bulk-data"
OPINION_ROOT = "opinions"
CLUSTER_ROOT = "clusters"
CITATIONS_REMOTE_PATH = "citations/all.csv.gz"
CITATIONS_LOCAL_PATH = "citations.csv"

FILE_ROOT_DIR = os.path.join("data", "cl")


def get_download_url(resource_type: str, jurisdiction: str):
    return f"{BASE_URL}/{resource_type}/{jurisdiction}.tar.gz"


def get_folder_path(resource_type: str, jurisdiction: str):
    return get_full_path(os.path.join(FILE_ROOT_DIR, resource_type, jurisdiction))


def get_data_folder(resource_type: str, jurisdiction: str):
    print(f"Downloading {resource_type} data for jurisdiction {jurisdiction}...")
    tar_file_bytes = urllib.request.urlopen(get_download_url(resource_type, jurisdiction)).read()
    print(f"Completed {resource_type} data download for jurisdiction {jurisdiction}, extracting...")
    folder_path = get_folder_path(resource_type, jurisdiction)
    tarfile.open(fileobj=io.BytesIO(tar_file_bytes)).extractall(folder_path)
    print(f"Completed extraction of {resource_type} data for jurisdiction {jurisdiction}...")
    return folder_path


def get_citation_csv():
    print("Downloading citations CSV...")
    tar_file_bytes = urllib.request.urlopen(f"{BASE_URL}/{CITATIONS_REMOTE_PATH}").read()
    print("Completed citations data download, extracting...")
    decompressed_file_path = get_full_path(os.path.join(FILE_ROOT_DIR, CITATIONS_LOCAL_PATH))
    file_contents = gzip.GzipFile(fileobj=io.BytesIO(tar_file_bytes)).read()
    with open(decompressed_file_path, 'wb') as decompressed_file:
        decompressed_file.write(file_contents)
    print("Completed extraction of citations data...")


if __name__ == '__main__':
    threads = []
    for jur in JURISDICTIONS:
        threads.append(threading.Thread(target=get_data_folder, args=(CLUSTER_ROOT, jur)))
        threads.append(threading.Thread(target=get_data_folder, args=(CLUSTER_ROOT, jur)))
    threads.append(threading.Thread(target=get_citation_csv))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
