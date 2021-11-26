import pandas as pd
import ccxt
import numpy as np
from datetime import datetime
import time
import concurrent.futures
import plotly.graph_objects as go# collect the candlestick data from Binance
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
binance = ccxt.binance()
exchange = binance
exchange_markets = binance.load_markets()
filtroporvolume = 0
parescomerros = []
pairs = []
suffix = "/USDT"
start_time = time.time()
###Pega Todas as moedas###
def carregarpares():

    exchange = binance
    exchange_markets = binance.load_markets()
    filtroporvolume = 0
    parescomerros = []
    # since1 = exchange.parse8601('2017-09-01T00:00:00Z')
    pairs = []
    suffix = "/USDT"
    ###Pega Todas as moedas###
    for i in exchange_markets:
        # print(float(exchange.fetch_ticker(i)["info"]["quoteVolume"]))
        # print(float(exchange.fetch_ticker(i)["info"]["quoteVolume"]) < 200)
        # time.sleep(5)
        if filtroporvolume == 1:
            try:
                if i.endswith(suffix) == True and exchange_markets[i]["active"] == True and float(
                        exchange.fetch_ticker(i)["info"]["quoteVolume"]) < 150:
                    pairs.append(i)
            except:
                print("erro " + i)
                parescomerros.append(i)
        elif filtroporvolume == 0:
            if i.endswith(suffix) == True and exchange_markets[i]["active"] == True and i.endswith(
                    "DOWN/USDT") == False and i.endswith("UP/USDT") == False:
                pairs.append(i)
    #print(pairs)
    pairs = pd.Series(pairs)
    return pairs





def carregardadosolhcmp(timeframe, pairs):
    pair = pairs
    #print(pairs)
    try:
        ohlcv = binance.fetch_ohlcv(symbol=pair, timeframe=timeframe, limit=1000)

        # timestamp to datetime
        start_dt = datetime.fromtimestamp(ohlcv[0][0] / 1000)
        end_dt = datetime.fromtimestamp(ohlcv[-1][0] / 1000)

        # ohlcv to pandas
        df = pd.DataFrame(ohlcv, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Time'] = [datetime.fromtimestamp(float(time) / 1000) for time in df['Time']]
        df.set_index('Time', inplace=True)
        df = df.drop(['Open', "High", 'Low', 'Volume'], 1)
        df = df.rename({'Close': pair}, axis=1)
        #dfpair = pd.concat([df, dfpair], axis=1)
        #(dfpair)
        #return dfpair
        return df
    except:
        print("erro " + pair)
        parescomerros.append(pair)


#dfpair = pd.DataFrame()
#pairs = carregarpares()

def agruparohlc(carregar, timeframe, pares):
    pairs = pares
    dfpair = pd.DataFrame()
    #print(pairs)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        resultado = [executor.submit(carregar, timeframe=timeframe, pairs=pair) for index,pair in pairs.iteritems()]
        for f in concurrent.futures.as_completed(resultado):
            dfpair = pd.concat([f.result(), dfpair], axis=1)
            #print(f.result())
        return dfpair

dfpair = agruparohlc(carregardadosolhcmp, "1d", carregarpares())


#start_time = time.time()
#carregardadosolhc(timeframe="5m", pairs=carregarpares())
#print("normal--- %s seconds ---" % (time.time() - start_time))




### Num de dias para o momentum###
numdedias = 30
#dfpair = dfpair.fillna(0)
#print(dfpair)
###Rolling percentual do momentum###
dfpairmomentum = dfpair.pct_change(periods=1)
dfpairsharpe = (dfpairmomentum.rolling(15).mean()/dfpairmomentum.rolling(15).std()) *np.sqrt(15)
dfpairmomentum = dfpairsharpe
###Percentual sem momentum###
#dfpairatual = dfpair.pct_change(periods=numdedias)

#dROPA A ULTIMA LINHA PARA PEGAR O CLOSE
#dfpairmomentum = dfpairmomentum.tail(3)
### Maiores resultados por row###
dfpairmomentum = dfpairmomentum[:-1]
#dfpairmomentum = dfpairmomentum.apply(pd.Series.nsmallest, axis=1, n=10)
dfpairmomentum = dfpairmomentum.apply(pd.Series.nlargest, axis=1, n=7)

#print(dfpairmomentum)
#print(dfpairmomentum.tail(1).notna())
resultado = dfpairmomentum.tail(1).apply(lambda row: row[row.notna()], axis=1)
print(resultado)


print("futures--- %s seconds ---" % (time.time() - start_time))
exit()

