from tradingFunctions import *
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

base_path = 'C:/Users/david/Desktop/Trading/Tick Lists/'
#base_path = 'C:/Users/david'
#AMEX = pd.read_csv(base_path+'AMEX.csv')
#NASDAQ = pd.read_csv(base_path+"NASDAQ.csv")
#NYSE = pd.read_csv(base_path+"NYSE.csv")

#grand_list = list(AMEX['Symbol']) + list(NASDAQ['Symbol']) + list(NYSE['Symbol'])

ticks = pd.read_csv(base_path+'/symbols_for_use.csv')
grand_list = list(ticks['Symbol'])

keep = 5

HAs = 1
dist_away = 0.01
smoothing_period = 5
degree = 3
#daily_pivots_data = {}
thresh = 0.2

keys = ['Min Pivot','Min Fill Ins','Max Pivot','Max Fill Ins']
dists = {}
good_ticks = []

for i, ticker in enumerate(grand_list):
    if i % 100 == 0:
        print(str(i)+" of "+str(len(grand_list)))
    #print(ticker)
    dists[ticker] = {}
    raw_data = getStockData(ticker, '2000-01-01', '2021-04-26', '1d',False,False,'')
    if raw_data.shape[0] >= 200 and raw_data['Close'].mean()>=5:
        #print(ticker)
        try:
            pivot_data = findPivots(raw_data.copy(), HAs, dist_away, smoothing_period, degree)
            raw_data['Min Pivot'] = pivot_data['Min Pivot']
            #raw_data['Usable Min Date'] = pivot_data['Usable Min Date']
            raw_data['Max Pivot'] = pivot_data['Max Pivot']
            #raw_data['Usable Max Date'] = pivot_data['Usable Max Date']
            #now to fill in the gaps for two mins or maxes in a row
            fill_ins = fillPivotGaps(pivot_data.copy(),'Min Pivot','Max Pivot')
            raw_data['Min Fill Ins'] = fill_ins['Min Pivot']
            raw_data['Max Fill Ins'] = fill_ins['Max Pivot']
            
            #now that we have the pivots, record them into a dictionary by ticker
            for key in keys:
                dist_open = [abs(raw_data['Open'][-1]-x) for x in raw_data[key][-1*keep:]]
                dist_high = [abs(raw_data['High'][-1]-x) for x in raw_data[key][-1*keep:]]
                dist_low = [abs(raw_data['Low'][-1]-x) for x in raw_data[key][-1*keep:]]
                dist_close = [abs(raw_data['Close'][-1]-x) for x in raw_data[key][-1*keep:]]
                all_dists = dist_open + dist_high + dist_low + dist_close
                dists[ticker][key] = min(all_dists)
                if key in ['Min Pivot','Max Pivot']:
                    for k in raw_data[key][-1*keep:]:
                        if (raw_data['High'][-1] - k) >= 0 and (raw_data['Low'][-1] - k) <= 0:
                            good_ticks.append(ticker)
        except:
            print("Error with "+str(ticker))

print("going through distances")    
#now to go through these and find the distances 
for ticker in grand_list:
    try:
        for k in keys:
            if dists[ticker][k] <= thresh:
                print(ticker+" is within the threshold for "+k)
    except:
        continue
    
for t in good_ticks:
    print(t)
