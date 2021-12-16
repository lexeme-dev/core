from .base_model import *
from .cluster import *
from .opinion import *
from .citation import *
from .cluster_citation import *
from .similarity import *

DEFAULT_SERIALIZATION_ARGS = {
    "exclude": [Cluster.searchable_case_name, Opinion.html_text],
}
