# -*- coding: utf-8 -*-
"""
cron: 53 11 * * *
new Env('吾爱破解');
"""

import requests,os,sys
import urllib.parse
from bs4 import BeautifulSoup

from notify_mtr import send
from utils import get_data


class Pojie:
    def __init__(self, check_items):
        self.check_items = check_items

    @staticmethod
    def sign(cookie):
        url1 = "https://www.52pojie.cn/CSPDREL2hvbWUucGhwP21vZD10YXNrJmRvPWRyYXcmaWQ9Mg==?wzwscspd=MC4wLjAuMA=="
        url2 = 'https://www.52pojie.cn/home.php?mod=task&do=apply&id=2&referer=%2F'
        url3 = 'https://www.52pojie.cn/home.php?mod=task&do=draw&id=2'
        cookie = urllib.parse.unquote(cookie)
        cookie_list = cookie.split(";")
        cookie = ''
        for i in cookie_list:
            key = i.split("=")[0]
            if "htVC_2132_saltkey" in key:
                cookie += "htVC_2132_saltkey=" + urllib.parse.quote(i.split("=")[1]) + "; "
            if "htVC_2132_auth" in key:
                cookie += "htVC_2132_auth=" + urllib.parse.quote(i.split("=")[1]) + ";"
            if not ('htVC_2132_saltkey' in cookie or 'htVC_2132_auth' in cookie):
                print("cookie中未包含htVC_2132_saltkey或htVC_2132_auth字段，请检查cookie")
                sys.exit()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57'
        }
        res1 = requests.get(url1, headers=headers, allow_redirects=False)
        s_cookie = res1.headers['Set-Cookie']
        cookie = cookie + s_cookie
        headers['Cookie'] = cookie
        res2 = requests.get(url2, headers=headers, allow_redirects=False)
        s_cookie = res2.headers['Set-Cookie']
        cookie = cookie + s_cookie
        headers['Cookie'] = cookie
        res3 = requests.get(url3, headers=headers)
        r_data = BeautifulSoup(res3.text, "html.parser")
        jx_data = r_data.find("div", id="messagetext").find("p").text
        if "您需要先登录才能继续本操作" in jx_data:
            print(f"Cookie 失效")
            msg = f"Cookie 失效"
        elif "恭喜" in jx_data:
            print(f"签到成功")
            msg = f"签到成功"
        elif "不是进行中的任务" in jx_data:
            print(f"今日已签到")
            msg = f"今日已签到"
        else:
            print(f"签到失败")
            msg = f"签到失败"
        return msg
    
    def main(self):
        i = 1
        msg_all = ""
        for check_item in self.check_items:
            cookie = check_item.get("cookie")
            sign_msg = self.sign(cookie=cookie)
            msg = f"账号 {i} 签到状态: {sign_msg}"
            msg_all += msg + "\n\n"
            i += 1
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("POJIE", [])
    res = Pojie(check_items=_check_items).main()
    send("吾爱破解", res)