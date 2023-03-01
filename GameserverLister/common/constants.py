import os
from datetime import datetime, timezone

ROOT_DIR = rootDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
UNIX_EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)
