import okex.Market_api as Market
import json
import customtkinter as CT

api_key = ""
secret_key = ""
passphrase = ""
# flag = '1'  #demo trading
flag = '0'  # real trading
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)

spreads = []
def get_spreads(bars):

    result_swap = marketAPI.get_tickers('SWAP')
    #prt = json.dumps(result_swap, indent=2)
    #print(prt)
    for num, i in enumerate(result_swap['data']):
        bid = float(i['bidPx'])
        ask = float(i['askPx'])
        namae_i = i['instId']
        dif = (ask - bid)
        dif_bps = (dif / bid) * 100 * 100
        print(f"Bps : {dif_bps}, Name: {namae_i}")

        find_ = namae_i.find("USDT")
        if find_ == -1:
            continue
        if num == 200:
            break
        if dif_bps > 5:
            continue
        result = marketAPI.get_candlesticks(i['instId'], bar=f'{bars}m', limit=5)
        amt_mov = 0.0
        for i in result['data']:
            amt_mov += (float(i[2]) - float(i[3]))
        try:
            mv = round(dif / amt_mov, 4)
        except:
            mv = 0
            continue
        print(f"{mv}, num:{num}")
        spreads.append([round(mv*100,4), round(dif_bps, 4), namae_i])

    spreads.sort()
    for i in spreads:
        print(i)
#get_spreads(5)

print(f"The number of swaps is: {len(spreads)}")

#moves per second is...
class App(CT.CTk):
    WIDTH = 1000
    HEIGHT = 520

    num_buttons = 10
    text_val = [None] * num_buttons
    text_bps = [None] * num_buttons
    text_sym = [None] * num_buttons
    text_vol = [None] * num_buttons

    def __init__(self):
        super().__init__()
        self.title("CT complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        for i in range(self.num_buttons):
            self.text_val[i] = CT.StringVar()
            self.text_bps[i] = CT.StringVar()
            self.text_sym[i] = CT.StringVar()
            self.text_vol[i] = CT.StringVar()

        self.button_val = [None] * self.num_buttons
        self.button_bps = [None] * self.num_buttons
        self.button_sym = [None] * self.num_buttons
        self.button_vol = [None] * self.num_buttons

        # ============ frame 1 ============
        self.frame_1 = CT.CTkFrame(master=self, )
        self.frame_1.pack(pady=20, padx=40, fill="both", expand=True, side="left")

        self.button_info_val = CT.CTkButton(text="Spread Val", master=self.frame_1, corner_radius=0, pady=20).grid(
            row=0, column=0)
        self.button_info_bps = CT.CTkButton(text="Bps", master=self.frame_1, corner_radius=0, pady=20).grid(row=0,
                                                                                                            column=1)
        self.button_info_sym = CT.CTkButton(text="Sym", master=self.frame_1, corner_radius=0, pady=20).grid(row=0,
                                                                                                            column=2)
        self.button_info_vol = CT.CTkButton(text="Volume", master=self.frame_1, corner_radius=0, pady=20).grid(row=0,
                                                                                                               column=3)

        for i in range(self.num_buttons):
            self.button_val[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_val[i]).grid(
                row=i + 1, column=0)
            self.button_bps[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_bps[i]).grid(
                row=i + 1, column=1)
            self.button_sym[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_sym[i]).grid(
                row=i + 1, column=2)
            self.button_vol[i] = CT.CTkButton(master=self.frame_1, corner_radius=0, textvariable=self.text_vol[i]).grid(
                row=i + 1, column=3)

        # ============ frame 2 ============
        self.frame_2 = CT.CTkFrame(master=self, )
        self.frame_2.pack(pady=20, padx=40, fill="both", expand=True, side="right")

        self.text_update = CT.StringVar()
        self.text_time = CT.StringVar()
        self.button_update = CT.CTkButton(master=self.frame_2, textvariable=self.text_update, pady=20, padx=20,command=lambda: self.update()).pack()
        self.button_time = CT.CTkButton(master=self.frame_2, textvariable=self.text_update, pady=20, padx=20, ).pack()

    def update(self):
        spreads.clear()
        get_spreads(5)
        for i in range(self.num_buttons):
            self.text_val[i].set(spreads[i][0])
            self.text_bps[i].set(spreads[i][1])
            self.text_sym[i].set(spreads[i][2])
            #self.text_vol[i].set(spreads[i][3])


app = App()
app.mainloop()
