from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'history-rates-data'})
row = table.find_all('a', attrs={'class' : 'w'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    #get period
    period = table.find_all('a', attrs={'class' : 'w'})[i].text
    period = period.strip()

    #get nominal USD to IDR
    kurs_usd = table.find_all('span', attrs={'class' : 'w'})[i].text
    kurs_usd = kurs_usd.strip()

    temp.append((period, kurs_usd))
    
temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('period','kurs_usd'))

#insert data wrangling here

data['period'] = data['period'].astype('datetime64[ns]')
data['kurs_usd'] = data['kurs_usd'].replace('\$1 = Rp','',regex=True).replace(',','',regex=True)
data['kurs_usd'] = data['kurs_usd'].astype('float64')

data = data.set_index('period')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["kurs_usd"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = data.plot(figsize = (10,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)