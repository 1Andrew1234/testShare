# -*-coding:utf-8 -*-
import requests
import hmac
import pandas as pd
import time
import wxpy
from wxpy import *
bot = Bot(console_qr=True)
bibox_key='f76379cb00896cf749ed03e37012ddaa0c37eb21'
bibox_secret='6618411ab5365792aa8021dcba3c2e663d0a14b9'
# tuling = wxpy.Tuling(api_key='01e5cef894554387bd15ab6126c36900')

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

def load_custorms(custorm_file):
    """
    from file load custorms by remark_name(can be set unique)
    :param custorm_file:
    :return:
    """
    user_names = {}
    with open(custorm_file) as data:
        for line in data:
            line_spt = line.strip('\n').split(' ')
            remark_name = line_spt[0]
            username = line_spt[1]
            user_names[remark_name] = username
            print remark_name,username
    data.close()
    return user_names

def get_friends(user_names):
    friends = {}
    for (remark_name,username) in user_names.items():
        firend = bot.friends().search(remark_name)
        if len(firend) <=0:
            print remark_name+' not exist friend'
            # do something
        else:
            print firend[0], firend[0].remark_name, ' got friend', type(firend[0].remark_name)
            friends[firend[0].remark_name.encode('utf-8')] = firend[0]
    return friends

custorm_file = 'custorms.txt'
user_names = load_custorms(custorm_file)
friends = get_friends(user_names)
for k, v in friends.items():
    print k.decode('utf-8'), v, [k]

'''
@bot.register()
def print_messages(msg):
    print '**** receive message ****'
    print msg
    member = msg.member
    if member is not None:
        print '===qun xiaoxi'
        # print msg.is_at, member, member.display_name, member.name
        # at and do sth
        if not msg.is_at:
            return

        for rmk_name, friend in friends.items():
            # print rmk_name, friend, member==friend
            if member == friend:
                print 'at and friend:', member.name
                friend.send("hello "+str(member.name))
    msg_sender_remark_name = msg.sender.remark_name

    receive_text = msg.text.encode('utf-8')
    # print receive_text, type(receive_text), [receive_text], receive_text == '1'
    print 'receive message:' + str(receive_text)
    # print msg.sender.remark_name
    reply_msg = ''
    print [msg_sender_remark_name],[msg_sender_remark_name.encode('utf-8')]
    if friends.has_key(msg_sender_remark_name.encode('utf-8')):
        print '**** message sender ****'
        print msg_sender_remark_name+' is customer'
        if receive_text == '1':
            print "command 1"
            # call some function
            # my_balance = get_balance()
            # send_msg = 'welcome customer:'+msg_sender_remark_name+'\n'
            # print my_balance
            friends[msg_sender_remark_name].send("command 1")
        elif receive_text == '2':
            print "command 2"
            # call some function
            # my_change = get_change()
            # send_msg = 'welcome customer:' + msg_sender_remark_name + '\n'
            # print my_change
            friends[msg_sender_remark_name].send("command 2")

        elif receive_text == '3':
            print "command 3"
            # my_volume = get_volume()
            # print my_volume
            friends[msg_sender_remark_name].send("command 3")

        else:
            friends[msg_sender_remark_name].send('command error, 1->balance, 2->change, 3-volume \n')
    else:
        # not customer
        print msg_sender_remark_name + ' is not customer'
'''
group=bot.groups().search('bot-test')[0]
print group

@bot.register([group])
def auto_reply(msg):
    print(msg)
    remark_name = msg.member.name
    # print(friends.has_key(remark_name))
    #        if msg.member.name=='王泽宪':
    #            group.send('hi!'+msg.member.name)
    if not friends.has_key(remark_name):
        # custormer not in our list, not reply
        return

    user_name_custormer = user_names.get(remark_name, 'not register')
    # print(user_name_custormer)

    if msg.text == '1':
        print "command 1"
        group.send("command 1 , user_id:"+user_name_custormer)
        # balance = get_balance()
        # return balance
    elif msg.text == '2':
        print "command 2"
        group.send("command 2 , user_id:"+user_name_custormer)
    elif msg.text == '3':
        print "command 3"
        group.send("command 3 , user_id:"+user_name_custormer)
    else:
        group.send('command error, 1->balance, 2->change, 3-volume')

embed()

