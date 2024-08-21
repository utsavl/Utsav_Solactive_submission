# Assessment Index Modelling

Solution by Utsav Lotia

I solved this assessment model test by first reading the csv file which contains all the stock level info. Next, I got the last business day of each month as to get the new weighting for the next month. Next step is to calculate the weights based on the market cap. For this I used the rank function and gave the weights to top 3 stocks. I calculated the beginning and end values for each day since the weighting is effective at the end of first business day. To get the index level, I calculated the percentage difference between the beginning value and end value and add it to 100 via cumsum to get the final index level 
