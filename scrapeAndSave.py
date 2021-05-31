import requests
import bs4
from GetQou import *
from tqdm import tqdm
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
cred = credentials.Certificate('path/to/serviceAccount.json')  # for more info see : https://firebase.google.com/docs/firestore/quickstart#python
default_app=firebase_admin.initialize_app(cred)


'''
The Link of the website look like this 

 https://www.goodreads.com/quotes?page=1

'''


'''
This function requests the first page to get

all the categories and return them in 'cats'

 *To understand the code better try to print quoteCat
 and see what it contains

'''
def getCatS():
	res = requests.get('https://www.goodreads.com/quotes')
	soup = bs4.BeautifulSoup(res.text,"lxml")
	quoteCat = soup.select('.gr-hyperlink')
	cats=set()
	for c in quoteCat:
		if 'Quotes' in c.text:
			cats.add(c.get('href'))
	return cats





def getAndSaveQuotes(url,cat):
	
	#for each quote there is 100 page
	# (tqdm is to print a progress bar)
	for p in tqdm(range(1,101),desc=f'Tag:{cat}'):
		url=url+'?page='+str(p)
		res = requests.get(url)
		soup = bs4.BeautifulSoup(res.text,"lxml")
		quoteText = soup.select('.quoteText')    
		quote=''
		author=''
		# I'm looking for the quote and it's author
		for q in quoteText:
			text=(q.text).split()
			#print(text)
			
			for i,w in enumerate(text):
				if w !='―':
					quote=quote+' '+w
				else:
					author=' '.join(text[i+1:])
					
					break
			SaveInBase(author,quote,cat) #This function connects to the firestore and saves the qoute 
			#print(f'QOUTE:{quote}  AUTHOR:{author}')#save in database
			quote=''
			author=''
		

def SaveInBase(author,quote,cat):
	c=0
	db = firestore.client()
	doc_ref = db.collection(u'collections').document(cat) # I use the collection 'collections' to keep track of how many quotes I have in each cat'
	doc=doc_ref.get()										# the documents ID's is the number of the quote
	if doc.exists:
		#incress the counter by one
		c=int((doc.to_dict())['counter'])
		doc_ref.set({u'name':cat,u'counter':str(c+1)})
	else:
		doc_ref.set({u'name':cat,u'counter':'0'})

	doc_ref = db.collection(cat).document(str(c+1))           # Save the qoute in its collection
	doc_ref.set({u'quote': quote,u'author':author,u'category':cat})




if __name__ == "__main__":
	url='https://www.goodreads.com'
	cats=getCatS()  #call the function getCat
	#past to the end of the url a categorie and try to scrape it
	for c in cats:
		turl=url+c
		i=c.rfind("/")
		cat=c[i+1:]
		getAndSaveQuotes(turl,cat)