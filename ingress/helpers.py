import os

from db.sqlalchemy.models import Court

BASE_CL_DIR = os.path.join("data", "cl")

CLUSTER_PATH = "clusters"
OPINION_PATH = "opinions"
CITATIONS_PATH = "citations.csv"

JURISDICTIONS = [
    Court.SCOTUS,
    Court.CA1,
    Court.CA2,
    Court.CA3,
    Court.CA4,
    Court.CA5,
    Court.CA6,
    Court.CA7,
    Court.CA8,
    Court.CA9,
    Court.CA10,
    Court.CA11,
    Court.CADC,
    Court.CAFC,
]
