import time
from flask import Flask,jsonify,request
import pandas as pd
import numpy as np
import json
import math
import requests
from localsettings import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_long_df(idx_url):
	r=requests.get(idx_url)
	j=json.loads(r.text)
	headers=j['ordered_keys']
	d2={h:[] for h in headers}
	for h in headers:
		for item in j['items']:
			d2[h].append(j['items'][item][headers.index(h)])
	df=pd.DataFrame.from_dict(d2)
	return(df)

#on initialization, load every index as a dataframe, via a call to the django api's static assets

registered_caches=[
	'voyage_bar_and_donut_charts',
	'voyage_maps',
	'voyage_summary_statistics',
	'voyage_pivot_tables',
	'voyage_xyscatter',
	'voyage_export'
]

for rc in registered_caches:
	print("loading %s" %rc)
	xl="%s=load_long_df(\"" %rc + DJANGO_STATIC_URL + "customcache/%s.json\")" %rc
	exec(xl)


#voyage_export=load_long_df(DJANGO_STATIC_URL+'customcache/voyage_export.json')

#Implementing this as a limited pivot table with some weird twists at the end to replicate legacy functionality
##first series is the rows of course
##only one column, however (at least for now)
##### with the exception of binning -- we'll allow a column for that on numeric variables
##then a tuple giving you one value and a function to apply on top of it
###n.b. this would remove the embarked/disembarked split view on the pivot table (but it's fast enough to allow that to just be a toggle)
##this allows us to use it as well as:
###a groupby function
#####non-tabular if you use rmna="All"
###a normalized (percentages) table
##& to apply binning -- which I'm going to require is expressed as a simple integer of the number of bins. making that friendly is a ui question.

@app.route('/groupby/',methods=['POST'])
def groupby():
	st=time.time()
	rdata=request.json
	
	#print("------->",rdata)
	dfname=rdata['cachename'][0]
	
	#it must have a list of ids (even if it's all of the ids)
	ids=rdata['ids']
	
	#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
	columns,rows=rdata['groupby_fields']
	val,fn=rdata['value_field_tuple']
	
	removeallNA=False
	rmna=rdata.get('rmna')
	
	if rmna is not None:
		rmna=rmna[0]
	
	if rmna in ["True",True]:
		rmna=True
	elif rmna in ["all","All"]:
		rmna=False
		removeallNA=True
	
	normalize=rdata.get('normalize')
	if normalize is not None:
		normalize=normalize[0]
	if normalize not in ["columns","index"]:
		normalize=False
	
	df=eval(dfname)
	
	df2=df[df['id'].isin(ids)]
	
	bins=rdata.get('bins')
	if bins is not None:
		binvar,nbins=[bins[0],int(bins[1])]
		df2=pd.cut(df2[binvar],nbins)
	
	#print("+++++++++++++++++++")
	#print(columns)
	#print(df2.columns)
	#print(rows)
	#print("+++++++++++++++++++")

	#https://pandas.pydata.org/docs/user_guide/reshaping.html#reshaping-crosstabulations
	ct=pd.crosstab(
		df2[columns],
		df2[rows],
		values=df2[val],
		aggfunc=eval("np."+fn),
		normalize=normalize,
		dropna=rmna
	)
	
	#print(ct)
	
	if removeallNA:
		#https://stackoverflow.com/questions/26033301/make-pandas-dataframe-to-a-dict-and-dropna
		ctd={col: ct[col].dropna().to_dict() for col in ct.columns}
	else:
		ctd=ct.to_dict()
	return jsonify(ctd)

@app.route('/dataframes/',methods=['POST'])
def dataframes():
	st=time.time()
	
	rdata=request.json
	
	dfname=rdata['cachename'][0]
	df=eval(dfname)
	ids=rdata['ids']
	df2=df[df['id'].isin(ids)]
	columns=list(set(rdata['selected_fields']+['id']))
	df2=df2[[c for c in columns]]
	df3=df2.set_index('id')
	df3=df3.reindex(ids)
	j3=df3.to_dict()
	
	return jsonify(j3)