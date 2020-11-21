#################################
##### Name: Hanren Zhang    #####
##### Uniqname: hzhng       #####
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
key = secrets.CONSUMER_KEY
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()):
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text 
        save_cache(cache)
        return cache[url]

CACHE_DICT = load_cache()

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, category, address, zipcode, phone):
        self.name = name
        self.category = category
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        return (self.name + " (" + self.category + "): " + self.address + " " + self.zipcode)


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_website = "https://www.nps.gov"
    response = requests.get(state_website)
    soup = BeautifulSoup(response.text, 'html.parser')
    state_listing_parent = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    state_listing_li = state_listing_parent.find_all('li', recursive=False)
    state_url = dict()
    for states in state_listing_li:
        state_link_tag = states.find('a')
        state_name = state_link_tag.get_text()
        state_link = state_link_tag['href']
        state_details_url = state_website + state_link
        if state_name not in state_url:
            state_url.update({state_name.lower(): state_details_url})
    return state_url


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    name_div = soup.find('div', class_='Hero-titleContainer clearfix')
    name = name_div.find('a').get_text()
    try:
        category_div = soup.find('div', class_='Hero-designationContainer')
        category = category_div.find('span', class_="Hero-designation").get_text()
    except: category = "Not found category"
    if category == "":
        category = "Not found category"
    try:
        address_div = soup.find('div', itemprop='address')
        address_sub_1 = address_div.find('span', itemprop="addressLocality").get_text()
        address_sub_2 = address_div.find('span', itemprop="addressRegion").get_text()
        address = address_sub_1 + ", " + address_sub_2
    except:
        address = "Not found address"
    try:
        zipcode = address_div.find('span', itemprop="postalCode").get_text().strip()
    except:
        zipcode = "Not found zipcode"
    try:
        phone_div = soup.find('div', class_='vcard')
        phone = phone_div.find('span', class_="tel").get_text().strip()
    except:
        phone = "Not found phone"
    
    site_instance = NationalSite(name, category, address, zipcode, phone)
    return site_instance


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    state_website = "https://www.nps.gov"
    response = make_url_request_using_cache(state_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    site_listing_parent = soup.find('ul', id='list_parks')
    site_name_listing_div = site_listing_parent.find_all('div', class_="col-md-9 col-sm-9 col-xs-12 table-cell list_left")
    site_instance_list = []
    site_url = dict()
    for sites in site_name_listing_div:
        site_link_tag = sites.find('h3')
        site_name = site_link_tag.get_text()
        site_link = site_link_tag.find("a")['href']
        site_details_url = state_website + site_link
        if site_name not in site_url:
            site_url.update({site_name: site_details_url})
    for sites in site_url.keys():
        site_instance_list.append(get_site_instance(site_url[sites]))
    return site_instance_list


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    endpoint_url = 'http://www.mapquestapi.com/search/v2/radius'
    params = {'origin': site_object.zipcode, 'radius': 10, 'maxMatches': 10, "ambiguities": "ignore", "outFormat": "json", 'key': key}
    response = requests.get(endpoint_url, params=params)
    results = response.json()
    return results
    

if __name__ == "__main__":
    state_website = "https://www.nps.gov"
    website_info = None
    while True:
        if website_info == None:
            state_name = input("Please enter a state name or exit:\n")
            if state_name.lower() == "exit":
                break
            elif state_name.lower().title() in us_state_abbrev.keys():
                state_abbrev = us_state_abbrev[state_name.lower().title()].lower()
                state_de = "/state/" + "/" + state_abbrev
                website_info = state_website + state_de
                print('-' * 34, "\nList of National Sites in " + state_name.lower().title(), "\n" + '-' * 34)
                instance_list = get_sites_for_state(website_info)
                for instances in instance_list:
                    site_number = instance_list.index(instances) + 1
                    site_name = instances.name
                    site_category = instances.category
                    site_address = instances.address
                    site_zipcode = instances.zipcode
                    print("[" + str(site_number) + "] " + site_name + " (" + site_category + "): " + site_address + " " + site_zipcode)
            else:
                print("[Error] Enter proper state name")
                continue
        else:
            location_number = input("Choose the number for detail search or exit or back:\n")
            if location_number.lower() == "back":
                website_info = None
            elif location_number.lower() == "exit":
                break
            elif location_number in (str(instance_list.index(instances)+1) for instances in instance_list):
                site_info = instance_list[int(location_number) - 1]
                site_name = instance_list[int(location_number) - 1].name
                site_list = get_nearby_places(site_info)
                location_details = site_list['searchResults']
                print('-' * 34, "\nPlaces near " + site_name, "\n" + '-' * 34)
                for dicts in location_details:
                    location_name = dicts['name']
                    location_category = dicts["fields"]['group_sic_code_name_ext']
                    if location_category == "":
                        location_category = "no category"
                    location_street_address = dicts["fields"]['address']
                    if location_street_address == "":
                        location_street_address = 'no address'
                    location_city = dicts["fields"]['city']
                    if location_city == "":
                        location_city = 'no city'
                    print("- " + location_name + " (" + location_category + "): " + location_street_address + ", " + location_city)
                continue
            else:
                print("[Error] Invalid input, try again.")
                continue
    
    
    

    