import os
import json
import requests

import db_utils
import data_models
import utils

import time
start = time.monotonic()

url = "https://arxiv.org/pdf/1809.05724"
ref_id = 'b19'
ret = utils.process_reference(url, ref_id)
