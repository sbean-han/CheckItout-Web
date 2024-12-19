import streamlit as st
import json
import checkitoutAPI, aladinAPI
import pandas as pd
import os, time 
from datetime import datetime, timedelta
from configparser import ConfigParser
st.set_page_config(layout="wide")

review_path='reviews.json'
last_data_path='last_data.json'
error_path='errors.json'

errors=[]
reloadAladin=False
show_z_plot=True
ideatext=None
attending=[]

ONE_HOUR=3600

st.title("🎈 책키라웃 Summary")

    
def update_config(change=['reviews','attending']):
    if not('reviews' in change or 'attedning' in change):
        change=['reviews','attending']
    config=ConfigParser()
    if 'reviews' in change:
        config['reviews']={}
        config['reviews']['pull_at']= str(time.time())
    if 'attending' in change:
        config['attending']={}
        config['attending']['names']=attending
    with open ('conf.ini','w') as f:
        config.write(f)

def update_reviews():
    reviews=checkitoutAPI.get_reviews()
    checkitoutAPI.reviews_tojson(reviews,review_path)
    update_config()

def time_of_data(time_diff):
    # 시간 차이에 따라 적절한 형식으로 변환
    if time_diff < 1:
        time_display = "방금 전"
    elif time_diff < 60:
        minutes = int(time_diff// 60)
        time_display = f"{minutes}분 전"
    elif time_diff<60*60*24:
        hours = int(time_diff// 3600)
        time_display = f"{hours}시간 전"
    else:
        days = int(time_diff// 3600*24)
        time_display = f"{days}일 전"
    return time_display

def checkConfig():
    global review_time, mod_time, attending
    config = ConfigParser()
    config.read('conf.ini')
    review_time=float(config['reviews']['pull_at'])
    attending=config['attending']['names']
    mod_time=getmodTime(review_time)

def getmodTime(startTime):
    current_time=time.time()
    return current_time-startTime

def check_review_load_time():
    global mod_time
    mod_time=getmodTime(review_time)
    if mod_time> ONE_HOUR*24*7:
        mod_time=0
        return True
    return False

def get_reviewDict(reload):
    if reload:
        reviews=checkitoutAPI.get_reviews()
        checkitoutAPI.reviews_tojson(reviews,review_path)
        update_config()
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
    review_contents=[rv.pre_contents for rv in reviews]
    Review_data=pd.DataFrame(review_summary,index=[rv.post_key for rv in reviews])
    
    return Review_data,pd.Series(data=review_contents,index=[rv.post_key for rv in reviews])

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
    for idx, book in reviews.loc[need_aladin].iterrows():
        newbook, error=updateBookInfo(book)
        if error:
            errors.append(newbook.name)
        newbooks.append(newbook)
    newbooks=pd.concat([books,pd.DataFrame(newbooks)])
    newbooks.to_json(last_data_path)
    errorlog(errors)
    return newbooks

def errorlog(errors):
    with open ('errors.json', 'w') as f:
        f.write(str(errors))

def updateBookInfo(book):
    book_lists, keys=aladinAPI.getBookLists(book)
    return aladinAPI.chooseOneBook(book, book_lists, keys)

def update_groupby_score(Review_data, by='reviewer',plot=True,type=None):
    reviewers_data=Review_data.groupby(by)
    if type is None:
        reviewers_data=reviewers_data.describe()['Score'][['mean','min','max','std']]
        z_score=lambda z: (z['Score']-reviewers_data['mean'][z[by]])/reviewers_data['std'][z[by]]
        Review_data['Z_score']=Review_data.apply(z_score, axis=1)
        if plot:
            st.scatter_chart(Review_data,x=by,y='Z_score', color='Title')
        return Review_data
    else:
        return Review_data.groupby(by).agg({
            'Score': 'mean',      # score 평균
            'Z_score': 'count',    # z_score 평균
            **{col: 'first' for col in Review_data.columns if col not in ['ISBN', 'Score', 'Z_score']}  # 나머지 열 첫 번째 값
        }).reset_index()
                

def BookLists(Review_data):
    Review_data=update_groupby_score(Review_data,'ISBN',False,'mean')
    Review_data.rename(columns={'Z_score':'Review #'},inplace=True)
    Output=Review_data.filter(items=['Review #','image','Title','Author','Stars','Score','ISBN']).sort_values(by=['Review #','Score'], ascending=False)
    return Output

def user_submit():
    if ideatext is not None:
        with open('idea.json','a') as f:
            f.writelines(ideatext+'\n')


def get_unix_range(year:int, month:int):
    # 기준 월의 시작
    start = datetime(year, month, 1)
    # 기준 월의 끝 (다음 달 1일에서 -1초)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Unix timestamp 변환
    start_timestamp = int(start.timestamp() * 1000)  # milliseconds
    end_timestamp = int(end.timestamp() * 1000)      # milliseconds
    return start_timestamp, end_timestamp

def find():
    st.balloons()
    
    config=ConfigParser()
    config.read('conf.ini')
    if not attending==config['attending']['names']:
        update_config('attending')
    
    review_time=[(rv.time, rv.reviewer) for rv in reviews if not rv.unwanted]
    start,end=get_unix_range(int(current_year),int(selected_month))
    done=[]
    for t, person in review_time:
        print(t)
        if start<=t<=end:
            done.append(person)
    import numpy as np
    not_done=[]
    for person in attending.split('/'):
        if not person in done:
            not_done.append(person)
    finally_str=', '.join(not_done) if not_done else '없습니다🤩'

    st.toast(f'{selected_month}월의 범인은!! '+finally_str,icon="🔥")


checkConfig()

do_reload=check_review_load_time()
reviews=get_reviewDict(do_reload)
Review_data, real_reviews=reviewDF(reviews)
further_data=getFurtherReviews() ##last_data_path를 읽어옴.
newidx=newReviewCnt(Review_data,further_data)
Review_data=updateBooksInfo(further_data, Review_data, newidx)
with st.expander('개인별 점수분포'):
    Review_data=update_groupby_score(Review_data, 'reviewer',show_z_plot)
    st.write('마우스를 올리면 책이름을 알 수 있습니다.')

with st.sidebar:
    st.write('마지막 리뷰 Update: '+time_of_data(mod_time))
    st.button('Update', type='primary', on_click=update_reviews)
    st.subheader('범인은? 👮')
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month-1 if current_date.month>1 else 12

    # 월 범위 생성 (1월부터 12월까지)
    month_options = [f"{month:02d}" for month in range(1, 13)]

    # 슬라이더로 기준 월 선택
    selected_month = st.select_slider(
        f"{current_year} 어느 달의 범인을 찾나요?",
        options=month_options,
        value=f"{current_month:02d}",  # 기본값은 현재 월
    )

    attending=st.text_area('👇 후보군',value=attending, help='이번달 참여자 입력')
    st.button('범인찾기',on_click=find)
    ideatext=st.text_area('✍️이런 기능을 추가해주세요.')
    st.button('Submit', on_click=user_submit)

new_book_lists=BookLists(Review_data)
st.subheader('✅책을 선택해 보세요! ')
event=st.dataframe(new_book_lists,
                   column_config={'image': st.column_config.ImageColumn('Cover'),'Title': st.column_config.Column(width='medium'),'Author': st.column_config.Column(width='small')},
                   height=500,use_container_width=True,hide_index=True,on_select="rerun", selection_mode='multi-row')
my_choose=new_book_lists.iloc[event.selection.rows]
Review_data['real_review']=real_reviews

if not my_choose.empty:
    st.subheader('✅리뷰!')
    havetoshow=Review_data[Review_data.ISBN.isin(my_choose.ISBN)]
    for tab,review in zip(st.tabs(list(havetoshow.reviewer)),havetoshow.real_review):
        tab.write(review)
else:
    st.subheader('⬆️위에서 리뷰를 선택해보세요!')
    st.image('example.png')