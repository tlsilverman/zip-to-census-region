import os
os.environ["DC_STATEHOOD"] = "1"

import constants
from census import Census
# from us import states
import us
from pathlib import Path
import urllib3
import zipcodes

API_KEY = constants.API_KEY

    # def get_state_from_zipcode(zipcode):

# check if zip/zcta crosswalk file exists, and if not, fetch the file
# this fetch is currently naive, as it only checks whether the local file exists and not whether the two files match (to save bandwidth)
# TODO: decide whether to make this fetch check to see if the files match
# Unnecessary currently, as we plan to use the zipcodes module, which takes regular zip codes and not ZCTA values
def check_crosswalk():
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
    return

# Take a state name and return a region number based on the state's name
def get_region_number(stateName):

    c = Census(API_KEY, year=2010)
    test = c.acs5.state('REGION', us.states.lookup(stateName).fips)
    return test

def main():

    check_crosswalk()

    regionNumber = get_region_number("Maryland")

    print((regionNumber))

if __name__ == "__main__":
    main()
