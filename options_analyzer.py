from bs4 import BeautifulSoup
import requests
import yfinance as yf
import pandas as pd

# analyze different unusual options activity sources to see the success rate of each source
options = dict()
optionlist = dict()
webcounter = 0
#itm, expired, pages?
def expired(br):
    enddate = pd.to_datetime(options[br][5])
    now = pd.datetime.now()         
    if now > enddate:
        return ' | Expired'
    else:
        return ''


def info(chose): 
    # contract info
    global history
    tickaa = yf.Ticker(chose)
    history = tickaa.history(start = dateminus1(options[chose][4]) , end = dateadd1(options[chose][5]))
    options[chose][2] = '$' + str(round(history['Open'].iloc[1], 2))
    options[chose][3] = '$' + str(round(history['Close'].iloc[-1], 2))
    if options[chose][0] == 'PUT':            
        for i in range(len(history.index) - 1):
            priced = int(float(options[chose][1].replace('$', '')))
            if round(history['Low'].iloc[i+1], 2) <= priced:
                options[chose][6] = 'True'
    if options[chose][0] == 'CALL':            
        for i in range(len(history.index) - 1):
            priced = int(float(options[chose][1].replace('$', '')))
            if round(history['High'].iloc[i+1], 2) >= priced:
                options[chose][6] = 'True'
    # contract history
    
    datehyphen = options[chose][5].replace('-', '')
    cost = options[chose][1].replace('$', '')
    typeoption = options[chose][0][0]
    barchart = 'https://www.barchart.com/stocks/quotes/' + chose + '%7C' + datehyphen + '%7C' + cost + typeoption + '/price-history/historical'
    print('')
    expir = str(expired(chose))
    print(str(options[chose][7]) + expir.upper())
    print('')
    print('Contract history: ')
    print(barchart)
    print('')
    
    #print all
    print('Ticker: ' + chose + ' (' + options[chose][3] + ')')
    print('Trade Type: ' + options[chose][0])
    print('Strike Price: ' + options[chose][1])
    print('Initial Price: ' + options[chose][2])
    print('Date Created: ' + options[chose][4])
    print('Expiration Date: ' + options[chose][5])
    print('Reached ITM: ' + options[chose][6])

    
    
def dateadd1(date):
    nextdaydate = pd.to_datetime(date) + pd.DateOffset(days = 1)
    nextdaystring = str(nextdaydate)
    nextday = nextdaystring[:10]
    return nextday

def dateminus1(date):
    prevdaydate = pd.to_datetime(date) - pd.DateOffset(days = 1)
    prevdaystring = str(prevdaydate)
    prevday = prevdaystring[:10]
    return prevday

while True:
    
    # unusual whales, stockwits, benzinga
    
    web = requests.get('https://www.benzinga.com/markets/options?page=' + str(webcounter)).text
    soup = BeautifulSoup(web, 'lxml')
    
    for s in soup.find_all('div', class_= 'benzinga-articles benzinga-articles-mixed'):
        #bruh = s.ul.li.div
        what = s.ul
    for b in what.find_all('li'):
        links = b.find('div')
        if links.find_all('a'):
            link = links.find('a')['href']
            if 'sees' in link:
                continue
            elif 'unusual' in link:
                pass
            else:
                continue
            x = 'https://www.benzinga.com' + link
            
            weblinks = requests.get(x).text
            webl = BeautifulSoup(weblinks, 'lxml')
            webli = webl.find('div', class_= 'article-content-body-only')
            #print link information, ticker and option data
            counter = 0
            ticker = webli.find('a', class_= 'ticker')
            actualname = webli.strong.text
            #date created
            dcdate = webl.head.find('meta', {'name' : 'DC.Date'})
                
            
            date_created = dcdate.attrs['content']

            #placeholder
            currentprice = 'bruh'
            pricecreated = 'bru'
            reachstrike = 'False'            
            
            if ticker.text in options:
                continue
            #type, price, date
            for c in webli.find_all('li'):
                counter += 1
                colon = c.text.index(':')
                count = 3
                data = c.text[colon + 2]
                while True:
                    if (colon + count) == len(c.text):
                        break                
                    data1 = c.text[colon + count]
                    count += 1
                    data = data + data1
                
                if counter == 3:
                    contract_type = data
                elif counter == 4:
                    date = data 
                elif counter == 5:
                    strikeprice = data
                else:
                    continue
            
            options[ticker.text] = [contract_type, strikeprice, pricecreated ,currentprice, date_created, date, reachstrike, actualname]
        
    # for each dictionary, find price of initial price then compare to current price
#    check if has gone up/down, reached strike price
    print('')
    print('Unusual Options Tickers: ')
    
    for dic in options:
        a = 'bruh'
        ticka = yf.Ticker(dic)
        hista = ticka.history(start = dateminus1(options[dic][4]) , end = dateadd1(options[dic][5]))
#        if options[dic][0] == 'PUT':
#            if round(hista['Close'].iloc[-1], 2) <= int(float(options[dic][1].replace('$', ''))):
#                a = 'ITM'
#            else:
#                a = 'OTM'
#        if options[dic][0] == 'CALL':
#            if round(hista['Close'].iloc[-1], 2) >= int(float(options[dic][1].replace('$', ''))):
#                a = 'ITM'
#            else:
#                a = 'OTM'
        if options[dic][0] == 'PUT':            
            for i in range(len(hista.index) - 1):
                priced = int(float(options[dic][1].replace('$', '')))
                if round(hista['Low'].iloc[i+1], 2) <= priced:
                    a = ' (ITM)'
                else:
                    a = ' (OTM)'
        if options[dic][0] == 'CALL':            
            for i in range(len(hista.index) - 1):
                priced = int(float(options[dic][1].replace('$', '')))
                if round(hista['High'].iloc[i+1], 2) >= priced:
                    a = ' (ITM)'
                else:
                    a = ' (OTM)'
        print(dic + a + expired(dic))
    
    n = 0
    webcounter += 1    
    while True:
        global someinput
        print('Which Ticker Would You Like Information On?')
        print('Leave Blank To Skip: ')
        print('Type 2 To Exit: ')
        someinput = input('')
        chose = 'None'
        if someinput.upper() == 'ALL':
            for dic in options:
                info(dic)
            continu = input('Enter Any Key to Continue: ')   
            n = 1
            break
        for dic in options:
            if someinput.upper() == dic:
                chose = dic
            else:
                pass
            
        if someinput == '':
            break
        elif someinput == '2':
            break
        
        if chose == 'None':
            print('No Information Found, Try Again')
        else:
            break
        
    if someinput == '':
        continue        
    elif someinput == '2':
        break
    
    if n == 1:
        continue
    
    info(chose) 
    print('Type 1 To Check Ticker History: ')
    print('Type 2 To Exit: ')
    print('Type Any Other Key To Continue: ')
    somethin = input('')
    
    if somethin == '1':
        print(history)
        contin = input('Enter Any Key To Continue: ')
    elif somethin == '2':
        break
    else:
        pass
    

