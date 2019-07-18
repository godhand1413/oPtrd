from requests import get
import pandas as pd
import numpy as np
import re,time
import win32api
import win32gui
import win32con

pd.set_option('display.unicode.east_asian_width', True)
np.set_printoptions(precision=4,suppress=True,formatter={'float': '{: 0.4f}'.format})
url = 'http://hq.sinajs.cn/list=CON_OP_10001901,CON_OP_10001902,sh510050'
#url = 'http://hq.sinajs.cn/list=CON_OP_10001880,CON_OP_10001882,sh510050'
htgp=win32gui.FindWindow(None,"网上股票交易系统5.0")
htqq=win32gui.FindWindow(None,"华泰股票期权 - [期权T型报价]")
cmd = win32gui.FindWindow("ConsoleWindowClass",None)
time.sleep(0.5)
win32gui.SetWindowPos(htgp,0,0,0,562,438,4)
time.sleep(0.5)
win32gui.SetWindowPos(htqq,0,563,0,800,603,4)
time.sleep(0.5)
win32gui.SetWindowPos(cmd,0,0,438,550,139,4)
time.sleep(0.5)
win32gui.SetForegroundWindow(htgp)

def get_data(url):
	d = get(url).text
	d = re.findall(r"\"(.+)\"",d)
	d = pd.DataFrame(d)
	d = d[0].str.split(',',expand=True)
	return np.array(d)

#open and close 50etf + put3300
def delta_zero(d,c):
	#买一量，买一价，卖一量，卖一价
        e = d[2,[10,11,20,21]].astype(float)
        p = d[1,[0,1,4,3]].astype(float)
        ask_bid = p[3]-p[1]
        if(e[2] < 10000):
            print('not enough...')
            time.sleep(5)
            return c
        if(ask_bid > 0.002):
            print('gap too big...')
            time.sleep(5)
            return c   
        if(c > 0):
            htqq_buy_open() 
            eft_buy()
            log('b,'+str(e[3])+','+str(p[3])+'\n')
            #htqq_sell_close()
            #eft_sell()
            #log('s,'+str(e[1])+','+str(p[1])+'\n')          
            c -= 1
            time.sleep(3)
        print('\n{:<17s}{:<15s}'.format('ETF','PUT'))
        print('{:<9.0f}{:<8.4f}{:<6.0f}{:<9.4f}'.format(e[2],e[3],p[2],p[3]))
        return c

#买入开仓B 66
#卖出平仓S 83
def htqq_buy_open():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,66,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,66,0)

def htqq_sell_close():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,83,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,83,0)
    
def eft_buy():
    win32api.keybd_event(66,0,0,0)
    win32api.keybd_event(66,0,win32con.KEYEVENTF_KEYUP,0)

def eft_sell():
    win32api.keybd_event(83,0,0,0)
    win32api.keybd_event(83,0,win32con.KEYEVENTF_KEYUP,0)

def log(s):
    f = open(r'C:\Users\qmin\Desktop\log.txt','a')
    f.write(s)
    f.close()

if __name__ == '__main__':
    c = 2
    while(True):
        d = get_data(url)
        c = delta_zero(d,c)
        time.sleep(0.5)

    
