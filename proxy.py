#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import ipaddress
import sqlite3
import re
import geoip2.database

class proxy(object):
    def __init__(self):
        #need download the database geo ip  https://pypi.python.org/pypi/geoip2
        self.reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        self.mainfunction()

    def mainfunction(self):
        connection, cursor=self.initDatabase()
        print('Start scrape')

        total=0
        totalProxynova=0
        totalProxynovaSuccess=0
        totalHidemyass=0
        totalHidemyassSuccess=0
        try:
            for proxy in self.proxynova():
                totalProxynova=totalProxynova+1
                proxy=self.preInsert(proxy)
                if self.insertIntoDatabase(proxy,connection, cursor):
                    totalProxynovaSuccess=totalProxynovaSuccess+1
        except:
            pass
        try:
            for proxy in self.hidemyass():
                totalHidemyass=totalHidemyass+1
                proxy=self.preInsert(proxy)
                if self.insertIntoDatabase(proxy,connection, cursor):
                    totalHidemyassSuccess=totalHidemyassSuccess+1
        except:
            pass
        print('Total:')
        print('proxynova: '+str(totalProxynova))
        print('hidemyass: '+str(totalHidemyass))
        print('Success:')
        print('proxynova: '+str(totalProxynovaSuccess))
        print('hidemyass: '+str(totalHidemyassSuccess))


        connection.close()
        #print('Total: '+str(i)+' and new: '+str(insertNumber))

    def initDatabase(self):

        database_file = 'proxy.db'
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()
        # We create the table where the proxies will be stored
        try:
            cursor.execute('CREATE TABLE proxies (id INTEGER PRIMARY KEY '
				'AUTOINCREMENT, ip TEXT, port INTEGER, type TEXT, country TEXT, '
				'anonymity TEXT, speed TEXT, connection_time TEXT, success INTEGER, fail INTEGER)')
        # If there's already such a table, we don't have anything to do
        except sqlite3.OperationalError:
            pass
        # Otherwise, we save the changes
        else:
            connection.commit()
        return connection, cursor

    def preInsert(self,proxy):
        type=''
        try:
            proxies={
                'http':'http://'+proxy['ip']+':'+str(proxy['port']),
            }
            html=requests.get('http://163.com', proxies=proxies,timeout=3)
            if html.status_code==200:
                type='http'
        except:
            pass
        try:
            proxies={
                'https':'http://'+proxy['ip']+':'+str(proxy['port']),
            }
            html=requests.get('http://163.com', proxies=proxies,timeout=3)
            if html.status_code==200:
                type='https'
        except:
            pass
        proxy['type']=type
        response = self.reader.country(proxy['ip'])
        proxy['country'] = response.country.iso_code
        return proxy

    def insertIntoDatabase(self, proxy, connection, cursor):
        # ip, int(port), type, country, anonymity, speed, connection_time
        #proxy=[ip,port,type,'','','','']


        cursor.execute('SELECT id FROM proxies WHERE ip=? and port=?', (proxy['ip'],proxy['port']))
        if cursor.fetchone():
            return False
        cursor.execute('INSERT INTO proxies (ip, port, type, country, anonymity, speed, connection_time,success,fail) VALUES (?, ?, ?, ?, ?, ?, ?,0,0)', (proxy['ip'],proxy['port'],proxy['type'],proxy['country'],proxy['anon'],'',''))
        connection.commit()
        return True

    def hidemyass(self):
        url="http://proxylist.hidemyass.com/"
        html=requests.get(url)
        html=BeautifulSoup(html.text,'html5lib')

        trs=html.select('#listable tbody tr');

        for tr in trs:
            tds=tr.find_all('td')
            #remove style display:none
            for hidden in tds[1].find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
            reRulesHiddenClass=re.compile(r'([a-zA-Z0-9_-]+){display:\s*none}')

            #remove the style which defined display nont
            for hiddenClass in reRulesHiddenClass.findall(tds[1].style.text):
                for hidden2  in tds[1].select('.'+hiddenClass):
                    hidden2.decompose()
            #remove the style
            tds[1].style.decompose()
            ip=removeSpace(tds[1].text)



            try:
                ipaddress.ip_address(ip)
            except:
                continue

            port=removeSpace(tds[2].text)
            try:
                port=int(port)
            except:
                continue
            type=removeSpace(tds[6].text)
            anon=removeSpace(tds[7].text)
            port={'ip':ip,'port':port,'type':type,'anon':anon}
            yield port



    def proxynova(self):
        url="http://www.proxynova.com/proxy-server-list/elite-proxies/"
        html=requests.get(url)
        html=BeautifulSoup(html.text,'html5lib')
        table=html.find('table',{'id':'tbl_proxy_list'})
        # items=table.select()

        items=table.find_all('tr')
        i=0
        insertNumber=0
        for item in items:
            i=i+1
            #the first line always the tables's header
            if(i>1):
                tds=item.find_all('td',{'align':'left'})
                #only check the table tr which has 6 td
                if len(tds) < 6:
                    continue
                ip=removeSpace(tds[0].text)
                #if the ipaddress throw error, it's not the ip.
                try:
                    ipaddress.ip_address(ip)
                except:
                    continue
                port=removeSpace(tds[1].text)
                #port is the number
                try:
                    port=int(port)
                except:
                    continue
                anon=removeSpace(tds[5].text)
                proxy={ 'ip':ip,  'port':port, 'type':'','anon':anon }
                yield proxy



def removeSpace(text):
    return text.strip()
    #return text.replace("\n",'').replace("\t",'').replace(" ",'')


if __name__ == '__main__':
	proxy()