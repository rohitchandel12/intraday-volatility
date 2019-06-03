#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 22:30:28 2019

@author: kunwu
"""

import requests,json
api='xxxxxxxadd your own api key*********'
base_url='https://cloud.iexapis.com/stable'


symbol='IBM'

#1-minute data of latest date
url=base_url+'/stock/{}/intraday-prices?token={}'.format(symbol,api)

res = requests.get(url=url)
datas = json.loads(res.content.decode())

