import pandas as pd
import pickle
import matplotlib.pyplot as plt

phases = {2005: 1, 2006: 1, 2007: 1, 2008: 2, 2009: 2, 2010: 2, 2011: 2, 2012: 2, 2013: 3, 2014: 3, 2015: 3, 2016: 3, 2017: 3, 2018: 3, 2019: 3, 2020: 3}
sectors = {1: 'Combustion installations exceeding 20 MW', 2: 'Mineral oil refineries', 3: 'Coke ovens', 4: 'Metal ore roasting or sintering installations',
           5: 'Production of pig iron or steel', 6: 'Production of cement clinker in rotary kilns or lime', 7: 'Manufacture of glass including glass fibre',
           8: 'Manufacture of ceramic products by firing', 9: 'Production of pulp from timber or other fibrous materials paper and board', 10: 'Aircraft operator activities',
           35: 'Production of pulp', 20: 'Combustion of fuels', 21: 'Refining of mineral oil', 22: 'Production of coke', 23: 'Metal ore roasting or sintering',
           24: 'Production of pig iron or steel', 25: 'Production or processing of ferrous metals', 26: 'Production of primary aluminium', 27: 'Production of secondary aluminium',
           28: 'Production or processing of non-ferrous metals', 29: 'Production of cement clinker', 30: 'Production of lime or calcination', 31: 'Manufacture of glass',
           32: 'Manufacture of ceramics', 33: 'Manufacture of mineral wool', 34: 'Production or processing of gypsum or plasterboard', 99: 'Other activity',
           36: 'Production of paper or cardboard', 37: 'Production of carbon black', 38: 'Production of nitric acid', 39: 'Production of adipic acid',
           40: 'Production of glyoxal and glyoxylic acid', 41: 'Production of ammonia', 42: 'Production of bulk chemicals', 43: 'Production of hydrogen and synthesis gas',
           44: 'Production of soda ash and sodium bicarbonate', 45: 'Capture of greenhouse gases', 46: 'Transport of greenhouse gases', 47: 'Storage of greenhouse gases'}
mysectors = {1: 'Combustion', 2: 'Oil', 3: 'Coke', 4: 'Metals', 5: 'Iron', 6: 'Cement', 7: 'Glass', 8: 'Ceramics', 9: 'Paper', 10: 'Aircraft', 20: 'Combustion', 21: 'Oil',
           22: 'Coke', 23: 'Metals', 24: 'Iron', 25: 'Metals', 26: 'Metals', 27: 'Metals', 28: 'Metals', 29: 'Cement', 30: 'Lime', 31: 'Glass', 32: 'Ceramics', 33: 'Isolation',
           34: 'Isolation', 35: 'Paper', 36: 'Paper', 37: 'Metals', 38: 'Chemicals', 39: 'Chemicals', 40: 'Chemicals', 41: 'Chemicals', 42: 'Chemicals', 43: 'Gas', 44: 'Chemicals',
           45: 'CO2', 46: 'CO2', 47: 'CO2', 99: 'Other'}

curves = pickle.load(open('result/result.curves', 'rb'))
countries = pickle.load(open('meta/countries', 'rb'))

merged = pd.merge(curves[(curves['Type']=='AllowanceInAllocation')], curves[(curves['Type']=='VerifiedEmissions')], on=['Reference', 'Country', 'Sector', 'Date'], how='left')

merged = merged.rename(columns = {'Value_x':'Allowance','Value_y':'Emissions'})
merged['MySector'] = merged['Sector']
merged['MySector'].replace(mysectors, inplace=True)
merged = merged[['Reference', 'Country', 'Sector', 'MySector', 'Date', 'Allowance', 'Emissions']]
merged.to_csv('result/result_curves.csv')
print(merged.head())

sumCountrySector = merged.groupby(['Country', 'Sector', 'Date'], as_index=False).sum()
sumCountrySector['Sector'].replace(sectors, inplace=True)
sumCountrySector['Country'].replace(countries, inplace=True)
sumCountrySector.to_csv('result/result_sum.csv', columns=['Country', 'Sector', 'MySector', 'Date', 'Allowance', 'Emissions'])

fig, ax1 = plt.subplots()
sumSector = merged.groupby(by=['MySector', 'Date'], as_index=False)['Allowance', 'Emissions'].sum()
sumSector['Emissions-Allowance'] = sumSector['Emissions'] - sumSector['Allowance']
sumSector = sumSector.pivot(index='Date', columns='MySector', values='Emissions-Allowance')
print(sumSector.head())

ax2 = ax1.twinx()
sumAll = merged.groupby(by=['Date'], as_index=True)['Allowance', 'Emissions'].sum()
print(sumAll.head())
sumAll.plot(ax=ax2, style='--', linewidth=3)
sumSector[['Combustion']].plot(ax=ax2, style='--', linewidth=1)
sumSector.ix[:, sumSector.columns != 'Combustion'].plot(ax=ax1)

fig.tight_layout()
plt.legend()
plt.show()

