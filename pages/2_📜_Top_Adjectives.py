
import altair as alt
import streamlit as st
from vega_datasets import data
import pandas as pd
import ast
import re

st.set_page_config(
    page_title="CAPRP Viz",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",  # Define o layout da página como 'wide'
    #initial_sidebar_state="expanded"  # Expande a barra lateral inicialmente
)


st.title('Top Adjectives - Visualization')

def get_dep_list(df, col_name):
    dep_list = set()
    dep_list.add('all')
    for index, row in df.iterrows():
        list_adj = ast.literal_eval(row[col_name+'_adj_dep'])
        for adj in list_adj:
            dep_list.add(adj) 
    return dep_list

def filter_df(df, label_list, col_name):
    filter_adj = []
    for index, row in df.iterrows():
        new_adj = []
        list_adj = ast.literal_eval(row[col_name+'_adj'])
        list_dep = ast.literal_eval(row[col_name+'_adj_dep'])
        for i in range(len(list_dep)):
            if list_dep[i] in label_list:
                new_adj.append(re.sub('[^a-zA-Z]+', '', list_adj[i].lower()))
        filter_adj.append(new_adj)
    return filter_adj


csv_files = ['data/reviews_rebuttal_adj_dep_part1.csv', 'data/reviews_rebuttal_adj_dep_part2.csv', 'data/reviews_rebuttal_adj_dep_part3.csv', 'data/reviews_rebuttal_adj_dep_part4.csv']
df_reviews = pd.concat([pd.read_csv(f, lineterminator = '\n') for f in csv_files])

col_name = st.selectbox('Select a review type:',['review','rebuttal'], key='review_type')
dep_list = get_dep_list(df_reviews, col_name)
adj_type = st.selectbox('Select a adjective type:', dep_list, key='adjective_type')
ratings = [1,2,3,4,5,6,7,8,9,10]
rate_1 = st.selectbox('Select the first rating:', ratings, key='rating')
ratings2 = ratings.copy()
ratings2.remove(rate_1)
rate_2 = st.selectbox('Select the second rating:', ratings2, key='second_rating')
top_n = st.selectbox('Select the number of top words:',['5','10','15','20'], key='top_n')

if adj_type != 'all':
    df_reviews['filter_adj'] = filter_df(df_reviews, [adj_type], col_name)
else:
    df_reviews['filter_adj'] = filter_df(df_reviews, dep_list, col_name)

filter_col = 'filter_adj'


notas = {}
for i in range(1, 11):
    notas[i] = []
    for adj_list in df_reviews[df_reviews['rating_old'] == i]['filter_adj']:
        for adj in adj_list:
            if (adj != '-') & (adj != ''):
                notas[i].append(adj.lower()) 


notas_count = {}
for key in sorted([rate_1, rate_2]):#notas.keys():
    dict_key = {}
    for f in notas[key]:
        if f in dict_key:
            dict_key[f] += 1
        else:
            dict_key[f] = 1
    #list_key = [(f, dict_key[f]) for f in dict_key]
    list_key = []
    for f in dict_key:
        list_key.append((f, dict_key[f]))
    list_key.sort(key=lambda x: x[1], reverse=True)
    notas_count[key] = list_key


data = []
for key in notas_count.keys():
    notas_count_filter = notas_count[key][:int(top_n)]
    count = 0
    for word, value in notas_count_filter:
        data.append([key, word, count])
        count += 1

source = pd.DataFrame(data, columns=['date', 'word', 'price'])
source['date'] = source['date'].astype(str)

#source.date = pd.to_numeric(source.date)
#source.date = pd.to_datetime(source.date, format='%M')

#print(source)
chart = alt.Chart(source).mark_line(point = True).encode(
    x = alt.X("date",  title="rating"),
    y="rank:O",
    color=alt.Color("word:N")
).transform_window(
    rank="rank()",
    sort=[alt.SortField("price")],
    groupby=["date"]
).properties(
    title="Bump Chart das palavras-chave",
    width=2400,
    height=600,
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)