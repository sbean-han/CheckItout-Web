import streamlit as st
import json
import checkitoutAPI, aladinAPI
import pandas as pd
import os, time, datetime

review_path='reviews.json'
last_data_path='last_data.json'
error_path='error.json'
mod_time=0
errors=[]
reloadAladin=False
ONE_HOUR=3600

st.title("🎈 책키라웃 리뷰 Summary Page!")

def time_of_data(time_diff):
    # 시간 차이에 따라 적절한 형식으로 변환
    if time_diff < 1:
        time_display = "방금 전"
    elif time_diff < 60:
        minutes = int(time_diff// 60)
        time_display = f"{minutes}분 전"
    else:
        hours = int(time_diff// 3600)
        time_display = f"{hours}시간 전"
    return time_display

def checkReview():
    global mod_time
    if os.path.exists(review_path):
        file_time=os.path.getmtime(review_path)
        current_time=time.time()
        mod_time=current_time-file_time
        if mod_time> ONE_HOUR*24:
            mod_time=0
            return True
    return False

def get_reviewDict(reload):
    if reload:
        reviews=checkitoutAPI.get_reviews()
        checkitoutAPI.reviews_tojson(reviews,review_path)
    else:
        reviews=[]
        with open(review_path, 'r', encoding='utf-8') as f:
            json_reviews=json.load(f)
        for rev in json_reviews:
            reviews.append(checkitoutAPI.review_post(rev, 'json'))  
    return reviews

def reviewDF(reviews):
    reviews=[rv for rv in reviews if not rv.unwanted]
    review_summary=[rv.summary for rv in reviews]
    Review_data=pd.DataFrame(review_summary,index=[rv.post_key for rv in reviews])
    return Review_data

def getFurtherReviews():
    if os.path.exists(last_data_path):
        with open(last_data_path) as f:
            al=json.load(f)
        return pd.DataFrame(al)
    return {}

def newReviewCnt(reviews, books):
    ##index얻어가기
    need_aladin= reviews.index.difference(books.index)
    return need_aladin

def updateBooksInfo(books,reviews, need_aladin):
    global errors
    newbooks=[]
    if len(need_aladin)==0: return books
    for book in reviews.loc[need_aladin]:
        newbook, error=updateBookInfo(book)
        if error:
            errors.append(newbook.name)
        newbooks.append(newbook)
    newbooks=pd.concat([books,pd.DataFrame(newbooks)])
    newbooks.to_json(last_data_path)
    return newbooks

def updateBookInfo(book):
    book_lists, keys=aladinAPI.getBookLists(book)
    return aladinAPI.chooseOneBook(book, book_lists, keys)

st.write(time_of_data(mod_time))
reload=checkReview()
reviews=get_reviewDict(reload)
Review_data=reviewDF(reviews)
further_data=getFurtherReviews() ##last_data_path를 읽어옴.
newidx=newReviewCnt(Review_data,further_data)
Review_data=updateBooksInfo(further_data, Review_data, newidx)

reviewers_data=Review_data.groupby('reviewer').describe()['Score'][['mean','min','max','std']]
z_score=lambda z: (z['Score']-reviewers_data['mean'][z['reviewer']])/reviewers_data['std'][z['reviewer']]
Review_data['Z_score']=Review_data.apply(z_score, axis=1)
# data=data.set_index(['Title'])
st.scatter_chart(Review_data,x='reviewer',y='Z_score', color='Title')
Output=Review_data.filter(items=['Z_score', 'image','Title','Author','Stars','ISBN','Score']).sort_values(by=['Z_score','Score'], ascending=False)
st.dataframe(Output,column_config={'image': st.column_config.ImageColumn('Cover')},height=500,use_container_width=True,hide_index=True)
