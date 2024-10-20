## new_review.json과 비슷한 형태의 json일때

def reviews_json(pre_rv):
    reviews=[]
    for it in pre_rv:
        if it['content'].startswith('#인증'):
            from checkitoutAPI import review_post
            reviews.append(review_post(it))
    review_summary=[rv.summary for rv in reviews]
    data=pd.DataFrame(review_summary)
    return reviews        

reviews=reviews_json(json_reviews)
