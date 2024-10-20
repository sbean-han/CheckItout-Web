import json
import requests
from .naverbandapi.client import BandOpenApi
from urllib import request
import pandas as pd

class CIOBandToken:
    token = 'ZQAAAXGiKTyGNuCdE77hKvr9_lELYlrnntxypBloeQDh6-UqVRioF-MWU31X-vMlpLzCtggDEi0ciG9ibJnkwkoOmgg3mlKwRaOQ3Go6rZJU6Bx_'# 한수빈Token임. 개인정보 조회하면 한수빈으로 나옴
    client_id= '43936540'
    redirect_uri='http://localhost:8888'
    client_secret='mebdlfZfOzbicInuZHp15mORFL8TFUL0'
    bandkey='AAAEXPSpQDly5hUs9Q5RUmv0'

def get_reviews() ->list:
    CIOBandAPI=BandOpenApi(CIOBandToken.token)
    reviews=[]
    response=CIOBandAPI.get_posts(CIOBandToken.bandkey, "ko_KR")
    while 'items' in response:
        for it in response['items']:
            if it['content'].startswith('#인증'):
                reviews.append(review_post(it))
        params=response['paging']['next_params']
        response=CIOBandAPI.get_nextpage('posts', params, 'v2')
    
    review_summary=[rv.summary for rv in reviews]
    data=pd.DataFrame(review_summary)
    return reviews

def reviews_tojson(reviews):
    with open('reviews.json','w',encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False)

class review_post:
    def __init__(self, review):
        self.reviewer=review['author']['name']
        self.pre_contents=review['content']
        self.time=review['created_at']
        self.comment_counts=review['comment_count']
        self.emotion_count=review['emotion_count']
        self.post_key=review['post_key']
        self.refine_contents()
    
    def refine_contents(self):
        bfr_cont=self.pre_contents
        header={"#":('',2),
                '책 제목':('Score',1), 
                '저자':('Title',1), 
                '출판사':('Author', 1),
                '완독날짜':('Publisher',1),
                '별점':('',1), 
                '한줄평':('Stars',1)}
        after={}
        for hdr, how in header.items():
            sp=bfr_cont.split(hdr)
            if len(sp)<=how[1]:
                if hdr=='#':
                    how=('',1)
                else:    
                    for hd in cont_hdr_exceptions[hdr]:
                        sp=bfr_cont.split(hd)
                        if len(sp)!=1:
                            break
            if len(sp)<=how[1]:
                continue
            bfr_cont=sp[how[1]]
            if how[0]:
                after[how[0]]=sp[0].lstrip(': ').rstrip('\n ')
        self.content=bfr_cont
        self.summary=after
        self.refine_exceptions()

    def get_score_from_stars(self):
        return 'Yet'

    def refine_exceptions(self):
        keys=self.summary.keys()
        if 'Score' in keys and self.summary['Score']=='인증':
            self.summary['Score']=self.get_score_from_stars()
    

cont_hdr_exceptions={
    '완독날짜':['완독일', '완독 날짜','완독 일'],
    '한줄평': ['\n'],
    '별점': [],
    '저자':[],
    '출판사':[],
    '책 제목':[]
}