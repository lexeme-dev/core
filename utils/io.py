import os

from dotenv import load_dotenv


def get_full_path(relative_project_path):
    load_dotenv()
    return os.path.join(os.getenv('PROJECT_PATH'), relative_project_path)


N2V_MODEL_PATH = get_full_path('tmp/n2v_gensim.bin')
CITATION_LIST_CSV_PATH = get_full_path('tmp/citation_list.csv')
NETWORK_CACHE_PATH = get_full_path('tmp/network_cache.pik')
HYPERSCAN_TMP_PATH = get_full_path('tmp/hyperscan')
