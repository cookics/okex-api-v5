import asyncio
import websockets
import json
import requests
import hmac
import base64
import zlib
import datetime
import tkinter
import customtkinter
import random as rnd
import threading
import time
from okex.consts import *
from api_key import API_KEY_DEMO as API_KEY, PASSPHRASE_DEMO as PASSPHRASE, SECRET_KEY_DEMO as SECRET_KEY


def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def get_local_timestamp():
    return int(time.time())


def sort_num(n):
    if n.isdigit():
        return int(n)
    else:
        return float(n)


def get_server_time():
    url = "https://www.okx.com/api/v5/public/time"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data'][0]['ts']
    else:
        return ""


def login_params(timestamp, api_key, passphrase, secret_key):
    message = timestamp + 'GET' + '/users/self/verify'

    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    sign = base64.b64encode(d)

    login_param = {"op": "login", "args": [{"apiKey": api_key,
                                            "passphrase": passphrase,
                                            "timestamp": timestamp,
                                            "sign": sign.decode("utf-8")}]}
    login_str = json.dumps(login_param)
    return login_str


def change(num_old):
    num = pow(2, 31) - 1
    if num_old > num:
        out = num_old - num * 2 - 2
    else:
        out = num_old
    return out


class WS:

    def partial(self, res):
        bids = res['data'][0]['bids']
        asks = res['data'][0]['asks']
        instrument_id = res['arg']['instId']
        # print('全量数据bids为：' + str(bids))
        # print('档数为：' + str(len(bids)))
        # print('全量数据asks为：' + str(asks))
        # print('档数为：' + str(len(asks)))
        return bids, asks, instrument_id

    def update_bids(self, res, bids_p):
        # 获取增量bids数据
        bids_u = res['data'][0]['bids']
        # print('增量数据bids为：' + str(bids_u))
        # print('档数为：' + str(len(bids_u)))
        # bids合并
        print(f"Binds_p: {bids_p}")
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
            # print('bids：' + str(bids_p) + '，档数为：' + str(len(bids_p)))
        return bids_p

    def update_asks(self, res, asks_p):
        # 获取增量asks数据
        asks_u = res['data'][0]['asks']
        # print('增量数据asks为：' + str(asks_u))
        # print('档数为：' + str(len(asks_u)))
        # asks合并
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
            # print('合并后的asks为：' + str(asks_p) + '，档数为：' + str(len(asks_p)))
        return asks_p

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
        fina = change(int_checksum)
        return fina

    # subscribe channels un_need login
    async def subscribe_without_login(self, url, channels):
        l = []
        while True:
            try:
                async with websockets.connect(url) as ws:
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

                        print(get_timestamp() + res)
                        res = eval(res)
                        if 'event' in res:
                            continue
                        for i in res['arg']:
                            if 'books' in res['arg'][i] and 'books5' not in res['arg'][i]:
                                if res['action'] == 'snapshot':
                                    for m in l:
                                        if res['arg']['instId'] == m['instrument_id']:
                                            l.remove(m)
                                    bids_p, asks_p, instrument_id = self.partial(res)

                                    d = {}
                                    d['instrument_id'] = instrument_id
                                    d['bids_p'] = bids_p
                                    d['asks_p'] = asks_p
                                    l.append(d)
                                    checksum = res['data'][0]['checksum']
                                    # print('推送数据的checksum为：' + str(checksum))
                                    check_num = self.check(bids_p, asks_p)
                                    # print('校验后的checksum为：' + str(check_num))
                                    if check_num == checksum:
                                        print("校验结果为：True")
                                    else:
                                        print("校验结果为：False，正在重新订阅……")

                                        # 取消订阅
                                        await self.unsubscribe_without_login(url, channels)
                                        # 发送订阅
                                        async with websockets.connect(url) as ws:
                                            sub_param = {"op": "subscribe", "args": channels}
                                            sub_str = json.dumps(sub_param)
                                            await ws.send(sub_str)
                                            print(f"send: {sub_str}")

                                elif res['action'] == 'update':
                                    for j in l:
                                        print(f"J: {j}")
                                        if res['arg']['instId'] == j['instrument_id']:
                                            bids_p = j['bids_p']
                                            asks_p = j['asks_p']
                                            bids_p = self.update_bids(res, bids_p)
                                            asks_p = self.update_asks(res, asks_p)

                                            # checksum
                                            checksum = res['data'][0]['checksum']
                                            # print('checksum：' + str(checksum))
                                            check_num = self.check(bids_p, asks_p)
                                            # print('checksum：' + str(check_num))
                                            if check_num == checksum:
                                                print("True")
                                            else:
                                                print("校验结果为：False，正在重新订阅……")

                                                # 取消订阅
                                                await self.unsubscribe_without_login(url, channels)
                                                # 发送订阅
                                                async with websockets.connect(url) as ws:
                                                    sub_param = {"op": "subscribe", "args": channels}
                                                    sub_str = json.dumps(sub_param)
                                                    await ws.send(sub_str)
                                                    print(f"send: {sub_str}")
            except Exception as e:
                print("连接断开，正在重连……")
                continue

    # subscribe channels need login
    async def subscribe(self, url, api_key, passphrase, secret_key, channels):
        while True:
            try:
                async with websockets.connect(url) as ws:
                    # login
                    timestamp = str(get_local_timestamp())
                    login_str = login_params(timestamp, api_key, passphrase, secret_key)
                    await ws.send(login_str)
                    # print(f"send: {login_str}")
                    res = await ws.recv()
                    print(res)

                    # subscribe
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

                        print(get_timestamp() + res)

            except Exception as e:
                print("连接断开，正在重连……")
                continue

    # trade
    async def trade(self, url, api_key, passphrase, secret_key, trade_param):
        while True:
            try:
                async with websockets.connect(url) as ws:
                    # login
                    timestamp = str(get_local_timestamp())
                    login_str = login_params(timestamp, api_key, passphrase, secret_key)
                    await ws.send(login_str)
                    # print(f"send: {login_str}")
                    res = await ws.recv()
                    print(res)

                    # trade
                    sub_str = json.dumps(trade_param)
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

                        print(get_timestamp() + res)

            except Exception as e:
                print("连接断开，正在重连……")
                continue

    # unsubscribe channels
    async def unsubscribe(self, url, api_key, passphrase, secret_key, channels):
        async with websockets.connect(url) as ws:
            # login
            timestamp = str(get_local_timestamp())
            login_str = login_params(timestamp, api_key, passphrase, secret_key)
            await ws.send(login_str)
            # print(f"send: {login_str}")

            res = await ws.recv()
            print(f"recv: {res}")

            # unsubscribe
            sub_param = {"op": "unsubscribe", "args": channels}
            sub_str = json.dumps(sub_param)
            await ws.send(sub_str)
            print(f"send: {sub_str}")

            res = await ws.recv()
            print(f"recv: {res}")

    # unsubscribe channels
    async def unsubscribe_without_login(self, url, channels):
        async with websockets.connect(url) as ws:
            # unsubscribe
            sub_param = {"op": "unsubscribe", "args": channels}
            sub_str = json.dumps(sub_param)
            await ws.send(sub_str)
            print(f"send: {sub_str}")

            res = await ws.recv()
            print(f"recv: {res}")


"""
Public
"""

instId = BTC_SWAP
instType = SWAP

channels = [{"channel": "instruments", "instType": instType}]
channels = [{"channel": "tickers", "instId": instId}]
channels = [{"channel": "open-interest", "instId": instId}]
channels = [{"channel": "candle1m", "instId": instId}]
channels = [{"channel": "trades", "instId": instId}]
channels = [{"channel": "estimated-price", "instType": instType, "uly": "BTC-USD"}]
channels = [{"channel": "mark-price", "instId": instId}]
channels = [{"channel": "mark-price-candle1D", "instId": instId}]
channels = [{"channel": "price-limit", "instId": instId}]
channels = [{"channel": "books", "instId": instId}]
channels = [{"channel": "opt-summary", "uly": "BTC-USD"}]
channels = [{"channel": "funding-rate", "instId": instId}]
channels = [{"channel": "index-candle1m", "instId": instId}]
channels = [{"channel": "index-tickers", "instId": instId}]
channels = [{"channel": "status"}]

"""
Private
"""

channels = [{"channel": "account", "ccy": "BTC"}]
channels = [{"channel": "positions", "instType": instType, "uly": "BTC-USDT", "instId": instId}]
channels = [{"channel": "orders", "instType": instType, "uly": "BTC-USD", "instId": instId}]
channels = [{"channel": "orders-algo", "instType": instType, "uly": "BTC-USD", "instId": instId}]

'''
Trade
'''

trade_param_mkt = {
    "id": "1512",
    "op": "order",
    "args": [
        {
            "side": "buy",
            "instId": "BTC-USDT",
            "tdMode": "isolated",
            "ordType": "market",
            "sz": "100"
        }
    ]
}
trade_param_limit = {
    "id": "1512",
    "op": "order",
    "args": [
        {"side": "buy",
         "instId": "BTC-USDT",
         "tdMode": "isolated",
         "ordType": "limit",
         "px": "19777",
         "sz": "1"
         }
    ]
}
trade_param_batch = {
    "id": "1512",
    "op": "batch-orders",
    "args": [
        {"side": "buy", "instId": "BTC-USDT", "tdMode": "isolated", "ordType": "limit", "px": "19666", "sz": "1"},
        {"side": "buy", "instId": "BTC-USDT", "tdMode": "isolated", "ordType": "limit", "px": "19633", "sz": "1"}
    ]
}
trade_param_cancel = {
    "id": "1512",
    "op": "cancel-order",
    "args": [
        {"instId": "BTC-USDT", "ordId": "259424589042823169"}
    ]
}
trade_param_batch_cancel = {
    "id": "1512",
    "op": "batch-cancel-orders",
    "args": [
        {"instId": "BTC-USDT", "ordId": "259432098826694656"},
        {"instId": "BTC-USDT", "ordId": "259432098826694658"}
    ]
}
trade_param_amend = {
    "id": "1512",
    "op": "amend-order",
    "args": [
        {"instId": "BTC-USDT", "ordId": "259432767558135808", "newSz": "2"}
    ]
}
trade_param_batch_amend = {
    "id": "1512",
    "op": "batch-amend-orders",
    "args": [
        {"instId": "BTC-USDT", "ordId": "259435442492289024", "newSz": "2"},
        {"instId": "BTC-USDT", "ordId": "259435442496483328", "newSz": "3"}
    ]}

book_ws = WS()


# loop = asyncio.get_event_loop()
# loop.run_until_complete(book_ws.subscribe_without_login(url, channels))
# loop.run_until_complete(subscribe(url, api_key, passphrase, secret_key, channels))
# loop.run_until_complete(trade(url, api_key, passphrase, secret_key, trade_param))
# loop.close()

class App(customtkinter.CTk):
    WIDTH = 780
    HEIGHT = 520

    xf = [None] * 7
    button = [None] * 7

    def __init__(self):

        super().__init__()

        for i in range(7):
            self.xf[i] = customtkinter.StringVar()
            r = rnd.random()
            self.xf[i].set(round(r, 6))
        for i in range(7):
            print(self.xf[i])

        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.protocol("WM_DELETE_WINDOW", self.on_closiing)

        # ============ create ============

        self.frame_1 = customtkinter.CTkFrame(master=self, )
        self.frame_1.pack(pady=20, padx=60, fill="both", expand=True)

        self.frame_2 = customtkinter.CTkFrame(master=self, )
        self.frame_2.pack(pady=20, padx=60, fill="both", expand=True)

        self.button_2 = customtkinter.CTkButton(master=self.frame_2,
                                                command=threading.Thread(target=self.tread_t()).start(),
                                                corner_radius=0)
        self.button_2.pack()

        self.label_1 = customtkinter.CTkLabel(master=self.frame_1, justify=tkinter.LEFT)
        self.label_1.pack()

        for i in range(7):
            self.button[i] = customtkinter.CTkButton(master=self.frame_1, command=self.button_callback, corner_radius=0,
                                                     textvariable=self.xf[i])
            self.button[i].pack()

    def button_callback(self):
        print("pressDwa")
        for i in range(7):
            r = rnd.random()
            self.xf[i].set(round(r, 6))

    def tread_t(self):
        print("sleep 1")
        time.sleep(3)
        print("sleep 3")

    def web_connect(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(book_ws.subscribe_without_login(url, channels))


class TKtest(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.frame_2 = customtkinter.CTkFrame(master=self, )
        self.frame_2.pack(pady=20, padx=60, fill="both", expand=True)
        self.button_1 = customtkinter.CTkButton(master=self.frame_2,
                                                command=threading.Thread(target=self.tread_t()).start(),
                                                corner_radius=0)
        self.button_1.pack()
        self.button_2 = customtkinter.CTkButton(master=self.frame_2,
                                                command=threading.Thread(target=self.tread_t()).start(),
                                                corner_radius=0)
        self.button_2.pack()

    def tread_t(self):
        print("sleep 1")
        time.sleep(3)
        print("sleep 3")


url = WS_URL_PUBLIC_DEMO
app = TKtest()
app.mainloop()
