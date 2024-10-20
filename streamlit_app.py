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
    one_hour=current_time-3600
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

# def reviews_json(pre_rv):
#     reviews=[]
#     for it in pre_rv:
#         if it['content'].startswith('#인증'):
#             from checkitoutAPI import review_post
#             reviews.append(review_post(it))
#     review_summary=[rv.summary for rv in reviews]
#     data=pd.DataFrame(review_summary)
#     return reviews        

# reviews=reviews_json(json_reviews)
st.title("🎈 책키라웃 리뷰 Summary Page!")
review_summary=[rv.summary for rv in reviews]
data=pd.DataFrame(review_summary)
st.dataframe(data)
print('running')