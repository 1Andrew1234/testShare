# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:17:23 2018

@author: Cruise Wong



""""""
使用方法：
1. 运行程序
2. 调用login函数进行微信登录，需要扫码
3. 调用main主函数程序机器人开始运行监测群消息
"""

import requests
import hmac
import pandas as pd
import time
import wxpy
bibox_key='f76379cb00896cf749ed03e37012ddaa0c37eb21'
bibox_secret='6618411ab5365792aa8021dcba3c2e663d0a14b9'
tuling = wxpy.Tuling(api_key='01e5cef894554387bd15ab6126c36900')
bot=wxpy.Bot(console_qr=True)
def login():
    global bot
    bot=wxpy.Bot(console_qr=True)

def get_assets():
    cmds = '[{"cmd":"transfer/assets","body":{"select":""}}]'
    asset = requests.post("https://api.bibox.com/v1/transfer", data={'cmds': cmds, 'apikey': bibox_key,
                'sign': hmac.new(bibox_secret.encode('utf-8'), cmds.encode('utf-8')).hexdigest()})
    ast_list = asset.json()['result'][0]['result']['assets_list']
    df_ast=pd.DataFrame(ast_list)
    df_ast[['BTCValue','CNYValue','USDValue','balance','freeze']]=df_ast[['BTCValue','CNYValue','USDValue','balance','freeze']].astype('float') # 字符转数字
    df_ast['total']=df_ast.balance.astype('float')+df_ast.freeze.astype('float') # 计算总余额
    df_ast.loc[df_ast.coin_symbol=='BTC','initial']=3 # 设置初始余额
    df_ast.loc[df_ast.coin_symbol=='ETH','initial']=36 # 设置初始余额
    df_ast.loc[df_ast.coin_symbol=='CAT','initial']=300000 # 设置初始余额
    df_ast=df_ast.dropna()
    return df_ast
def get_balance():
    df=get_assets()
    ast_str=''
    for i in range(len(df.coin_symbol)):
        ast_str=ast_str+'The balance of '+df.iloc[i,4]+' is '+str(df.iloc[i,6])+'\n'
    return ast_str
def get_change():
    df_ast=get_assets()
    df_ast['usd_price']=df_ast.USDValue/(df_ast.total)
    df_ast['initial_usd_value']=df_ast.usd_price*df_ast.initial
    total_usd=df_ast.USDValue.sum()
    initial_total_usd=df_ast.initial_usd_value.sum()
    df_ast['change']=(total_usd-initial_total_usd)/df_ast.usd_price
    ret_str='The ETH changed '+str(df_ast.loc[df_ast.coin_symbol=='ETH','change'].values[0])+'; The CAT changed '+str(df_ast.loc[df_ast.coin_symbol=='CAT','change'].values[0])
    return ret_str
def get_transactions(ticker,i):
    cmds = '[{"cmd":"orderpending/orderHistoryList","body":{"pair":"' + ticker + '", "account_type":0, "page":'+str(i)+',"size":200}}]'
    result = requests.post("https://api.bibox.com/v1/orderpending", data={'cmds': cmds, 'apikey': bibox_key, 'sign': hmac.new(bibox_secret.encode('utf-8'), cmds.encode('utf-8')).hexdigest()})
    result = result.json()
    return result


def get_volume():
    df_btc=pd.DataFrame()
    df_eth=pd.DataFrame()
    for i in range(30):
        trans_btc=get_transactions('CAT_BTC',i+1)
        trans_eth=get_transactions('CAT_ETH',i+1)
        df_btc=df_btc.append(pd.DataFrame(trans_btc['result'][0]['result']['items']))
        df_eth=df_eth.append(pd.DataFrame(trans_eth['result'][0]['result']['items']))
    amount_btc=df_btc[df_btc.createdAt/1000>time.time()-24*60*60].amount.astype('float').sum()
    amount_eth=df_eth[df_eth.createdAt/1000>time.time()-24*60*60].amount.astype('float').sum()
    ret='In the last 24 hours, we traded '+str(amount_btc)+' CAT on CAT/BTC pair and '+str(amount_eth)+' CAT on CAT/ETH pair.'
    return ret

group=bot.groups().search('BOT')[0]
@bot.register([group])
def auto_reply(msg):
    print(msg)
#        print(msg.member.name)
#        if msg.member.name=='王泽宪':
#            group.send('hi!'+msg.member.name)
#        if msg.member.name=='Manson':
#            group.send('hi!'+msg.member.name)
#        if msg.member.name=='Bigbao':
#            group.send('hi!'+msg.member.name)         

    if msg.text=='balance':
        balance=get_balance()
        return balance
    else:
        if msg.text=='change':
            return get_change()
        else:
            if msg.text=='volume':
                return get_volume()
            else:
                tuling.do_reply(msg)


wxpy.embed()