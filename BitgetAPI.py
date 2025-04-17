import hashlib
import hmac
import base64
import time
import json
import requests


class BitgetAPI:
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key.encode()
        self.passphrase = passphrase
        self.base_url = "https://api.bitget.com"

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(self.secret_key, message.encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def _headers(self, method, request_path, body=""):
        timestamp = str(int(time.time() * 1000))
        if method == "GET":
            message = f"{timestamp}{method}{request_path}"
        else:
            message = f"{timestamp}{method}{request_path}{body}"  # ✅ 拼上 request_path 再拼 body

        signature = hmac.new(self.secret_key, message.encode(), hashlib.sha256).digest()
        sign = base64.b64encode(signature).decode()

        print(f"[SIGN-DEBUG] timestamp        : {timestamp}")
        print(f"[SIGN-DEBUG] message          : {message}")
        print(f"[SIGN-DEBUG] signature(base64): {sign}")

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }


    def get_contract_kline(self, symbol="BTCUSDT_UMCBL", granularity=300, limit=5):
        request_path = "/api/mix/v1/market/history-candles"
        query = f"symbol={symbol}&granularity={granularity}&limit={limit}"
        full_url = f"{self.base_url}{request_path}?{query}"

        headers = self._headers("GET", request_path, f"{request_path}?{query}")

        print(f"[DEBUG] 请求URL: {full_url}")
        print(f"[DEBUG] headers: {headers}")
        resp = requests.get(full_url, headers=headers)

        print(f"[DEBUG] 状态码: {resp.status_code}")
        print(f"[DEBUG] 响应内容: {resp.text}")

        if resp.status_code == 200:
            data = resp.json()
            return [
                {
                    "timestamp": int(d[0]),
                    "open": float(d[1]),
                    "high": float(d[2]),
                    "low": float(d[3]),
                    "close": float(d[4]),
                    "volume": float(d[5])
                } for d in data["data"]
            ]
        else:
            print(f"[ERROR] 获取K线失败：{resp.status_code} - {resp.text}")
            return []

    def get_contract_kline_v2(self, symbol="BTCUSDT", granularity="5m", limit=100, product_type="usdt-futures"):
        url = f"{self.base_url}/api/v2/mix/market/candles"
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "limit": limit,
            "productType": product_type
        }
        print(f"[DEBUG] 请求URL: {url}")
        print(f"[DEBUG] 请求参数: {params}")
        response = requests.get(url, params=params)
        print(f"[DEBUG] 响应码: {response.status_code}")
        print(f"[DEBUG] 响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "timestamp": int(d[0]),
                    "open": float(d[1]),
                    "high": float(d[2]),
                    "low": float(d[3]),
                    "close": float(d[4]),
                    "volume": float(d[5])
                } for d in data["data"]
            ]
        else:
            print("❌ 获取失败")
            return []

    def get_kline_data(self, symbol="BTCUSDT_UMCBL", granularity=300, limit=100):
        request_path = "/api/mix/v1/market/history-candles"
        full_url = self.base_url + request_path

        params = {
            "symbol": symbol,
            "granularity": granularity,
            "limit": limit
        }

        query_string = f"symbol={symbol}&granularity={granularity}&limit={limit}"
        headers = self._headers("GET", request_path, "", query_string)

        print(f"[DEBUG] 请求URL: {full_url}")
        print(f"[DEBUG] 请求参数: {params}")
        print(f"[DEBUG] query_string: {query_string}")
        resp = requests.get(f"{full_url}?{query_string}", headers=headers)

        print(f"[DEBUG] 状态码: {resp.status_code}")
        print(f"[DEBUG] 响应内容: {resp.text}")

        if resp.status_code == 200:
            data = resp.json()
            return [
                {
                    "timestamp": int(d[0]),
                    "open": float(d[1]),
                    "high": float(d[2]),
                    "low": float(d[3]),
                    "close": float(d[4]),
                    "volume": float(d[5])
                } for d in data["data"]
            ]
        else:
            print(f"[ERROR] 获取K线失败：{resp.status_code} - {resp.text}")
            return []



    def place_conditional_order(self, side, qty, trigger_price, order_price, stop_loss=None, symbol="BTCUSDT_UMCBL"):
        request_path = "/api/mix/v1/plan/placePlanOrder"
        full_url = self.base_url + request_path

        body_data = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(qty),
            "side": side,
            "orderType": "limit",
            "triggerPrice": str(trigger_price),
            "executePrice": str(order_price),
            "triggerType": "mark_price",
            "timeInForceValue": "normal",
            "reduceOnly": False,
            "presetStopLossPrice": str(stop_loss) if stop_loss else None
        }

        body_data = {k: v for k, v in body_data.items() if v is not None}
        body = json.dumps(body_data)
        headers = self._headers("POST", request_path, body)

        resp = requests.post(full_url, headers=headers, data=body)
        print(f"[DEBUG] 请求URL: {full_url}")
        print(f"[DEBUG] 请求BODY: {body}")
        print(f"[DEBUG] 响应码: {resp.status_code}")
        print(f"[DEBUG] 响应内容: {resp.text}")

        try:
            return resp.json()
        except Exception:
            return {"error": "Invalid response"}

    def place_limit_order(self, side, qty, price, stop_loss=None, take_profit=None, symbol="BTCUSDT_UMCBL", pos_side=None):
        request_path = "/api/mix/v1/order/placeOrder"
        full_url = self.base_url + request_path

        body_data = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": f"{float(qty):.3f}",  # 保留3位小数
            "side": side,                 # open_long / open_short
            "posSide": pos_side,         # long / short
            "orderType": "limit",
            "price": f"{float(price):.1f}",  # 保留1位小数，避免整数格式被拒
            "timeInForceValue": "normal",
            "reduceOnly": False,
            "presetStopLossPrice": f"{float(stop_loss):.1f}" if stop_loss else None,
            "presetTakeProfitPrice": f"{float(take_profit):.1f}" if take_profit else None
        }

        body_data = {k: v for k, v in body_data.items() if v is not None}

        body = json.dumps(body_data)
        headers = self._headers("POST", request_path, body)

        resp = requests.post(full_url, headers=headers, data=body)
        print(f"[DEBUG] 限价单请求URL: {full_url}")
        print(f"[DEBUG] 请求BODY: {body}")
        print(f"[DEBUG] 响应码: {resp.status_code}")
        print(f"[DEBUG] 响应内容: {resp.text}")

        try:
            return resp.json()
        except Exception:
            return {"error": "Invalid response"}
