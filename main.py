import os
os.environ["DC_STATEHOOD"] = "1"

import constants
from census import Census
from us import states
from pathlib import Path
import urllib3

API_KEY = constants.API_KEY

c = Census(API_KEY, year=2024)

# check if zip/zcta crosswalk file exists, and if not, fetch the file
if not Path("./crosswalk.csv").is_file():
    print("downloading crosswalk file...")
    http = urllib3.PoolManager()
    resp = urllib3.request("GET", "https://raw.githubusercontent.com/censusreporter/acs-aggregate/refs/heads/master/crosswalks/zip_to_zcta/zip_zcta_xref.csv", preload_content=False) 
    with open("./crosswalk.csv", 'wb') as out:
        while True:
            data = resp.read(32768)
            if not data:
                break
            out.write(data)
    resp.release_conn()

# fetch region name from ZCTA5
test = c.acs5.state_zipcode(('NAME'), Census.ALL, "03055")

print((test))
