from backtester.trading_utils import get_stock_symbols, get_stock_data, find_pivots, fill_pivot_gaps
import pandas as pd
import argparse
import json
pd.options.mode.chained_assignment = None  # default='warn'

parser = argparse.ArgumentParser(
                    prog = 'Daily Pivot Check',
                    description = 'Goes through historical data and finds pivot points. Returns stock symbols currently trading within a pivot zone.')

KEYS = ['Min Pivot','Min Fill Ins','Max Pivot','Max Fill Ins']

def get_distance_from_pivot(symbol: str, num_has: int, dist_thresh: float,
                 smooth_period: int, degree: int, keep:int):
    df = get_stock_data(symbol)
    if df.shape[0] >= 200 and df['Close'].mean()>=5:
        df['dates'] = df.index.copy()
        df = df.reset_index(drop=True)
        pivot_df = find_pivots(df.copy(), num_has, dist_thresh, smooth_period, degree)
        df['Min Pivot'] = pivot_df['Min Pivot'].copy()
        #df['Usable Min Date'] = pivot_df['Usable Min Date']
        df['Max Pivot'] = pivot_df['Max Pivot'].copy()
        #df['Usable Max Date'] = pivot_df['Usable Max Date']
        #now to fill in the gaps for two mins or maxes in a row
        pivot_df = fill_pivot_gaps(pivot_df.copy(),'Min Pivot','Max Pivot')
        df['Min Fill Ins'] = pivot_df['Min Pivot']
        df['Max Fill Ins'] = pivot_df['Max Pivot']
        #now that we have the pivots, record them into a dictionary by ticker
        for key in KEYS:
            dist_open = [abs(df['Open'].iloc[-1]-x) for x in df[key].iloc[-1*keep:]]
            dist_high = [abs(df['High'].iloc[-1]-x) for x in df[key].iloc[-1*keep:]]
            dist_low = [abs(df['Low'].iloc[-1]-x) for x in df[key].iloc[-1*keep:]]
            dist_close = [abs(df['Close'].iloc[-1]-x) for x in df[key].iloc[-1*keep:]]
            all_dists = dist_open + dist_high + dist_low + dist_close
            #dists[ticker][key] = min(all_dists)
            min_dist = min(all_dists)
            if key in ['Min Pivot','Max Pivot']:
                for k2 in df[key].iloc[-1*keep:]:
                    if (df['High'].iloc[-1] - k2) >= 0 and (df['Low'].iloc[-1] - k2) <= 0:
                        return {'min_dist':min_dist,'good_tick':True}
                    return {'min_dist':min_dist,'good_tick':False}
    return {'min_dist':None, 'good_tick':None}


    

if __name__ == "__main__":
    parser.add_argument(
        "--keep",
        type=int,
        default = 5,
        help = ""
        )

    parser.add_argument(
        "--num_ha",
        type=int,
        default = 1,
        help = "How many times the heinin-ashi should be derived on the data for smoothing."
        )

    parser.add_argument(
        "--min_dist",
        type=float,
        default=0.01,
        help = ""
        )

    parser.add_argument(
        "--smoothing_period",
        type=int,
        default=5,
        help="Moving average period for smoothing"
        )

    parser.add_argument(
        "--polynomial_degree",
        type=int,
        default=3,
        help=""
        )

    parser.add_argument(
        "--thresh",
        type=float,
        default=0.2,
        help="")

    args = parser.parse_args()

    keep = args.keep
    num_ha = args.num_ha
    min_dist = args.min_dist
    smoothing_period = args.smoothing_period
    poly_degree = args.polynomial_degree
    thresh = args.thresh

    # get the stock symbols list
    symbols = get_stock_symbols(return_all=False)
    ticker_results = []
    ticker_distances_to_pivot = {}
    ticker_status = {}
    for symbol in symbols:
        result = get_distance_from_pivot(symbol, num_ha, min_dist, smoothing_period, poly_degree, keep)
        ticker_results.append(result)
        ticker_distances_to_pivot[symbol] = result['min_dist']
        ticker_status[symbol] = result['good_tick']

    with open('../output_data/daily_pivot_check_result.json','w') as f0:
        json.dump(result, f0)
    with open('../output_data/ticker_distances.json','w') as f1:
        json.dump(ticker_distances_to_pivot, f1)
    with open('../output_data/ticker_status.json','w') as f2:
        json.dump(ticker_status, f2)


    # 



    ##base_path = 'C:/Users/david'
    ##AMEX = pd.read_csv(base_path+'AMEX.csv')
    ##NASDAQ = pd.read_csv(base_path+"NASDAQ.csv")
    ##NYSE = pd.read_csv(base_path+"NYSE.csv")

    ##grand_list = list(AMEX['Symbol']) + list(NASDAQ['Symbol']) + list(NYSE['Symbol'])

    #ticks = pd.read_csv(base_path+'/symbols_for_use.csv')
    #grand_list = symbols.copy()

    #keep = 5

    #HAs = 1
    #dist_away = 0.01
    #smoothing_period = 5
    #degree = 3
    ##daily_pivots_data = {}
    #thresh = 0.2

    #keys = ['Min Pivot','Min Fill Ins','Max Pivot','Max Fill Ins']
    #dists = {}
    #good_ticks = []

    #for i, ticker in enumerate(grand_list):
    #    if i % 100 == 0:
    #        print(str(i)+" of "+str(len(grand_list)))
    #    #print(ticker)
    #    dists[ticker] = {}
    #    raw_data = get_stock_data(ticker)
    #    if raw_data.shape[0] >= 200 and raw_data['Close'].mean()>=5:
    #        #print(ticker)
    #        try:
    #            pivot_data = findPivots(raw_data.copy(), HAs, dist_away, smoothing_period, degree)
    #            raw_data['Min Pivot'] = pivot_data['Min Pivot']
    #            #raw_data['Usable Min Date'] = pivot_data['Usable Min Date']
    #            raw_data['Max Pivot'] = pivot_data['Max Pivot']
    #            #raw_data['Usable Max Date'] = pivot_data['Usable Max Date']
    #            #now to fill in the gaps for two mins or maxes in a row
    #            fill_ins = fillPivotGaps(pivot_data.copy(),'Min Pivot','Max Pivot')
    #            raw_data['Min Fill Ins'] = fill_ins['Min Pivot']
    #            raw_data['Max Fill Ins'] = fill_ins['Max Pivot']
            
    #            #now that we have the pivots, record them into a dictionary by ticker
    #            for key in keys:
    #                dist_open = [abs(raw_data['Open'][-1]-x) for x in raw_data[key][-1*keep:]]
    #                dist_high = [abs(raw_data['High'][-1]-x) for x in raw_data[key][-1*keep:]]
    #                dist_low = [abs(raw_data['Low'][-1]-x) for x in raw_data[key][-1*keep:]]
    #                dist_close = [abs(raw_data['Close'][-1]-x) for x in raw_data[key][-1*keep:]]
    #                all_dists = dist_open + dist_high + dist_low + dist_close
    #                dists[ticker][key] = min(all_dists)
    #                if key in ['Min Pivot','Max Pivot']:
    #                    for k in raw_data[key][-1*keep:]:
    #                        if (raw_data['High'][-1] - k) >= 0 and (raw_data['Low'][-1] - k) <= 0:
    #                            good_ticks.append(ticker)
    #        except:
    #            print("Error with "+str(ticker))

    #print("going through distances")    
    ##now to go through these and find the distances 
    #for ticker in grand_list:
    #    try:
    #        for k in keys:
    #            if dists[ticker][k] <= thresh:
    #                print(ticker+" is within the threshold for "+k)
    #    except:
    #        continue
    
    #for t in good_ticks:
    #    print(t)