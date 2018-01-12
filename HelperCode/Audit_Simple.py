'''
Created on Jan 11, 2018

@author: emigre459
'''



import xml.etree.cElementTree as ET
import pprint
import re

OSMFILE = "../data_sample_100_elemsWithTags.osm"


def audit(osmfile, options=None):
    '''
    Audits the OSM file using the different audit functions defined herein.
    
    osm_file: str. Filepath to the OSM file being audited
    options: list of str. Dictates what types of audits are run. Allowed options values:
                        'counting'
                        'zips'
                        'county/state counting'
    
    '''
    
    with open(osmfile, "r") as fileIn:
        if options:
            #Setting up the necessary beginning parameters for each function
            if 'counting' in options:
                tag_counts = {}
            if 'zips' in options:
                zipLength = 5
                zipLengthDict = {zipLength:0, "Non-number": 0}
                known_zips = set()
            if 'county/state counting' in options:
                county_tags = {}
                state_tags = {}
                
    #----------------------------------------------------------------------
            #Iterating through the XML file
            for _, elem in ET.iterparse(fileIn):
                if 'counting' in options:
                    tag_counts = count_tags(elem, tag_counts)
                
                if 'zips' in options:
                    zipLengthDict, known_zips = zipCheck(elem, zipLengthDict, known_zips, digits=zipLength)
                
                if 'county/state counting' in options:
                    county_tags, state_tags = countyStateTypeCounter(elem, county_tags, state_tags)
    
    #----------------------------------------------------------------------    
            #printing everything once done iterating
            if 'counting' in options:
                print("Tags Found")
                pprint.pprint(tag_counts)
            if 'zips' in options:
                print("\nZip Lengths")
                pprint.pprint(zipLengthDict) 
                print("\nUnique Zip Codes")
                pprint.pprint(known_zips)
            if 'county/state counting' in options:
                print("\nTypes of County Tags")
                pprint.pprint(county_tags)
                print("\nTypes of State Tags")
                pprint.pprint(state_tags)
    
    
    

def count_tags(elem, tag_dict):
    '''
    Looks at how many tags in the OSM sample file there are, binning them by unique tag type 
    with tag type as the key and the count found of each tag type as the value.
    
    Reference: This code is taken from the Udacity Data Analyst Nanodegree case study of OpenStreetMap data
    
    elem: ET element.
    tag_dict: dict. Lists all of the tag types seen so far as keys and their frequency of observation as values.
    
    Return: dict. Keys are tag type strings and values are the integer count of that tag type
    '''
    
    if elem.tag not in tag_dict.keys():
        tag_dict[elem.tag] = 1
    else:
        tag_dict[elem.tag] += 1
    
    return tag_dict


def zipCheck(elem, zip_length_dict, knownZips, digits = 5):
    '''
    Checks all of the zip/postal codes contained in an OSM file and counts how many digits are included 
    in each code and then compares that count to a predefined number of digits. Returns the different lengths
    of zip codes it finds. NOTE: this assumes that zip codes are only found as the value of the child tag key
    "addr:postcode"
    
    elem: ET element.
    digits: int. Number of digits expected for a zip code
    
    Returns: dict. Keys are zip code type identifiers (primarily digit counts) and values are the number of those
                    type identified.
    '''
    
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "addr:postcode":
                tempZip = tag.attrib['v'].strip()
                
                #check to see if tempZip only has numbers in it
                if tempZip.isdigit():
                    knownZips.add(tempZip)
                    
                    if len(tempZip) in zip_length_dict.keys():
                        zip_length_dict[len(tempZip)] += 1                        
                    else:
                        zip_length_dict[len(tempZip)] = 1
                else:
                    tempZip = re.sub("\D", "", tempZip) #replaces every non-digit char in tempZip with ""
                    print("Found a zip code with more than numbers!")
                    zip_length_dict["Non-number"] += 1
                    knownZips.add(tempZip)

    return zip_length_dict, knownZips

def countyStateTypeCounter(elem, county_types={}, state_types={}):
    '''
    Checks for the presence of a tag with 'county' included in the key and returns a dict with that tag
    key recorded as a key in the dict, mapped to a value representing the frequency that key is observed
    
    elem: ET element.
    '''
    county_re = re.compile('county',re.IGNORECASE)  # @UndefinedVariable
    state_re = re.compile('state',re.IGNORECASE)  # @UndefinedVariable
    
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            cty_match = county_re.search(tag.attrib['k'])
            state_match = state_re.search(tag.attrib['k'])
            if cty_match is not None: 
                if tag.attrib['k'] not in county_types.keys():
                    county_types[tag.attrib['k']] = 1
                else:
                    county_types[tag.attrib['k']] += 1
            elif state_match is not None:
                if tag.attrib['k'] not in state_types.keys():
                    state_types[tag.attrib['k']] = 1
                else:
                    state_types[tag.attrib['k']] += 1
            #Special case wherein use of regex is non-obvious
            elif tag.attrib['k'] == "gnis:ST_alpha":
                if tag.attrib['k'] not in state_types.keys():
                    state_types[tag.attrib['k']] = 1
                else:
                    state_types[tag.attrib['k']] += 1
                
                
    return county_types, state_types


def amenityFinder(elem, amenitySet=set()):
    '''
    Checks the element for the presence of an amenity and returns the input set + any new amenity types identified
    '''

#---------------------------------------------
#Main code execution space

audit(OSMFILE, options=['counting', 'zips', 'county/state counting'])