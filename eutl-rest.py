import pickle
from flask import Flask

mysectors = {1: 'Combustion', 2: 'Oil', 3: 'Coke', 4: 'Metals', 5: 'Iron', 6: 'Cement', 7: 'Glass', 8: 'Ceramics', 9: 'Paper', 10: 'Aircraft', 20: 'Combustion', 21: 'Oil',
           22: 'Coke', 23: 'Metals', 24: 'Iron', 25: 'Metals', 26: 'Metals', 27: 'Metals', 28: 'Metals', 29: 'Cement', 30: 'Lime', 31: 'Glass', 32: 'Ceramics', 33: 'Isolation',
           34: 'Isolation', 35: 'Paper', 36: 'Paper', 37: 'Metals', 38: 'Chemicals', 39: 'Chemicals', 40: 'Chemicals', 41: 'Chemicals', 42: 'Chemicals', 43: 'Gas', 44: 'Chemicals',
           45: 'CO2', 46: 'CO2', 47: 'CO2', 99: 'Other'}

curves = pickle.load(open('result/result.curves', "rb"))

allowances = curves[(curves['Type']=='AllowanceInAllocation')].groupby(['Sector','Date'], as_index=False).sum()
allowances['Sector'].replace(mysectors, inplace=True)
allowances = allowances[['Sector', 'Date', 'Value']]

emissions = curves[(curves['Type']=='VerifiedEmissions')].groupby(['Sector','Date'], as_index=False).sum()
emissions['Sector'].replace(mysectors, inplace=True)
emissions = emissions[['Sector', 'Date', 'Value']]

app = Flask(__name__)

@app.route("/allowances")
def get_allowances():
    return allowances.to_json(orient='records')

@app.route("/emissions")
def get_emissions():
    return emissions.to_json(orient='records')

if __name__ == "__main__":
    app.run()