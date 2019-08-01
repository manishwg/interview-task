#!/usr/bin/python

import sys
import requests
from lxml import html
from bs4 import BeautifulSoup
from texttable import Texttable
import json
from datetime import datetime

# To print data list in tabular format
def printTable(data):
	t = Texttable(max_width=140)
	t.add_rows(data)
	# t.set_cols_width([20,30])
	print(t.draw())


def track_directlog(trackid):
	global s
	track_info = dict()
	track_info['stat'] = 0

	tknParser = '//input[@id="tknConsulta2"]/@value'
	try:
		r = s.get("https://www.directlog.com.br/")
		if r.status_code == 200:

			track_info['stat'] = 1
			tree = html.fromstring(r.content)

			tkn = tree.xpath(tknParser)

			if len(tkn):
				print('Token: ' + str(tkn[0]))
				data = {'tipo': '0', 
						'numtracking': trackid, 
						'tknConsulta': tkn[0] } 
	  
				# sending post request and saving response as response object 
				r = s.post(url = 'https://www.directlog.com.br/track_individual/index.asp', data = data) 
				  

				if r.status_code == 200:

					if 'erro_individual.html' in str(r.content):
						print('invalid tracking nuber')
						return

					soup = BeautifulSoup(r.content, 'html.parser')
					tbl = soup.findAll('table', attrs = {'width':'95%'})
					trs = tbl[2].select('tr', recursive=False)

					parseData = []
					ls = []

					for td in trs[1].select('td', recursive=False):
						ls.append(td.text)
					parseData.append(ls)

					for tr in trs[2].select('tr', recursive=False):
						# print('\n\n')
						# print(type(tr))
						ls = []

						tds = tr.findAll('td')
						if len(tds)>=5:
							for td in tds:
								ls.append(td.text)
							parseData.append(ls)
					# print(parseData)
					printTable(parseData)
			else:
				print("[Error]: Unable to get token")

	except requests.exceptions.Timeout:
	    print(e)
	except requests.exceptions.TooManyRedirects:
	    print(e)
	except requests.exceptions.RequestException as e:
	    print('[Error]: Failed to establish a new connection')
	    sys.exit(1)
	return


def track_ninjavan(trackid):
	global s
	try:
		r = s.get("https://api.ninjavan.co/th/shipperpanel/app/tracking?&id=" + trackid)

		if r.status_code == 200:
			parseData = [['time','description']]
			# print(r.content)
			data = json.loads(r.content)
			event = data['orders'][0]['events']
			for i in event:
				# print(type(i['time']))
				parseData.append([str(datetime.fromtimestamp(i['time']/1000.0)), i['description']])
			# print(parseData)
			printTable(parseData)

		elif r.status_code == 404:
			print( 'invalid tracking number' ) 

	except requests.exceptions.Timeout:
	    print(e)
	except requests.exceptions.TooManyRedirects:
	    print(e)
	except requests.exceptions.RequestException as e:
	    print('[Error]: Failed to establish a new connection')
	    sys.exit(1)



s = requests.session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'})

# Dict of input : function_name
client_dict = {
			'directlog': track_directlog,
			'ninja_van_thailand': track_ninjavan
			}

if sys.argv[1] in client_dict.keys():
	client_dict[sys.argv[1]](sys.argv[2])
else:
	print('invalid argument')
s.close()