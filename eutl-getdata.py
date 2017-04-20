import pandas as pd
import pickle
import urllib
from lxml import etree
from io import BytesIO
from io import StringIO
import requests
from bs4 import BeautifulSoup

FETCH_NEW = False

def get_country_ids():
    try:
        if FETCH_NEW:
            raise OSError('Fetch data again')
        countries = pickle.load(open('meta/countries', "rb"))
        sectors = pickle.load(open('meta/sectors', "rb"))
    except (OSError, IOError) as e:
        result = requests.get("http://ec.europa.eu/environment/ets/oha.do")
        soup = BeautifulSoup(result.content, "lxml")
        summary = soup.find("select", {"name":"account.registryCodes"})
        titles = [option.text for option in summary.find_all('option')]
        values = [option.get('value') for option in summary.find_all('option')]
        # Remove the first option "-1" for all
        countries = dict(zip(values, titles))
        countries.pop('-1', None)
        pickle.dump(countries, open('meta/countries', "wb"))

        summary = soup.find("select", {"name":"mainActivityType"})
        titles = [option.text for option in summary.find_all('option')]
        values = [int(option.get('value')) for option in summary.find_all('option')]
        sectors = dict(zip(values,titles))
        sectors.pop(-1, None)
        pickle.dump(sectors, open('meta/sectors', "wb"))
    return countries, sectors

def get_file_name(country, sectorCode):
    sector = ".0" if sectorCode == -1 else "." + str(sectorCode)
    return 'data/data.' + country + sector

'''
DO AN ACTUAL DOWNLOAD FROM EUTL https://ec.europa.eu/clima/policies/ets/registry_en > EUTL
ETS >  Operator Holding Accounts > Details All All Phases > Export
Dump the read XML into a locale file for performance
Note that file for HR contains installation DE_200696
'''
def fetch_data(country, sectorCode):
    path = "http://ec.europa.eu/environment/ets/exportEntry.do?" \
           "permitIdentifier=&accountID=&form=ohaDetails&installationIdentifier=&complianceStatus=&primaryAuthRep=&searchType=oha&selectedPeriods=&identifierInReg=&buttonAction=all&account.registryCode=&" \
           "languageCode=en&installationName=&accountHolder=&accountStatus=&accountType=&action=&registryCode=&returnURL=&exportType=1&exportAction=ohaDetails&exportOK=exportOK"
    path += "&account.registryCodes=" + country + "&mainActivityType=" + str(sectorCode)
    f = urllib.request.urlopen(path)
    file = f.read()
    print(get_file_name(country, sectorCode))
    # Need to pickle raw content. Parsed XML is to large.
    pickle.dump(file, open(get_file_name(country, sectorCode), "wb"))
    return file

'''
For Germany 6086 records, exceeds the predefined limit of 3000. Please refine your criteria and try again.
Therefor we can fetch both for country plus sector for the big countries
Set FETCH_NEW if you want to force a new fetch rather than use local store
'''
def fetch_and_cache_data(country, sectorCode, new):
    try:
        if FETCH_NEW:
            raise OSError('Fetch data again')
        file = pickle.load(open(get_file_name(country, sectorCode), "rb"))
    except (OSError, IOError) as e:
        file = fetch_data(country, sectorCode)

    # sometimes we get a small file that is just a HTML saying there is no data. To avoid parse error we return a blank XML object.
    if len(file) < 50000:
        text_obj = BytesIO(file).read().decode('UTF-8')
        if "No results found for your query" in text_obj:
            return etree.parse(StringIO("<export></export>"))
    # discard strings which are entirely white spaces
    myparser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(BytesIO(file), myparser)
    return root
'''
Fetch an XML object per country and sector and iterate through all installations.
Crete a DataFrame with names, id and country
'''
def get_data(country, sector):
    root = fetch_and_cache_data(country, sector, FETCH_NEW)
    InstReferences, InstHolder, InstIDs, InstCountries, InstCity, InstAddress = [], [], [], [], [], []
    InstName, InstStatus, InstSectors, InstLatitude, InstLongitude = [], [], [], [], []
    CurveReferences, CurveCountries, CurveTypes, CurveSectors, CurveDates, CurveValues = [], [], [], [], [], []
    for inst in root.xpath('/export/OHADetails/Account/Installation'):
        country = inst.find('NationalAdministratorCode').text
        id = int(inst.find('InstallationOrAircraftOperatorID').text)
        sector_code = int(inst.find('MainActivityTypeCode').text)
        InstReferences.append(country + "_" + str(id))
        InstCountries.append(country)
        InstCity.append(None if inst.find('City').text == '-' else inst.find('City').text)
        InstLatitude.append(None if inst.find('Latitude') == None else float(inst.find('Latitude').text))
        InstLongitude.append(None if inst.find('Longitude') == None else float(inst.find('Longitude').text))
        InstAddress.append(None if inst.find('Address1') == None else inst.find('Address1').text+("" if inst.find('Address2') == None else ", "+inst.find('Address2').text))
        InstStatus.append(inst.getparent().find('AccountStatus').text)
        InstHolder.append(inst.getparent().find('AccountHolderName').text)
        InstIDs.append(id)
        InstSectors.append(sector_code)
        InstName.append(inst.find('InstallationNameOrAircraftOperatorCode').text)
        for type in ['AllowanceInAllocation', 'VerifiedEmissions']:
            for data in inst.xpath('Compliance/'+type):
                CurveReferences.append(country + "_" + str(id))
                CurveCountries.append(country)
                CurveSectors.append(sector_code)
                CurveTypes.append(type)
                CurveDates.append(pd.to_datetime('01/01/' + data.getparent().find('Year').text, format="%d/%m/%Y"))
                CurveValues.append(None if data.text in ['Excluded', 'Not Reported'] else int(data.text))
    curves = pd.DataFrame({'Reference': CurveReferences, 'Date': CurveDates, 'Value': CurveValues, 'Country': CurveCountries, 'Sector': CurveSectors, 'Type': CurveTypes})
    installations = pd.DataFrame({'Reference': InstReferences, 'Country': InstCountries, 'InstID': InstIDs, 'Sector': InstSectors, 'Name': InstName,
                                  'Status': InstStatus, 'City': InstCity, 'Address': InstAddress, 'Latitude': InstLatitude, 'Longitude': InstLongitude})
    return curves, installations

'''MAIN CODE'''
countries, sectors = get_country_ids()
print(countries)
print(sectors)

'''
Go though all countries and fetch the parsed DataFrame.
For a few big countries fetch by ountry and secor.
Append result of facilities and curves to a common DataFrame using concat.
'''
installations = pd.DataFrame()
curves = pd.DataFrame(dtype=float)
try:
    if FETCH_NEW:
        raise OSError('Fetch data again')
    installations = pickle.load(open('result/result.installations', "rb"))
    curves = pickle.load(open('result/result.curves', "rb"))
except (OSError, IOError) as e:
    for country in countries:
        if country in ['DE', 'GB', 'FR']:
            for sector in sectors:
                new_curves, new_installations = get_data(country, sector)
                print(country, sector, "installations", len(new_installations), "values", len(new_curves))
                installations = pd.concat([installations, new_installations])
                curves = pd.concat([curves, new_curves])
        elif country != 'EU':
            sector = -1
            new_curves, new_installations = get_data(country, sector)
            print(country, sector, "installations", len(new_installations), "values", len(new_curves))
            installations = pd.concat([installations, new_installations])
            curves = pd.concat([curves, new_curves])

    pickle.dump(installations, open('result/result.installations', "wb"))
    pickle.dump(curves, open('result/result.curves', "wb"))

print("#################curves###################")
print(curves.head())
print("#############installations################")
print(installations.head())
print('>>>>>>>>', len(installations), 'installations', len(curves), 'values')