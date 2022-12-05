import asyncio
import websockets
import json
import requests
import hmac
import base64
import zlib
import datetime
import time
import customtkinter
import random as rnd
import threading

from okex.consts import *


# from websocket_example import get_timestamp
def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def sort_num(n):
    if n.isdigit():
        return int(n)
    else:
        return float(n)


class OB:
    l = []
    bb = []
    bo = []
    spread = 0.0

    def check(self, bids, asks):
        # 获取bid档str
        bids_l = []
        bid_l = []
        count_bid = 1
        while count_bid <= 25:
            if count_bid > len(bids):
                break
            bids_l.append(bids[count_bid - 1])
            count_bid += 1
        for j in bids_l:
            str_bid = ':'.join(j[0: 2])
            bid_l.append(str_bid)
        # 获取ask档str
        asks_l = []
        ask_l = []
        count_ask = 1
        while count_ask <= 25:
            if count_ask > len(asks):
                break
            asks_l.append(asks[count_ask - 1])
            count_ask += 1
        for k in asks_l:
            str_ask = ':'.join(k[0: 2])
            ask_l.append(str_ask)
        # 拼接str
        num = ''
        if len(bid_l) == len(ask_l):
            for m in range(len(bid_l)):
                num += bid_l[m] + ':' + ask_l[m] + ':'
        elif len(bid_l) > len(ask_l):
            # bid档比ask档多
            for n in range(len(ask_l)):
                num += bid_l[n] + ':' + ask_l[n] + ':'
            for l in range(len(ask_l), len(bid_l)):
                num += bid_l[l] + ':'
        elif len(bid_l) < len(ask_l):
            # ask档比bid档多
            for n in range(len(bid_l)):
                num += bid_l[n] + ':' + ask_l[n] + ':'
            for l in range(len(bid_l), len(ask_l)):
                num += ask_l[l] + ':'

        new_num = num[:-1]
        int_checksum = zlib.crc32(new_num.encode())
        num = pow(2, 31) - 1
        if int_checksum > (pow(2, 31) - 1):
            fina = int_checksum - num * 2 - 2
        else:
            fina = int_checksum
        return fina

    def get_l(self):
        return self.l

    def print_book(self):
        a = []
        b = []
        for i in self.l:
            for num, j in enumerate(i['bids_p']):
                b.append(j)
                if num == 10:
                    break
            for num, j in enumerate(i['asks_p']):
                a.append(j)
                if num == 10:
                    break
        for i in range(10):
            print(f"{a[i][1]}       {b[i][1]}")

    def book_init(self, data, inst):
        for m in self.l:
            if inst == m['instrument_id']:
                self.l.remove(m)
        d = {}
        d['instrument_id'] = inst
        d['bids_p'] = data['bids']
        d['asks_p'] = data['asks']
        self.bb.append(data['bids'][0][0])
        self.bo.append(data['asks'][0][0])
        self.l.append(d)
        self.print_book()

    def book_update(self, data, inst):
        for j in self.l:
            if inst == j['instrument_id']:
                bids_p = j['bids_p']
                asks_p = j['asks_p']

                bids_u = data['bids']

                for i in bids_u:
                    bid_price = i[0]
                    for j in bids_p:
                        if bid_price == j[0]:
                            if i[1] == '0':
                                bids_p.remove(j)
                                break
                            else:
                                del j[1]
                                j.insert(1, i[1])
                                break
                    else:
                        if i[1] != "0":
                            bids_p.append(i)
                else:
                    bids_p.sort(key=lambda price: sort_num(price[0]), reverse=True)
                    # print('合并后的bids为：' + str(bids_p) + '，档数为：' + str(len(bids_p)))

                asks_u = data['asks']
                for i in asks_u:
                    ask_price = i[0]
                    for j in asks_p:
                        if ask_price == j[0]:
                            if i[1] == '0':
                                asks_p.remove(j)
                                break
                            else:
                                del j[1]
                                j.insert(1, i[1])
                                break
                    else:
                        if i[1] != "0":
                            asks_p.append(i)
                else:
                    asks_p.sort(key=lambda price: sort_num(price[0]))
                    # print('合并后的asks为：' + str(asks_p) + '，档数为：' + str(len(asks_p)))j

                if self.bb[-1][1] != bids_p[0][0]:
                    self.bb.append([get_timestamp(), bids_p[0][0]])
                    print(self.bb)
                if self.bo[-1][1] != asks_p[0][0]:
                    self.bo.append([get_timestamp(), asks_p[0][0]])
                    print(self.bo)


    async def subscribe_ob(self, instrument):
        while True:
            try:
                async with websockets.connect(WS_URL_PUBLIC_DEMO) as ws:
                    channels = [{"channel": "books", "instId": instrument}]
                    sub_param = {"op": "subscribe", "args": channels}
                    sub_str = json.dumps(sub_param)
                    await ws.send(sub_str)
                    print(f"send: {sub_str}")

                    while True:
                        try:
                            res = await asyncio.wait_for(ws.recv(), timeout=25)
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                            try:
                                await ws.send('ping')
                                res = await ws.recv()
                                print(res)
                                continue
                            except Exception as e:
                                print("连接关闭，正在重连……")
                                break

                        # print(get_timestamp() + res)

                        res = eval(res)  # Don't know why
                        if 'event' in res:  # Don't know why
                            continue

                        if res['action'] == 'snapshot':
                            self.book_init(res['data'][0], res['arg']['instId'])

                        elif res['action'] == 'update':
                            self.book_update(res['data'][0], res['arg']['instId'])

                        threading.Thread(target=app_b.print_l, args=self.l).start()


            except Exception as e:
                print("连接断开，正在重连……")
                continue


class App(customtkinter.CTk):
    WIDTH = 1050
    HEIGHT = 920
    num_buttons = 10
    xf_a = [None] * num_buttons
    xf_b = [None] * num_buttons
    xf_a_p = [None] * num_buttons
    xf_b_p = [None] * num_buttons
    spread_var = 0.0

    button_bid_price = [None] * num_buttons
    button_ask_price = [None] * num_buttons
    button_bid = [None] * num_buttons
    button_ask = [None] * num_buttons

    def __init__(self):

        super().__init__()

        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.protocol("WM_DELETE_WINDOW", self.on_closiing)

        # ============ create ============

        self.frame_1 = customtkinter.CTkFrame(master=self, )
        self.frame_1.pack(pady=20, padx=60, fill="both", expand=True, side="left")
        self.frame_2 = customtkinter.CTkFrame(master=self, )
        self.frame_2.pack(pady=20, padx=60, fill="both", expand=True, side="right")

        self.button_2 = customtkinter.CTkButton(text="run Book", master=self.frame_2,
                                                command=lambda: threading.Thread(target=run_book).start(),
                                                corner_radius=0, pady=20)
        self.button_2.grid(column=1, row=2)

        self.button_3 = customtkinter.CTkButton(master=self.frame_2, text="Print L",
                                                command=lambda: threading.Thread(target=self.print_l, args=(
                                                    btc_book.l, btc_book.bb, btc_book.bo)).start(),
                                                corner_radius=0, pady=20)
        self.button_3.grid(column=1, row=1)

        self.spread_var = customtkinter.StringVar()
        self.spread = customtkinter.CTkButton(master=self.frame_2, textvariable=self.spread_var).grid(column=1, row=3)

        cnt = 1
        for i in range(self.num_buttons - 1, -1, -1):
            self.xf_a[i] = customtkinter.StringVar()
            # self.xf_a[i].set(f"Box ask {i}")
            self.button_ask[i] = customtkinter.CTkButton(master=self.frame_1, command=self.button_callback,
                                                         corner_radius=0,
                                                         textvariable=self.xf_a[i], bg_color="red", fg_color="red")
            self.button_ask[i].grid(column=1, row=cnt)
            cnt += 1
        cnt = 1
        for i in range(self.num_buttons - 1, -1, -1):
            self.xf_a_p[i] = customtkinter.StringVar()
            self.xf_a[i].set(f"Box ask {i}")
            self.button_ask_price[i] = customtkinter.CTkButton(master=self.frame_1, command=self.button_callback,
                                                               corner_radius=0,
                                                               textvariable=self.xf_a_p[i], bg_color="red",
                                                               fg_color="white", text_color="black")
            self.button_ask_price[i].grid(column=2, row=cnt)  # , row = 2)
            cnt += 1
        cnt += 1
        nc = cnt
        for i in range(self.num_buttons):
            self.xf_b_p[i] = customtkinter.StringVar()
            self.xf_b_p[i].set(f"Box bid {i}")
            self.button_bid_price[i] = customtkinter.CTkButton(master=self.frame_1, command=self.button_callback,
                                                               corner_radius=0,
                                                               textvariable=self.xf_b_p[i], fg_color="white",
                                                               text_color="black")
            self.button_bid_price[i].grid(column=2, row=cnt)
            cnt += 1

        for i in range(self.num_buttons):
            self.xf_b[i] = customtkinter.StringVar()
            self.xf_b[i].set(f"Box bid {i}")
            self.button_bid[i] = customtkinter.CTkButton(master=self.frame_1, command=self.button_callback,
                                                         corner_radius=0,
                                                         textvariable=self.xf_b[i])
            self.button_bid[i].grid(column=3, row=nc)
            nc += 1

    def button_callback(self):
        print("press")
        for i in range(self.num_buttons):
            r = rnd.random()
            self.xf[i].set(round(r, 6))

    def print_l(self, l):
        for num, j in enumerate(l['bids_p']):
            self.xf_b[num].set(str(j[1]))
            self.xf_b_p[num].set(str(j[0]))
            if num == self.num_buttons - 1:
                break
        for num, j in enumerate(l['asks_p']):
            self.xf_a[num].set(str(j[1]))
            self.xf_a_p[num].set(str(j[0]))
            if num == self.num_buttons - 1:
                break

        bo = float(btc_book.bo[-1][1])
        bb = float(btc_book.bb[-1][1])
        spread = bo - bb
        dif = (bo - bb) / bb
        dif_bps = dif * 100 * 100

        self.spread_var.set(str(round(dif_bps, 4)))


def run_book():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(btc_book.subscribe_ob("BTC-USDT-SWAP"))
    loop.close()


def set_label_t(app):
    app.button_callback()


btc_book = OB()

loop = asyncio.get_event_loop()
app_b = App()

app_b.mainloop()
