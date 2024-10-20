import streamlit as st
import json
from .CheckItOut import checkitoutAPI
import pandas as pd

reviews=checkitoutAPI.get_reviews()

st.title("🎈 책키라웃 리뷰 Summary Page!")
review_summary=[rv.summary for rv in reviews]
data=pd.DataFrame(review_summary)
st.dataframe(data)