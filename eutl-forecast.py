import pandas as pd
import numpy as np
import pickle
from sklearn import svm as svm
from sklearn import model_selection
from sklearn import linear_model
from sklearn import preprocessing as pre

sectors = pickle.load(open('meta/sectors', 'rb'))
#columnsPredict = ["previousEmissions", "Allowance", "Ph", "Sector"]
columnsPredict = ["Year", "previousEmissions", "Allowance", "P1", "P2", "P3", "Sector"]


phases = {2005: 1, 2006: 1, 2007: 1, 2008: 2, 2009: 2, 2010: 2, 2011: 2, 2012: 2, 2013: 3, 2014: 3, 2015: 3, 2016: 3, 2017: 3, 2018: 3, 2019: 3, 2020: 3}
curves = pd.read_csv("result/result_curves.csv")
curves['previousEmissions'] = curves['Emissions'].shift(1)
curves.dropna(inplace=True)
curves = curves[(curves['Emissions']>0) & (curves['previousEmissions']>0)].reset_index()
curves['Year'] = pd.DatetimeIndex(curves['Date']).year
curves['Phase'] = pd.DatetimeIndex(curves['Date']).year
curves["Phase"].replace(phases, inplace=True)

binarizer = pre.LabelBinarizer()
binarizerResult = pd.DataFrame(binarizer.fit_transform(curves["Phase"]), columns = ["P1","P2","P3"])
curves = pd.concat([curves, binarizerResult], axis=1)
print(curves.head())
print(len(curves))
counter = round(len(curves) / 2)

pearson = curves.corr(method='pearson')
# assume target attr is the last, then remove corr with itself
corr_with_target = pearson.ix['Emissions']
# attributes sorted from the most predictive
predictivity = corr_with_target.sort_values(ascending=False)
print(predictivity)

def predict(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    score = model.score(X_test,y_test)
    print(name,score)
    predict_y_array = model.predict(X_test)
    return pd.DataFrame(predict_y_array, columns=[name])

curves_train = curves[curves['Year'] < 2016].reset_index()
curves_test = curves[curves['Year'] == 2016].reset_index()
print(curves_test.head())

X_train = curves_train[columnsPredict].as_matrix()
y_train = np.array(curves_train['Emissions'])
X_test = curves_test[columnsPredict].as_matrix()
y_test = np.array(curves_test['Emissions'])


'''
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.4)
#Fixed dataset to compare with different columns
X_train = X[0:counter,:]
X_test = X[counter:,:]
y_train = y[0:counter]
y_test = y[counter:]
'''
scaler = pre.StandardScaler().fit(X_train)

df = pd.DataFrame(X_test, columns=columnsPredict)
dfModel = predict("Linear", linear_model.LinearRegression(), X_train, y_train, X_test, y_test)
df = pd.concat([df, dfModel], axis=1)

dfModel = predict("Linear-Scaled", linear_model.LinearRegression(), scaler.transform(X_train), y_train, scaler.transform(X_test),  y_test)
df = pd.concat([df, dfModel], axis=1)

poly = pre.PolynomialFeatures(degree=2)
dfModel = predict("Linear-Polynomial", linear_model.LinearRegression(), poly.fit_transform(X_train), y_train, poly.fit_transform(X_test), y_test)
df = pd.concat([df, dfModel], axis=1)

df = pd.concat([df, pd.DataFrame(y_test, columns=["Actual"])], axis=1)

print(df.head())
df.to_csv("result/predicted.csv")