"""
什么值得买自动签到脚本
项目地址: https://github.com/hex-ci/smzdm_script
0 8 * * * smzdm_checkin.py
const $ = new Env("什么值得买签到");
"""

import hashlib
import os
import random
import sys
import time
import re
import requests
from notify_mtr import send
from utils import get_data


class Smzdm(object):
    KEY = "apr1$AwP!wRRT$gJ/q.X24poeBInlUJC"
    DEFAULT_USER_AGENT = "smzdm_android_V10.4.26 rv:866 (HUAWEI NXT-AL10;Android8.0.0;zh)smzdmapp"

    def __init__(self, check_items):
        self.session = requests.Session()
        self.check_items = check_items

    def _set_header(self,cookie):
        request_key = f"{random.randint(10000000, 100000000) * 10000000000 + self.start_timestamp}"
        headers = {
            "user-agent": os.environ.get("SMZDM_USER_AGENT") or self.DEFAULT_USER_AGENT,
            "request_key": request_key,
            "cookie": cookie["COOKIE"],
            "content-type": "application/x-www-form-urlencoded",
            "connection": "keep-alive",
        }
        self.session.headers = headers

    def _data(self,cookie):
        self.start_timestamp = int(time.time())
        self._set_header(cookie)
        microtime = self.start_timestamp * 1000
        sk = "1"
        token = cookie["TOKEN"]
        sign_str = f"f=android&sk={sk}&time={microtime}&token={token}&v=10.2.0&weixin=1&key={self.KEY}"
        sign = self._str_to_md5(sign_str).upper()
        data = {
            "weixin": "1",
            "captcha": "",
            "f": "android",
            "v": "10.2.0",
            "sk": sk,
            "sign": sign,
            "touchstone_event": "",
            "time": microtime,
            "token": token,
        }
        return data

    def _str_to_md5(self, m: str):
        return hashlib.md5(m.encode()).hexdigest()

    def checkin(self,cookie):
        url = "https://user-api.smzdm.com/checkin"

        # if self.index > 1:
        print("延时 5 秒执行")
        time.sleep(5)

        data = self._data(cookie)
        resp = self.session.post(url, data)
        if resp.status_code == 200 and int(resp.json()["error_code"]) == 0:
            resp_data = resp.json()["data"]
            checkin_num = resp_data["daily_num"]
            gold = resp_data["cgold"]
            point = resp_data["cpoints"]
            exp = resp_data["cexperience"]
            rank = resp_data["rank"]
            cards = resp_data["cards"]

            msg = f"""⭐签到成功{checkin_num}天
            
🏅金币: {gold}
🏅积分: {point}
🏅经验: {exp}
🏅等级: {rank}
🏅补签卡: {cards}\n
                   """

            print(msg)
            return  msg
        else:
            print("登录失败", resp.json())
            msg += "登录失败\n"
            return  msg

    def all_reward(self,cookie):
        msg=''
        url = "https://user-api.smzdm.com/checkin/all_reward"
        data = self._data(cookie)
        resp = self.session.post(url, data)
        if resp.status_code == 200 and int(resp.json()["error_code"]) == 0:
            resp_data = resp.json()["data"]
            str1 = resp_data["normal_reward"]["reward_add"]["title"] + ": " + resp_data["normal_reward"]["reward_add"]["content"]
            str2 = resp_data["normal_reward"]["gift"]["title"] + ": " + resp_data["normal_reward"]["gift"]["content_str"] + "\n"
            print(str1)
            print(str2)
            msg = str1 + "\n" +str2
        return msg
            

    def extra_reward(self,cookie):
        continue_checkin_reward_show = False
        userdata_v2 = self._show_view_v2(cookie)
        try:
            for item in userdata_v2["data"]["rows"]:
                if item["cell_type"] == "18001":
                    continue_checkin_reward_show = item["cell_data"][
                        "checkin_continue"
                    ]["continue_checkin_reward_show"]
                    break
        except Exception as e:
            print(f"检查额外奖励失败: {e}\n")
            msg = "检查额外奖励失败: {e}\n"
        if not continue_checkin_reward_show:
            print("今天没有额外奖励\n")
            msg = "今天没有额外奖励\n"
            return msg 
        url = "https://user-api.smzdm.com/checkin/extra_reward"
        data = self._data(cookie)
        resp = self.session.post(url, data)
        resp_data = resp.json()["data"]
        print(resp_data["title"] + ": " + re.sub('<[^<]+?>', '', resp_data["gift"]["content"]) + "\n")

    def _show_view_v2(self,cookie):
        url = "https://user-api.smzdm.com/checkin/show_view_v2"
        data = self._data(cookie)
        resp = self.session.post(url, data)
        if resp.status_code == 200 and int(resp.json()["error_code"]) == 0:
            return resp.json()

    def _vip(self):
        url = "https://user-api.smzdm.com/vip"
        data = self._data()
        resp = self.session.post(url, data)
        print(resp.json()["data"])

    @staticmethod
    def handle(cookie):
        ck = {}
        try:
            token = re.findall(r"sess=(.*?);", cookie)[0]
            cookie = cookie.replace("iphone", "android").replace("iPhone", "Android").replace("apk_partner_name=appstore", "apk_partner_name=android")
            ck={
                "COOKIE": cookie,
                "TOKEN": token,
            }
        except:
            print("发生异常错误")
        return ck



    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            cookie = check_item.get("cookie")
            cookie = self.handle(cookie)
            # sign = Smzdm(cookie)
            sign_msg = self.checkin(cookie)
            ward_msg = self.all_reward(cookie)
            extr_msg = self.extra_reward(cookie)
            msg = f"{sign_msg}\n{ward_msg}\n{extr_msg}"
            msg_all += msg + "\n\n"
        return msg_all



if __name__ == "__main__":
    _data = get_data()
    _check_items = _data.get("SMZDM_APP", [])
    result = Smzdm(check_items=_check_items).main()
    send("什么值得买APP", result)