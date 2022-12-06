import time

import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import json
import customtkinter as CT
"""
api_key = ""
secret_key = ""
passphrase = ""
# flag = '1'  #demo trading
flag = '0'  #real trading
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)



class spread:
    spreads = []



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


#result = marketAPI.get_candlesticks('BTC-USDT-SWAP', bar='1m', limit=5)
#print(json.dumps(result, indent=2))
#print(len(result['data']))

"""

class App(CT.CTk):
    WIDTH = 1000
    HEIGHT = 520

    num_buttons = 10
    button_val = [None] * num_buttons
    button_bps = [None] * num_buttons
    button_sym = [None] * num_buttons
    button_vol = [None] * num_buttons

    def __init__(self):
        super().__init__()
        self.title("CT complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")

        self.text_val = [CT.StringVar()] * self.num_buttons
        self.text_bps = [CT.StringVar()] * self.num_buttons
        self.text_sym = [CT.StringVar()] * self.num_buttons
        self.text_vol = [CT.StringVar()] * self.num_buttons

        # ============ frame 1 ============
        self.frame_1 = CT.CTkFrame(master=self, )
        self.frame_1.pack(pady=20, padx=40, fill="both", expand=True, side="left")

        self.button_info_val = CT.CTkButton(text="Spread Val", master=self.frame_1, corner_radius=0, pady=20).grid(row=0, column=0)
        self.button_info_bps = CT.CTkButton(text="Bps", master=self.frame_1, corner_radius=0, pady=20).grid(row=0, column=1)
        self.button_info_sym = CT.CTkButton(text="Sym", master=self.frame_1, corner_radius=0, pady=20).grid(row=0, column=2)
        self.button_info_vol = CT.CTkButton(text="Volume", master=self.frame_1, corner_radius=0, pady=20).grid(row=0, column=3)

        for i in range(self.num_buttons):
            self.button_val[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_val[i]).grid(row=i+1, column=0)
            self.button_bps[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_bps[i]).grid(row=i+1, column=1)
            self.button_sym[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_sym[i]).grid(row=i+1, column=2)
            self.button_vol[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_vol[i]).grid(row=i+1, column=3)

        # ============ frame 2 ============
        self.frame_2 = CT.CTkFrame(master=self, )
        self.frame_2.pack(pady=20, padx=40, fill="both", expand=True, side="right")

        self.text_update = CT.StringVar()
        self.text_time = CT.StringVar()
        self.button_update = CT.CTkButton(master=self.frame_2, textvariable=self.text_update, pady=20, padx=20,).pack()
        self.button_time = CT.CTkButton(master=self.frame_2, textvariable=self.text_update, pady=20, padx=20,).pack()



app = App()
app.mainloop()