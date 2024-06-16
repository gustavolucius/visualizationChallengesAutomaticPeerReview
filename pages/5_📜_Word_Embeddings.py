import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# Configuração da página para aumentar o espaço ocupado pelo Streamlit na tela
st.set_page_config(
    page_title="CAPRP Viz",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",  # Define o layout da página como 'wide'
    #initial_sidebar_state="expanded"  # Expande a barra lateral inicialmente
)

st.title('Word Embeddings - Visualization')

models = ['Rating < 5', 'Rating = 5', 'Rating = 6', 'Rating > 6']
# Defining a color map for the models
color_map = {
    'Rating < 5': 'red',
    'Rating = 5': 'green',
    'Rating = 6': 'purple',
    'Rating > 6': 'orange'
}

# Retrieving word embeddings
df = pd.read_csv('data/tokens.csv')
words_df = pd.read_csv('data/common_words.csv')

# Checkboxes para filtrar por modelo
st.sidebar.header('Filter by model:')

# Filtering models to show
sidebar_options = {}
for model in models:
    sidebar_options[model] = st.sidebar.checkbox(f'Show embeddings from {model}', value=True)

models_to_show = []
for model_name, option in sidebar_options.items():
    if option:
        models_to_show.append(model_name)

# Checkboxes para filtrar por modelo
st.sidebar.header('Filter by words:')

words_count = st.sidebar.selectbox(f'Show most common words', [5, 10, 20, 50])

# Creating a Plotly figure
fig = go.Figure()

for model in models_to_show:
    # Add scatter traces for each model
    model_data = df[df['model'] == model]
    model_data = model_data.merge(words_df, left_on='token', right_on='word')
    model_data = model_data.iloc[:words_count]

    fig.add_trace(go.Scatter(
        x=model_data['x'],
        y=model_data['y'],
        mode='markers+text',
        text=model_data['token'],
        marker=dict(color=color_map[model]),
        name=model,
        visible=True
    ))

fig.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=16
    ),
    xaxis_title="X Coordinate",
    yaxis_title="Y Coordinate",
    showlegend=True,
    width=1009,
    height=500
)

st.plotly_chart(fig)
