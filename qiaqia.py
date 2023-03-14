# -*- coding: utf-8 -*-
"""
new Env('洽洽食品');
"""

import requests
import json

from notify_mtr import send
from utils import get_data

requests.packages.urllib3.disable_warnings()

class qiaqia:
    def __init__(self,check_items):
        self.check_items = check_items

    @staticmethod
    def sign(auth,uid):
        headers = {
            'Host': 'vip.qiaqiafood.com',
            'content-type': 'application/json',
            'Connection': 'keep-alive',
            'Content-Length': '57',
            'Authorization':auth,
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent':f'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.33(0x18002124) NetType/4G Language/zh_CN',
            'Referer': f'https://servicewechat.com/wxc72491b6cd007333/175/page-frame.html'
            }
        url = "https://vip.qiaqiafood.com/vip/member/sign"
        body = {"channel":"","uid":uid,"tenantId":"1"}
        msg = " "
        try:
            res = requests.post(url=url, headers=headers, data=json.dumps(body)).json()
            if res['success']:
                msg = "已经连续签到{0}天".format(res['data']['continueDays'])
            elif (res['success']==False) and (res['status']=="-1") :
                msg = res['msg']
            else:
                msg = "签到信息失败 ,请检查 变量参数 是否正确!"
        except Exception as err:
            msg = str(err)
        return msg

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            Authorization = str(check_item.get("Authorization"))
            uid = str(check_item.get("uid"))
            sign_msg = self.sign(Authorization,uid)
            msg = f"{sign_msg}\n"
            msg_all += msg + "\n\n"
        return msg_all

if __name__ == "__main__":
    data= get_data()
    _check_items_list = data.get("qiaqia", [])
    res = qiaqia(check_items=_check_items_list).main()
    send("洽洽",res)