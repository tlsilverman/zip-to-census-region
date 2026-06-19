import os
os.environ["DC_STATEHOOD"] = "1"
import sys
import constants
from census import Census
# from us import states
import us
from pathlib import Path
import urllib3
import zipcodes
import csv

API_KEY = constants.API_KEY

REGION_NUMBER_DICT = {
    1: "Northeast",
    2: "Midwest",
    3: "South",
    4: "West",
    9: "Puerto Rico",
    99999: "invalid region"
}

def get_state_from_zipcode(zipcode):
    if (len(zipcode) < 5):
       return "invalid zipcode",False
    formatted_zipcode = '{:.5}'.format(zipcode)

    if not formatted_zipcode.isdigit(): # check for nonstandard strings. TODO: find a way to handle nonstandard (i.e. Canadian) zip codes
        return "invalid zipcode",False
    if not (zipcodes.is_real(formatted_zipcode)): # for now, just skip over non-existent zip codes. TODO: if possible, use city and state name to get real zipcode
        return "non-existent zipcode",False

    # print("fetching state for zipcode ", formatted_zipcode)
    return zipcodes.matching(formatted_zipcode)[0]["state"],True

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

# convert a zip code into a zcta to be used with census API
# returns the ZCTA if there's a match, returns original zipcode if there isn't
# currently doesn't have a use since we can't look up a region number with just a zipcode, but may be useful later
def zip_to_zcta(zipcode):
    crosswalk=open("./crosswalk.csv", "r")
    reader = csv.reader(crosswalk)

    zipString = str(zipcode)
    for line in reader:
        lineZipcode = line[0]
        if lineZipcode == zipString:
            return int(line[1])

    return zipcode

# Take a state name and return a region number based on the state's name
def get_region_number(stateFile):

    c = Census(API_KEY, year=2010)
    test = c.acs5.state('REGION', stateFile.fips)
    if not test:
        return 99999
    return test[0]['REGION']

# retrieves the csv for the incident logs and builds one with 
def construct_export_csv(filename):

    # open file, read csv, check state column
    importFile = open( "./" + filename, "r", encoding="cp1252")
    reader = csv.reader(importFile)

    if Path("./export.csv").is_file():
        os.remove("./export.csv")

    exportFile = open('./export.csv', 'w')
    writer = csv.writer(exportFile)
    
    lineCount = 1
    stateRegionDict = {
        "invalid zipcode": 99999,
        "non-existent zipcode": 99999
    }
    for line in reader:
        t=line[2],line[3],line[1],line[0]
        state = t[0]
        zipcode = t[1]
        city = t[2]
        region = 99999
        skip = False
        region_string = ""

        if ((t[0] == "") or (t[0] == "United States") or (t[0] == "Unspecified")):
            temp = get_state_from_zipcode(t[1])
            if temp[1]:
                stateFile = us.states.lookup(temp[0])
                if stateFile is not None:
                    state = stateFile.name

        if ("SaferProducts.gov" in t[3]):
            skip = True
        if (state == "State"):
            skip = True
            region_string = "Census Region"
        if not (state in stateRegionDict and stateRegionDict[state] == 99999):
            if state not in stateRegionDict:
                stateFile = us.states.lookup(state)
                if stateFile is not None:
                    stateName = stateFile.name
                    if stateName not in stateRegionDict:
                        stateRegionDict[stateName] = get_region_number(stateFile)

                        region = int(stateRegionDict[stateName])
            else:
                region = int(stateRegionDict[state])

        print("current line:",lineCount, end='\r')
        lineCount+=1
        if not skip:
            region_string = REGION_NUMBER_DICT[region]
        csvEntry = t[3], city,state,zipcode,region_string
        writer.writerow(csvEntry)

def main():
    
    check_crosswalk()
    # filename = "IncidentReports through 1-2-26 ZIPs.csv"
    filename = input("Please put the name of the csv file here: ")
    if not Path(filename).is_file():
        print("the file",filename,"is missing. Please add it to the same directory as the current file and run the script again.")
        sys.exit()
    else:
        print("Constructing the csv file...")
        construct_export_csv("IncidentReports through 1-2-26 ZIPs.csv")
        print("\nFinished, check export.csv for the updated file.")
if __name__ == "__main__":
    main()
