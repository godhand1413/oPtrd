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
htqq=win32gui.FindWindow(None,"华泰股票期权 - [期权T型报价]")
cmd = win32gui.FindWindow("ConsoleWindowClass",None)
win32gui.SetWindowPos(htqq,0,557,0,807,603,4)
time.sleep(0.5)
win32gui.SetWindowPos(cmd,0,0,0,550,731,4)
time.sleep(0.5)


etf50 = 43.82
etf50_avg = 2.949

put=47
put_avg=0.3632

def get_data(url):
	d = get(url).text
	d = re.findall(r"\"(.+)\"",d)
	d = pd.DataFrame(d)
	d = d[0].str.split(',',expand=True)
	return np.array(d)

#买入开仓B 66
#卖出平仓S 83
def htqq_buy_open():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,66,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,66,0)

def htqq_sell_close():
    win32api.PostMessage(htqq,win32con.WM_KEYDOWN,83,0)
    win32api.PostMessage(htqq,win32con.WM_KEYUP,83,0)
    
def log(s):
    f = open(r'C:\Users\qmin\Desktop\log.txt','a')
    f.write(s)
    f.close()

if __name__ == '__main__':
    lower=etf50/(put+1)
    middle=etf50/put
    upper=etf50/(put-1)
    #time.sleep(10)
    
    while(True):
        d = get_data(url)
	#买一量，买一价，卖一量，卖一价
        e = d[2,[10,11,20,21]].astype(float)
        p = d[0,[0,1,4,3]].astype(float)
        delta = -float(d[1,5])
        if(p[3]-p[1]>0.002):
            print('bid ask too big!')
            time.sleep(5)
            continue
        if(delta<lower):
            htqq_buy_open() 
            log('b,'+str(p[3])+'\n')
            put+=1
            upper=middle
            middle=lower
            lower=etf50/(put+1)
            time.sleep(3)
        if(delta>upper):
            htqq_sell_close()
            log('s,'+str(p[3])+'\n')
            put -= 1        
            lower=middle
            middle=upper
            upper=etf50/(put-1)
            time.sleep(3)
        #计算浮盈
        x = etf50*10000*(e[1]-etf50_avg)
        y = put*10000*(p[1]-put_avg)

        print('\n{:<9s}{:<9s}{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}\n'\
              '{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.0f}{:<9.0f}{:<9.0f}'\
              .format('50etf','8_3300','delta','upper','lower',\
                      e[3],p[3],delta,upper,lower,\
                      '50etf','8_3300','sum',\
                      x,y,x+y))
        time.sleep(3)

    
