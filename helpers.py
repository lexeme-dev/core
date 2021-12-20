import os.path
from dotenv import load_dotenv


def get_full_path(relative_project_path):
    load_dotenv()
    return os.path.join(os.getenv('PROJECT_PATH'), relative_project_path)
