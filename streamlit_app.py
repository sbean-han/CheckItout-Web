import streamlit as st
import json
import checkitoutAPI
import pandas as pd
import os, time

data_path='reviews.json'
get_data=True
if os.path.exists(data_path):
    file_time=os.path.getctime(data_path)
    current_time=time.time()
    one_hour=current_time-3600*60*3
    if file_time> one_hour:
        get_data=False
if get_data:
    reviews=checkitoutAPI.get_reviews()
    checkitoutAPI.reviews_tojson(reviews)
else:
    reviews=[]
    with open('reviews.json', 'r', encoding='utf-8') as f:
        json_reviews=json.load(f)
    for rev in json_reviews:
        reviews.append(checkitoutAPI.review_post(rev, 'json'))        

st.title("🎈 책키라웃 리뷰 Summary Page!")
reviews=[rv for rv in reviews if not rv.unwanted]

review_summary=[rv.summary for rv in reviews]
reviewers=[rv.reviewer for rv in reviews]

data=pd.DataFrame(review_summary)
data['reviewers']=reviewers
reviewers_data=data.groupby('reviewers').describe()['Score'][['mean','min','max','std']]
z_score=lambda z: (z['Score']-reviewers_data['mean'][z['reviewers']])/reviewers_data['std'][z['reviewers']]
data['Z_score']=data.apply(z_score, axis=1)
# data=data.set_index(['Title'])
st.scatter_chart(data,x='reviewers',y='Z_score', color='Title')
st.dataframe(data.filter(items=['Z_score','Title','Author','Stars','Score']).sort_values(by=['Z_score','Score'], ascending=False))

# st.dataframe(reviewers_data)