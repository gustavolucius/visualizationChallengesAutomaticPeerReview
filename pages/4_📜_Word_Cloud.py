import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="CAPRP Viz",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",  # Define o layout da página como 'wide'
    #initial_sidebar_state="expanded"  # Expande a barra lateral inicialmente
)

st.title('Word Cloud - Visualization')

def read_file(file_name):
    file = open('data/'+file_name+".txt", "r")
    content = file.read()
    #print(content)
    file.close()
    return content.lower()

# Create and generate a word cloud image:
def create_wordcloud(topic):
    if topic == 'Title':
        topic = 'title'
    elif topic == 'Abstract':
        topic = 'abstract'
    elif topic == 'Key-words':
        topic = 'key_words'
    elif topic == 'Topics from abstract':
        topic = 'topic abstract'
    elif topic == 'Review':
        topic = 'review'
    else:
        topic = 'rebuttal'

    #wordcloud = WordCloud().generate(topic)
    #return wordcloud
    return topic

# Create text

#title = read_file('title')
#abstract = read_file('abstract')
#key_words = read_file('key_words')
#topics = read_file('topic abstract')
#review = read_file('review')
#rebuttal = read_file('rebuttal')



topic = st.selectbox('Select an option:',['Title','Abstract','Key-words','Topics from abstract','Review','Rebuttal'])

if topic == 'Review':
    nota_review = st.selectbox('Select a rating:',['all','1','2','3','4','5','6','7','8','9','10'])
    if nota_review == 'all':
        file_name = 'review'
    else:
        file_name = 'review_' +  nota_review
elif topic == 'Rebuttal':
    nota_rebuttal = st.selectbox('Select a rating:',['all','1','2','3','4','5','6','7','8','9','10'])
    if nota_rebuttal == 'all':
        file_name = 'rebuttal'
    else:
        file_name = 'rebuttal_' +  nota_rebuttal
else:
    file_name = create_wordcloud(topic)


file = read_file(file_name)
wordcloud = WordCloud().generate(file)


# Display the generated image:
fig, ax = plt.subplots(figsize = (12, 8))
ax.imshow(wordcloud)
plt.axis("off")
st.pyplot(fig)