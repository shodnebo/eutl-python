import geocoder
import pickle

installations = pickle.load(open('result/result.installations', "rb"))
countries = pickle.load(open('meta/countries', 'rb'))
installations['CountryCode'] = installations['Country']
installations['Country'].replace(countries, inplace=True)

for index, inst in installations.iterrows():
    if (inst['Latitude'] == None) & (inst['City'] != None) & (inst["CountryCode"] == 'NO'):
        lookup = inst['Name'] + ", "+inst['Address'] + ", " + inst['City'] + ", " + inst['Country']
        g = geocoder.google(lookup)
        if g.lat == None:
            lookup = inst['Address'] + ", " + inst['City'] + ", " + inst['Country']
            g = geocoder.google(lookup)
            if g.lat == None:
                lookup = inst['Name'] + ", " + inst['City'] + ", " + inst['Country']
                g = geocoder.google(lookup)
        print(lookup + ":", g.latlng)
        installations.set_value(index, 'Latitude', g.lat)
        installations.set_value(index, 'Longitude', g.lng)

installations.to_csv('result/result_installations.csv')
