
import altair as alt
import streamlit as st
from vega_datasets import data
import pandas as pd
import ast


st.set_page_config(
    page_title="CAPRP Viz",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",  # Define o layout da página como 'wide'
    #initial_sidebar_state="expanded"  # Expande a barra lateral inicialmente
)

st.title('Top Words - Visualization')

def create_wordcloud(value):
    if value == '5':
        value = 5
    elif value == '10':
        value = 10
    elif value == '15':
        value = 15
    elif value == '20':
        value = 20
    else:
        value = 30
    return value

def read_file(file_name):
    file = open('data/'+file_name+".txt", "r")
    content = file.read()
    #print(content)
    file.close()
    return content.lower()

def return_data(all_data, value):
    new_data = {}
    #count_2019 = 0
    #count_2021 = 0
    data = ast.literal_eval(all_data)
    for key in data.keys():
        if data[key][0] < value or data[key][1] < value:
            new_data[key] = data[key]
    return new_data


all_data = read_file('data_ranking')
value = st.selectbox('Select the number of top words:',['5','10','15','20'], key='number_top_words')
#print(all_data)
data_filtered = return_data(all_data, int(value))

data = []

for key in data_filtered.keys():
    #print(data_filtered[key][0] )
    if int(data_filtered[key][0]) < int(value) :
        value2019 = data_filtered[key][0]
        data.append([2019, key, value2019])

    if int(data_filtered[key][1]) < int(value):
        value2021 = data_filtered[key][1]
        data.append([2021, key, value2021])

source = pd.DataFrame(data, columns=['date', 'word', 'price'])
source.date = pd.to_datetime(source.date, format='%Y')
#print(source)

chart = alt.Chart(source).mark_line(point = True).encode(
    x = alt.X("date", timeUnit="year", title="year"),
    y="rank:O",
    color=alt.Color("word:N")
    #color=alt.Color("continent").scale(range=okabe_ito)
).transform_window(
    rank="rank()",
    sort=[alt.SortField("price")],
    groupby=["date"]
).properties(
    title="Bump Chart - Key words",
    width=2400,
    height=600,
    
)


#tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])

#with tab1:
st.altair_chart(chart, theme="streamlit", use_container_width=True)
#with tab2:
#    st.altair_chart(chart, theme=None, use_container_width=True)

#filtro de palavra
all_data_complete = ast.literal_eval(read_file('data_ranking_complete'))

data_complete = []
for key in all_data_complete.keys():
    value2019 = all_data_complete[key][0]
    value2021 = all_data_complete[key][1]
    data_complete.append([key, value2019, value2021])


df_complete = pd.DataFrame(data_complete, columns=['Palavra-chave', 'Rank 2019', 'Rank 2021'])

query = st.text_input("Filter a key-word or a rank number:", key='key_word_filter')

if query:
    mask = df_complete.applymap(lambda x: query in str(x).lower()).any(axis=1)
    df_complete = df_complete[mask]

st.data_editor(
    df_complete,
    hide_index=True, 
    column_order=('Palavra-chave', 'Rank 2019', 'Rank 2021')
) 

#https://vega.github.io/vega/docs/schemes/
#st.dataframe() 
