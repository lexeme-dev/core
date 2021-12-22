import gzip
import io
import os
import tarfile
import threading
import urllib.request

from ingress.helpers import BASE_CL_DIR, CITATIONS_PATH, CLUSTER_PATH, OPINION_PATH, JURISDICTIONS
from utils.io import get_full_path

BASE_URL = "https://courtlistener.com/api/bulk-data"
REMOTE_CITATIONS_PATH = "citations/all.csv.gz"


class ClFileDownloader:
    def __init__(self):
        pass

    def download(self):
        for jur in JURISDICTIONS:
            threads = [threading.Thread(target=self.get_data_folder, args=(CLUSTER_PATH, jur)),
                       threading.Thread(target=self.get_data_folder, args=(OPINION_PATH, jur))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.get_citation_csv()

    def get_data_folder(self, resource_type: str, jurisdiction: str):
        print(f"Downloading {resource_type} data for jurisdiction {jurisdiction}...")
        tar_file_bytes = urllib.request.urlopen(self.__get_download_url(resource_type, jurisdiction)).read()
        print(f"Completed {resource_type} data download for jurisdiction {jurisdiction}, extracting...")
        folder_path = self.__get_folder_path(resource_type, jurisdiction)
        tarfile.open(fileobj=io.BytesIO(tar_file_bytes)).extractall(folder_path)
        print(f"Completed extraction of {resource_type} data for jurisdiction {jurisdiction}...")
        return folder_path

    def get_citation_csv(self):
        print("Downloading citations CSV...")
        tar_file_bytes = urllib.request.urlopen(f"{BASE_URL}/{REMOTE_CITATIONS_PATH}").read()
        print("Completed citations data download, extracting...")
        decompressed_file_path = get_full_path(os.path.join(BASE_CL_DIR, CITATIONS_PATH))
        file_contents = gzip.GzipFile(fileobj=io.BytesIO(tar_file_bytes)).read()
        with open(decompressed_file_path, 'wb') as decompressed_file:
            decompressed_file.write(file_contents)
        print("Completed extraction of citations data...")

    def __get_download_url(self, resource_type: str, jurisdiction: str):
        return f"{BASE_URL}/{resource_type}/{jurisdiction}.tar.gz"

    def __get_folder_path(self, resource_type: str, jurisdiction: str):
        return get_full_path(os.path.join(BASE_CL_DIR, resource_type, jurisdiction))


if __name__ == '__main__':
    downloader = ClFileDownloader()
    downloader.download()
