import json
import requests
from naverbandAPI import BandOpenApi
from urllib import request
import pandas as pd

class CIOBandToken:
    token = 'ZQAAAXGiKTyGNuCdE77hKvr9_lEVu8DSH49U_VTJO-n_6uYZm6z1VU8H6dYrT0gasEWyh0dRZH7pSbErrzJun6tZDjnbcbPIVryFA7ZiRuZvdn0Z'# 한수빈Token임. 개인정보 조회하면 한수빈으로 나옴
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

def reviews_tojson(reviews, filename):
    reviews=[rv.__dict__ for rv in reviews]
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False)

class review_post:
    unwanted=False
    score_star_table=table={
            0.5:'🌛',
            1:'⭐',
            1.5:'⭐🌛',
            2:'⭐⭐',
            2.5:'⭐⭐🌛',
            3:'⭐⭐⭐',
            3.5:'⭐⭐⭐🌛',
            4:'⭐⭐⭐⭐',
            4.5:'⭐⭐⭐⭐🌛',
            5:'⭐⭐⭐⭐⭐',         
        }
    def __init__(self,review, type='dict'):
        if type=='dict':
            self.from_dict(review)
        else: self.from_json(review)

    def from_dict(self, review):
        self.reviewer=review['author']['name']
        self.pre_contents=review['content']
        self.time=review['created_at']
        self.comment_counts=review['comment_count']
        self.emotion_count=review['emotion_count']
        self.post_key=review['post_key']
        self.refine_contents()
        self.summary['reviewer']=self.reviewer
    
    def from_json(self,review):
        for key, val in review.items():
            setattr(self, key,val)
        self.refine_contents()
        self.summary['reviewer']=self.reviewer

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
        stars, num=self.std_stars(self.summary['Stars'])
        self.summary['Score']=float(num)
        self.summary['Stars']=stars

    def std_stars(self,stars):
        stars.replace(' ','')
        one=['⭐','★','🌟','☆','🌕']
        half=['🌛', '반', '🌜', '🌗', '🫥', '🌓', '✨', '🫡', '?', '💔','.5','+0.5','쩜오','+/0.5']
        not_stars={
            '5점':('⭐⭐⭐⭐⭐',5),
            '4/5':('⭐⭐⭐⭐',4)
        }
        #3. not_stars
        if stars in not_stars:
            return not_stars[stars]
        #2. int
        if is_float(stars):
            num=is_float(stars)
        #1. 기본
        else:
            num, plus_half=0, False
            for st in one:
                num+=stars.count(st)
            for hf in half:
                if stars.count(hf)>0:
                    plus_half=True
            if plus_half: num+=0.5
            if num>5:
                return stars, 0
        if num==0:
            self.unwanted=True
            star_str=stars
        else:
            star_str=self.score_star_table[num]
    
        return star_str, num

    def refine_exceptions(self):
        keys=self.summary.keys()
        if 'Score' in keys:
            if self.summary['Score']=='인증':
                self.get_score_from_stars()
            elif not is_float(self.summary['Score']):
                self.get_score_from_stars()
            else:
                self.summary['Score']=float(self.summary['Score'])
                self.summary['Stars']=self.score_star_table[self.summary['Score']]
            
        else:
            self.unwanted=True
    

cont_hdr_exceptions={
    '완독날짜':['완독일', '완독 날짜','완독 일'],
    '한줄평': ['\n'],
    '별점': [],
    '저자':[],
    '출판사':[],
    '책 제목':[]
}

def is_float(str):
    try:
        float(str)
        return float(str)
    except:
        return False