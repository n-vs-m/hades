#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __  __  ______  ____    ____    ____
# /\ \/\ \/\  _  \/\  _`\ /\  _`\ /\  _`\
# \ \ \_\ \ \ \L\ \ \ \/\ \ \ \L\_\ \,\L\_\
#  \ \  _  \ \  __ \ \ \ \ \ \  _\L\/_\__ \
#   \ \ \ \ \ \ \/\ \ \ \_\ \ \ \L\ \/\ \L\ \
#    \ \_\ \_\ \_\ \_\ \____/\ \____/\ `\____\
#     \/_/\/_/\/_/\/_/\/___/  \/___/  \/_____/
#
# Heliocentric Ascension and Declination
# of Earth and HADES
#
# H.A.D.E.S
# v0.8 - 16 dec 2015
# Nicolas Montgermont
#
# Copyleft: This is a free work, you can copy,
# distribute, and modify it under the terms of the
# Free Art License http://artlibre.org/licence/lal/en/
#
# changelog
# v0.8 : added minor aspects : pi/4, 3pi/4, 2pi/5, 4pi/5
# v0.7 : english comments
# v0.6 : hidden password for publication
# v0.5 : add new_day check after 04AM
#        add flush to log in real time
#        update every 10 min

#################################
#### INIT
#################################

# LIB
import json
import req_admxi
import socket
import sys,pytz
import math
import ephem
import time
from datetime import datetime,date,timedelta
from yahoo_finance import Share

# CONSTANTS
HOST = 'localhost'      # The remote host
PORT = 8888             # The same port as used by the server
GOLD = Share('XAUUSD=X')
PI = math.pi
DATE_LIMITE = date(2020,12,31)

# VARIABLES
current_day = -1
next_pi = DATE_LIMITE
next_2pi3 = DATE_LIMITE
next_pi2 = DATE_LIMITE
next_pi3 = DATE_LIMITE
next_0 = DATE_LIMITE
next_par = DATE_LIMITE
next_cpar = DATE_LIMITE
next_pi4 = DATE_LIMITE
next_3pi4 = DATE_LIMITE
next_2pi5 = DATE_LIMITE
next_4pi5 = DATE_LIMITE

buy = 0
sell = 0
status_hades = '' 

# PWD
with open("/home/nico/code/pass_client.txt", "r") as keyfile:
    PASS_CLIENT = keyfile.read().strip()

#################################
#### FUNCTIONS ASTRONOMY
#################################

# Angle Between Earth and Pluto
def compute_angle(date_local):
    angle = [0,0,0]
    m = ephem.Sun()
    m.compute(ephem.Date(date_local))
    m2 = ephem.Pluto()
    m2.compute(ephem.Date(date_local))
    angle[0] = float(repr(ephem.separation((m.hlon,0),(m2.hlon,0))))
    angle[1] = abs(float(repr(ephem.separation((0,abs(m2.hlat)),(0,abs(m.a_dec))))))
    angle[2] = cmp(m2.hlat*m.a_dec,0)
    return angle
    
# Computing next event
def next_date(date_local):
    global next_pi
    global next_2pi3
    global next_pi2
    global next_pi3
    global next_0
    global next_par
    global next_cpar
    global next_pi4
    global next_3pi4
    global next_2pi5
    global next_4pi5

    global next_angle
    dates = []
    if (next_pi >= date_local) and (next_pi < DATE_LIMITE):
        dates.append((next_pi,u'\u260d' +' (Opposition)'))
    if (next_2pi3 >= date_local) and (next_2pi3 < DATE_LIMITE):
        dates.append((next_2pi3,u'\u25b3' +' (Trine)'))
    if (next_pi2 >= date_local) and (next_pi2 < DATE_LIMITE):
        dates.append((next_pi2,u'\u25a1' +' (Square)'))
    if (next_pi3 >= date_local) and (next_pi3 < DATE_LIMITE):
        dates.append((next_pi3,u'\u26b9' +' (Sextile)'))
    if (next_0 >= date_local) and (next_0 < DATE_LIMITE):
        dates.append((next_0,u'\u260c' +' (Conjonction)'))
    if (next_par >= date_local) and (next_par < DATE_LIMITE):
        dates.append((next_par,u'\u2225' +' (Parallel)'))
    if (next_cpar >= date_local) and (next_cpar < DATE_LIMITE):
        dates.append((next_cpar,u'\u2226' +' (Contraparallel)'))
    if (next_pi4 >= date_local) and (next_pi4 < DATE_LIMITE):
        dates.append((next_pi4,u'\u2220' +' (Semi square)'))
    if (next_3pi4 >= date_local) and (next_3pi4 < DATE_LIMITE):
        dates.append((next_3pi4,u'\u26bc' +' (Sesquiquadrate)'))
    if (next_2pi5 >= date_local) and (next_2pi5 < DATE_LIMITE):
        dates.append((next_2pi5,u'\u0051' +' (Quintile)'))
    if (next_4pi5 >= date_local) and (next_4pi5 < DATE_LIMITE):
        dates.append((next_4pi5,u'\u0062\u0051' +' (Biquintile)'))
    next_angle = sorted(dates)
    #print next
    #next_angle = next[0]

# computing dates of aspects
def compute_aspects(date_local):
    global next_pi
    global next_2pi3
    global next_pi2
    global next_pi3
    global next_0
    global next_par
    global next_cpar
    global next_pi4
    global next_3pi4
    global next_2pi5
    global next_4pi5

    diff_pi = 7
    diff_2pi3 = 7
    diff_pi2 = 7
    diff_pi3 = 7
    diff_0 = 7
    diff_par = 7
    diff_cpar = 7
    diff_pi4 = 7
    diff_3pi4 = 7
    diff_2pi5 = 7
    diff_4pi5 = 7
    for i in range(-1,100):
        local_angle = compute_angle(date_local+timedelta(days=i))
        
        # Ascension
        if (abs(local_angle[0]-PI) < diff_pi):          #opposiiton
            diff_pi = abs(local_angle[0]-PI)
            next_pi = date_local+timedelta(days=i)
        if (abs(local_angle[0]-2*PI/3) < diff_2pi3):    #trigone
            diff_2pi3 = abs(local_angle[0]-2*PI/3)
            next_2pi3 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-PI/2) < diff_pi2):       #square
            diff_pi2 = abs(local_angle[0]-PI/2)
            next_pi2 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-PI/3) < diff_pi3):       #sextile
            diff_pi3 = abs(local_angle[0]-PI/3)
            next_pi3 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-0)<diff_0):              #conjonction
            diff_0 = abs(local_angle[0]-0)
            next_0 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-PI/4)<diff_pi4):         #semisquare
            diff_pi4 = abs(local_angle[0]-PI/4)
            next_pi4 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-3*PI/4)<diff_3pi4):      #sesquisquare
            diff_3pi4 = abs(local_angle[0]-3*PI/4)
            next_3pi4 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-2*PI/5)<diff_2pi5):      #quintile
            diff_2pi5 = abs(local_angle[0]-2*PI/5)
            next_2pi5 = date_local+timedelta(days=i)
        if (abs(local_angle[0]-4*PI/5)<diff_4pi5):      #biquintile
            diff_4pi5 = abs(local_angle[0]-4*PI/5)
            next_4pi5 = date_local+timedelta(days=i)

        # Declination
        if (local_angle[2] >= 0):                       #parallel
            if (local_angle[1] < diff_par):
        	  diff_par = local_angle[1]
        	  next_par = date_local+timedelta(days=i)
        else:                                           #contraparallel
            if (local_angle[1] < diff_cpar):
        	  diff_cpar = local_angle[1]
        	  next_cpar = date_local+timedelta(days=i)

#################################
#### FUNCTIONS TWS
#################################
                
# date in TWS format
def get_local_date_TWS(decalage):
    delta = timedelta(days=decalage)
    zone = 'Europe/London'
    date_time = datetime.now(pytz.timezone(zone)) + delta
    day = date_time.strftime('%Y%m%d')
    return day

# print portfolio
def portfolio():
  tmp = req_admxi.get_portfolio('hades')
  print "MONEY: " + str(req_admxi.get_cash('hades')) + '$'
  if not tmp:
    print "SHARES : 0"
  else: 
    shares = tmp[0]  
    print "SHARES:   NAME |  NBR |  TYPE |  CUR"
    print "        %s |   %02d | %s |  %s" % (shares[1],int(shares[4]),shares[2],shares[3])
    
# Buy Gold
def buy_gold(qty):
  global buy 
  update_data()
  prix = GOLD.get_price()
  print prix
  # buy max
  local_qty = min(math.floor(money/(float(prix)+30)),qty)
  # pass order   
  if (local_qty > 0):   
    print "BUY: GOLD "+str(local_qty)+" shares at " + str(prix) + "$"  
    order = '{"pass_client": "'+ PASS_CLIENT +'",'
    order += '"contract": {"m_symbol": "XAUUSD","m_secType": "CMDTY","m_exchange": "SMART","m_currency": "USD"},'
    order +='"order": {"m_action": "BUY","m_totalQuantity": '+ str(local_qty)+', "m_orderType": "MKT", "m_lmtPrice":"", "m_tif": "GTD","m_goodAfterTime": "", "m_goodTillDate": "'+get_local_date_TWS(5)+' 23:59:59"}}'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(order)
    data = s.recv(1024)
    s.close()
    print 'DB response: ', repr(data)
  else:
    print "BUY: NOT enough money (" + str(money) +"$) to buy shares (" + str(shares) +"$)" 
  buy = 0         
  
# Sell Gold
def sell_gold(qty):
  global sell
  update_data()
  prix = GOLD.get_price()
  local_qty = min(qty,shares)
  # pass order
  if (local_qty > 0):
    print "SELL: GOLD "+str(local_qty)+" shares at " + str(prix) + "$"  
    order = '{"pass_client": "'+ PASS_CLIENT +'",'
    order += '"contract": {"m_symbol": "XAUUSD","m_secType": "CMDTY","m_exchange": "SMART","m_currency": "USD"},'
    order +='"order": {"m_action": "SELL","m_totalQuantity": '+ str(qty)+', "m_orderType": "MKT", "m_lmtPrice":"", "m_tif": "GTD","m_goodAfterTime": "", "m_goodTillDate": "'+get_local_date(5)+' 23:59:59"}}'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(order)
    data = s.recv(1024)
    s.close()
    print 'DB response: ', repr(data)
  else:
    print "SELL: NO shares to sell" 
  sell = 0        

def isopen():
  return 1 #getopenmarket('hades')
    
#################################
#### FUNCTIONS ALGO
#################################

def update_data():
	global money
	global shares
	money = req_admxi.get_cash('hades')
	tmp = req_admxi.get_portfolio('hades')
	if not tmp:
	  shares = 0
	else:  
	  shares = tmp[0][4]

# STATUS
def status():
    global status_hades
    status_hades = ''
    status_hades = str(datetime.now())+':\n  '
    if (date_local == next_pi):
        to_print = u'\u260d' +' (Opposition) day: buying GOLD'
    elif (date_local == next_2pi3):
        to_print = u'\u25b3' +' (Trine) day: selling GOLD'
    elif (date_local == next_pi2):
        to_print = u'\u25a1' +' (Square) day: buying GOLD'
    elif (date_local == next_pi3):
        to_print = u'\u26b9' +' (Sextile) day: selling GOLD'
    elif (date_local == next_0):
        to_print = u'\u260c' +' (Conjonction) day: selling GOLD'
    elif (date_local == next_par):
        to_print = u'\u2225' +' (Parallel) day: selling GOLD'
    elif (date_local == next_cpar):
        to_print = u'\u2226' +' (Contraparallel) day: buying GOLD'
    elif (date_local == next_pi4):
        to_print = u'\u2220' +' (Semisquare) day: buying GOLD'
    elif (date_local == next_3pi4):
        to_print = u'\u26bc' +' (Sesquiquadrate) day: buying GOLD'
    elif (date_local == next_2pi5):
        to_print = u'\u0051' +' (Quintile) day: selling GOLD'
    elif (date_local == next_4pi5):
        to_print = u'\u0062\u0051' +' (Biquintile) day: selling GOLD'
    else:
        to_print = 'NEXT: ' + next_angle[0][1] + ' the ' + str(next_angle[0][0])
    status_hades += to_print
    for i in range(0,len(next_angle)-1):
        status_hades += '\n  ..... ' + next_angle[i+1][1] + ' the ' + str(next_angle[i+1][0])
    textfile = open('/home/status/hades/status.txt', 'w')
    textfile.write(to_print.encode('utf-8'))
    textfile.close()
    
# new day
def new_day():
    global buy,sell,current_day,date_local
    current_day = date_local.day
    compute_aspects(date_local)
    next_date(date_local)
    if (date_local == next_pi):
        buy += 5
    if (date_local == next_2pi3):
        sell += 2
    if (date_local == next_pi2):
        buy += 3
    if (date_local == next_pi3):
        sell += 2 
    if (date_local == next_0):
        sell += 4
    if (date_local == next_par):
        sell += 3
    if (date_local == next_cpar):
        buy += 3
    if (date_local == next_pi4):
        buy += 1
    if (date_local == next_3pi4):
        buy += 1
    if (date_local == next_2pi5):
        sell += 1
    if (date_local == next_4pi5):
        sell += 1

#################################
#### MAIN
#################################
update_data()
while 1:
    tmp = datetime.now(pytz.timezone('Europe/London'))
    date_local = tmp.date()
    if (date_local.day != current_day) and (tmp.hour > 4):
        new_day()
    if buy > 0:
        if isopen():
            buy_gold(buy)
    if sell > 0:
        if isopen():
            sell_gold(sell)
    status()
    print status_hades.encode('utf-8')
    sys.stdout.flush()
    time.sleep(600)
    
