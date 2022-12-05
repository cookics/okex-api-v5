import time

import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import json

api_key = ""
secret_key = ""
passphrase = ""
# flag = '1'  #demo trading
flag = '0'  #real trading
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)

#result_spot = marketAPI.get_tickers('SPOT')
result_swap = marketAPI.get_tickers('SWAP')
#result_futures = marketAPI.get_tickers('FUTURES')
prt = json.dumps(result_swap,indent=2)
spreads = []

print(prt)
for num, i in enumerate(result_swap['data']):
    bid = float(i['bidPx'])
    ask = float(i['askPx'])
    namae_i = i['instId']
    dif = (ask-bid)
    dif_bps = (dif/bid)*100*100
    print(f"Bps : {dif_bps}, Name: {namae_i}")

    find_ = namae_i.find("USDT")
    if(find_ == -1):
        continue

    result = marketAPI.get_candlesticks(i['instId'], bar='1m', limit=5)
    amt_mov = 0.0
    for i in result['data']:
        amt_mov += (float(i[2])-float(i[3]))
    try:
        mv = round(dif/amt_mov, 4)
    except:
        mv = 0
        continue
    print(f"{mv}, num:{num}")
    spreads.append([mv, round(dif_bps,4), namae_i])

spreads.sort()
for i in spreads:
    print(i)
#print(f"The number of swaps is: {len(spreads)}")

'''

'''

#result = marketAPI.get_candlesticks('BTC-USDT-SWAP', bar='1m', limit=5)
#print(json.dumps(result, indent=2))
#print(len(result['data']))