#!/usr/bin/python
import re
import sys
import requests
from lxml import html
from bs4 import BeautifulSoup
from texttable import Texttable
import json
from datetime import datetime

session = requests.session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'})

# To print data list in tabular format
def printTable(data):
	t = Texttable(max_width=140)
	t.add_rows(data)
	# t.set_cols_width([20,30])
	print(t.draw())

def showHelp(message):
	print(message)
	print("\tUses: $ python track.py <client-name> <tracking-number>")
	print("\tsupported client names: directlog, ninja_van_thailand")


# directlog parcel parsing
def track_directlog(trackid):
	global session
	track_info = dict()
	track_info['stat'] = 0

	# Validating tracking number as per client
	if not re.match(r"^[\d]{10,12}$", trackid):
		print('invalid tracking nuber')
		return


	tknParser = '//input[@id="tknConsulta2"]/@value'
	try:
		response = session.get("https://www.directlog.com.br/")
		if response.status_code == 200:

			track_info['stat'] = 1
			tree = html.fromstring(response.content)

			tkn = tree.xpath(tknParser)

			if len(tkn):
				print('Token: ' + str(tkn[0]))
				data = {'tipo': '0', 
						'numtracking': trackid, 
						'tknConsulta': tkn[0] } 
	  
				# sending post request and saving response as response object 
				response = session.post(url = 'https://www.directlog.com.br/track_individual/index.asp', data = data) 
				  
				print(response.status_code)
				# print(response.text)
				if response.status_code == 200:
					if 'erro_individual.html' in str(response.content) or 'Dados informados incorretos ou inexistentes!' in str(response.content) :
						print('invalid tracking nuber')
						return
					# parsing stuff
					soup = BeautifulSoup(response.content, 'html.parser')
					tbl = soup.findAll('table', attrs = {'width':'95%'})
					trs = tbl[2].select('tr', recursive=False)

					ls, parseData = [], []

					for td in trs[1].select('td', recursive=False):
						ls.append(td.text)
					parseData.append(ls)

					for tr in trs[2].select('tr', recursive=False):
						ls, tds = [], tr.findAll('td')
						if len(tds)>=5:
							for td in tds:
								ls.append(td.text)
							parseData.append(ls)
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

# ninjavan parcel parse
def track_ninjavan(trackid):
	global session
	try:
		response = session.get("https://api.ninjavan.co/th/shipperpanel/app/tracking?&id=" + trackid)
		print(response.status_code)
		print(response.content)
		if response.status_code == 200 :
			parseData = [['time','description']]
			# print(response.content)
			data = json.loads(response.content)
			event = data['orders'][0]['events']
			for i in event:
				# print(type(i['time']))
				parseData.append([str(datetime.fromtimestamp(i['time']/1000.0)), i['description']])
			# print(parseData)
			print('\nStatus: ' + str(data['orders'][0]['status']) + '\n')
			printTable(parseData)

		elif response.status_code in [404,410] :
			print( 'invalid tracking number' )
		else:
			print( 'Unable to track' )



	except requests.exceptions.Timeout:
	    print(e)
	except requests.exceptions.TooManyRedirects:
	    print(e)
	except requests.exceptions.RequestException as e:
	    print('[Error]: Failed to establish a new connection')
	    sys.exit(1)


# Dict of input : function_name
client_dict = {
			'directlog': track_directlog,
			'ninja_van_thailand': track_ninjavan
			}
if len(sys.argv) is 3:
	if sys.argv[1] in client_dict.keys():
		client_dict[sys.argv[1]](sys.argv[2])
	else:
		showHelp('invalid argument')
else:
	showHelp("insufficient parameters")

session.close()
