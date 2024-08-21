import datetime as dt
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BDay,DateOffset


class IndexModel:
    
    model_output = pd.DataFrame()
    stock_prices = ''
    
    
    def __init__(self) -> None:
        self.stock_prices = pd.read_csv('stock_prices.csv')
        self.stock_prices['Date'] = pd.to_datetime(self.stock_prices['Date'],format = '%d/%m/%Y')
        

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        
        #--Get the last business day of each month
        calc_date = pd.bdate_range(start = start_date, end = end_date, freq='BMS') - BDay(1)
        calc_date_pd = pd.DataFrame(calc_date,columns = ['Date'])
        
        get_stocks = self.stock_prices.merge(calc_date_pd,on='Date')
        
        #--Calculate the weights based on the market cap
        weights = get_stocks.set_index('Date').apply(lambda x: pd.Series(x.rank(ascending=False)),axis = 1)
        weights[weights==1] = 0.5  #--Highest get weight of 0.5
        weights[weights==2] = 0.25 #--Second highest get weight of 0.25
        weights[weights==3] = 0.25 #--Third highest get weight of 0.5
        weights[weights>3] = 0    #--Rest 0

        #--Calculate two dataframes for beginning and end value for each day
        beg_value = weights.copy()
        end_value = weights.copy()

        beg_value.index = beg_value.index+BDay(2)
        end_value.index = end_value.index+BDay(1)
        
        beg_value_f = self.stock_prices[['Date']].merge(beg_value,on='Date',how='left').ffill()
        end_value_f = self.stock_prices[['Date']].merge(end_value,on='Date',how='left').ffill()
        
        beg_value_f1 = pd.DataFrame(self.stock_prices.set_index('Date').values*beg_value_f.set_index('Date').values,index = self.stock_prices.set_index('Date').index).sum(axis =1)
        end_value_f1 = pd.DataFrame(self.stock_prices.set_index('Date').values*end_value_f.set_index('Date').values,index = self.stock_prices.set_index('Date').index).sum(axis =1)
        
        beg_value_f1 = beg_value_f1.reset_index()
        beg_value_f1.columns = ['Date','beg_val']

        end_value_f1 = end_value_f1.reset_index()
        end_value_f1.columns = ['Date','end_val']
        
        #--Merge two dataframe to get the final table with date,beg value,end value and pct change
        final = beg_value_f1.merge(end_value_f1)
        final['prev_end_val'] = final['end_val'].shift(1)
        final['pct_change'] = ((final['beg_val']/final['prev_end_val']-1)*100).round(2)
        final['pct_change'].replace([np.nan, -np.nan], 0, inplace=True)
        
        final['index_level'] = (final['pct_change'].cumsum()+100)
        
        self.model_output = final.copy()


    def export_values(self, file_name: str) -> None:
        self.model_output[['Date','index_level']].to_csv(file_name,index = False)