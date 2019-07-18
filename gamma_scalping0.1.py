from requests import get
import pandas as pd
import numpy as np
import re,time
import win32api
import win32gui
import win32con

pd.set_option('display.unicode.east_asian_width', True)
np.set_printoptions(precision=4,suppress=True,formatter={'float': '{: 0.4f}'.format})
url = 'http://hq.sinajs.cn/list=CON_OP_10001902,CON_SO_10001902,sh510050'
#获取句柄
htqq=win32gui.FindWindow(None,"华泰股票期权 - [期权T型报价]")
cmd = win32gui.FindWindow("ConsoleWindowClass",None)
#设置窗口位置
win32gui.SetWindowPos(htqq,0,557,0,807,603,4)
time.sleep(0.5)
win32gui.SetWindowPos(cmd,0,0,0,550,731,4)
time.sleep(0.5)
#持仓量，持仓价
ETF50_VOLUME = 43.82
ETF50_AVG = 2.949
OP_VOLUME = 47
OP_AVG = 0.3632
#标的
class Option(object):
        def __init__(self,positionVolume,positionPrice,code=None,\
                     buy=None,b_volume=None,sell=None,s_volume=None,delta=None):               
                self.code = code
                self.buy = buy
                self.b_volume = b_volume
                self.sell = sell
                self.s_volume = s_volume
                self.delta = delta
                self.positionPrice = positionPrice
                self.positionVolume = positionVolume                
        def bid_ask(self):
                return self.sell - self.buy
        def profit(self):
                return (self.buy - self.positionPrice)*self.positionVolume*10000

def get_data(url):
	d = get(url).text
	d = re.findall(r"\"(.+)\"",d)
	d = pd.DataFrame(d)
	d = d[0].str.split(',',expand=True)
	return np.array(d)

def data_loading(d):
        #买一量，买一价，卖一量，卖一价
        opt.b_volume,opt.buy,opt.s_volume,opt.sell = d[0,[0,1,4,3]].astype(float)
        opt.delta = -float(d[1,5])
        etf50.b_volume,etf50.buy,etf50.s_volume,etf50.sell = d[2,[10,11,20,21]].astype(float)

def bounder_update():
        return etf50.positionVolume/(opt.positionVolume+1),\
               etf50.positionVolume/(opt.positionVolume-1)
        
#买入开仓B 66
#卖出平仓S 83
def htqq_buy_open():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,66,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,66,0)    
    opt.positionPrice=(opt.positionVolume*opt.positionPrice+opt.sell)/(opt.positionVolume+1)
    opt.positionVolume+=1
    log('b,'+str(opt.sell)+'\n')

def htqq_sell_close():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,83,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,83,0)    
    opt.positionPrice=(opt.positionVolume*opt.positionPrice-opt.buy)/(opt.positionVolume-1)
    opt.positionVolume-=1
    log('s,'+str(opt.buy)+'\n')
   
def log(s):
    f = open(r'C:\Users\qmin\Desktop\log.txt','a')
    f.write(s)
    f.close()

if __name__ == '__main__':
    opt = Option(positionVolume=OP_VOLUME,positionPrice=OP_AVG)
    etf50 = Option(positionVolume=ETF50_VOLUME,positionPrice=ETF50_AVG)
    lower,upper = bounder_update()
    
    while(True):
        d = get_data(url)	
        data_loading(d)
        if(opt.bid_ask()>0.002):
            print('bid ask too big!')
            time.sleep(5)
            continue
        if(opt.delta < lower):
            htqq_buy_open()
            lower,upper = bounder_update()
            time.sleep(3)          
        if(opt.delta > upper):
            htqq_sell_close()
            lower,upper = bounder_update()
            time.sleep(3)

        #浮盈
        x = etf50.profit()
        y = opt.profit()
        print('\n{:<9s}{:<9s}{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}\n'\
              '{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.0f}{:<9.0f}{:<9.0f}'\
              .format('50etf','8_3300','delta','upper','lower',\
                      etf50.sell,opt.sell,opt.delta,upper,lower,\
                      '50etf','8_3300','sum',\
                      x,y,x+y))
        
        time.sleep(1)

    
