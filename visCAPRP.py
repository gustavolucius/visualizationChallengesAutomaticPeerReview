import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.title('Peer Reviews - Visualization')

# Checkboxes para filtrar por ano
st.sidebar.header('Filtrar por Ano')
show_2019 = st.sidebar.checkbox('Mostrar artigos de 2019', value=True)
show_2021 = st.sidebar.checkbox('Mostrar artigos de 2021', value=True)

years_to_show = []
if show_2019:
    years_to_show.append(2019)
if show_2021:
    years_to_show.append(2021)

# Checkboxes para filtrar por situação final
st.sidebar.header('Filtrar por Situação Final')
show_acc = st.sidebar.checkbox('Mostrar artigos Aprovados', value=True)
show_rej = st.sidebar.checkbox('Mostrar artigos Reprovados', value=True)

final_to_show = []
if show_acc:
    final_to_show.append(1)
if show_rej:
    final_to_show.append(0)

csv_files = ['base_scientometrics_reviews_part1.csv', 'base_scientometrics_reviews_part2.csv', 'base_scientometrics_reviews_part3.csv', 'base_scientometrics_reviews_part4.csv']
df_reviews = pd.concat([pd.read_csv(f) for f in csv_files])
#df_reviews = pd.read_csv('base_scientometrics_reviews.csv')
df_papers = pd.read_csv('base_scientometrics_papers.csv')

df_papers = df_papers[['id_paper', 'title']]

idlist = np.unique(df_reviews['id_paper'].tolist())
listoflist = [
    [item, group['rating_old'].tolist(), group['rating_new'].tolist()]
    for item, group in df_reviews.groupby('id_paper')
]
data_aux = pd.DataFrame(listoflist, columns=["id_paper", "list_rating_old", "list_rating_new"])

new_df = df_reviews[['id_paper', 'rating_old', 'rating_new', 'confidence_old', 'confidence_new', 'year', 'decision']]
df_grouped = new_df.groupby('id_paper').mean().reset_index()

df_grouped['dif_mean'] = df_grouped['rating_new'] - df_grouped['rating_old']

df_grouped = pd.merge(df_grouped, data_aux, on='id_paper', how='inner')
df_grouped = pd.merge(df_grouped, df_papers, on='id_paper', how='inner')

def map_colors_var(variation):
    if variation == 0:
        return 'black'
    elif variation > 0:
        intensity = min(variation * 255, 255)
        return f'rgb(0, 0, {intensity})'
    else:
        intensity = min(-variation * 255, 255)
        return f'rgb({intensity}, 0, 0)'

def map_colors_final(final):
    if final == 0:
        return 'red'
    else:
        return 'green'

# Definindo o DataFrame inicial
filtered_df = df_grouped.copy()

# Lista para armazenar os pares de notas
if 'pares' not in st.session_state:
    st.session_state.pares = []
    
# Seletor para escolher o gráfico a ser exibido
st.sidebar.header('Selecione o tipo de Gráfico:')
grafico_selecionado = st.sidebar.selectbox('Opções', ('Variação da Média das Notas', 'Decisão Final'))

st.sidebar.header('Selecione um par de nota para pesquisar artigos com essa combinação:')
# Dropdowns para selecionar notas
rating_options = ["Todas"] + list(range(1, 11))
rating_old = st.sidebar.selectbox('Selecione uma nota antiga', rating_options)
rating_new = st.sidebar.selectbox('Selecione uma nota nova', rating_options)

# Botão de adicionar par
if st.sidebar.button('Adicionar Par'):
    if (rating_old, rating_new) in st.session_state.pares:
        st.sidebar.warning("Este par já foi adicionado.")
    else:
        st.session_state.pares.append((rating_old, rating_new))
        st.sidebar.success(f'Par adicionado: ({rating_old}, {rating_new})')
    st.rerun()
    
# Exibir os pares adicionados
st.sidebar.subheader('Pares de Notas: (Antiga, Nova)')
if st.session_state.pares:
    for i, (na, nn) in enumerate(st.session_state.pares):
        col1, col2, col3 = st.sidebar.columns([0.1, 0.8, 0.1])
        col2.write(f"Par {i+1}: ({na}, {nn})")
        if col3.button('X', key=f'remove_{i}'):
            st.session_state.pares.pop(i)
            st.rerun()
else:
    st.sidebar.write("Nenhum par adicionado.")

if grafico_selecionado == 'Variação da Média das Notas':
    if st.session_state.pares:
        filtered_rows = []
        for index, row in new_df.iterrows():         
            for pair in st.session_state.pares:
                if pair == ("Todas", "Todas"):
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif pair[0] == "Todas" and row['rating_new'] == pair[1]:
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif pair[1] == "Todas" and row['rating_old'] == pair[0]:
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif (row['rating_old'], row['rating_new'].astype('int64')) == pair:
                    filtered_rows.append(row['id_paper'].astype('int64'))
                    
        filtered_df = df_grouped[df_grouped['id_paper'].isin(filtered_rows)] 

    filtered_df = filtered_df[filtered_df['decision'].isin(final_to_show)]
    df_total_year = filtered_df.copy()
    filtered_df = filtered_df[filtered_df['year'].isin(years_to_show)]
    
    fig_var_conf = px.scatter(filtered_df, x='rating_old', y='rating_new', color=filtered_df['dif_mean'].apply(map_colors_var), 
                              color_discrete_map="identity",
                              labels={'rating_new': 'Média Nova', 'rating_old': 'Média Antiga', 'dif_mean': 'Diferença na Média',
                                      'decision': 'Situação Final'},
                              title='Gráfico de Notas com Variação da Média da Nota')

    custom_data = ['title', 'list_rating_old', 'rating_old', 'list_rating_new', 'rating_new', 'dif_mean']
    
    lines_info = {}
    fig_var_conf.data = []
    for year in filtered_df['year'].unique():
        df_year = filtered_df[filtered_df['year'] == year]
        for variation in df_year['dif_mean'].apply(lambda x: 'Aumentou' if x > 0 else 'Manteve' if x == 0 else 'Diminuiu').unique():
            df_variation = df_year[df_year['dif_mean'].apply(lambda x: 'Aumentou' if x > 0 else 'Manteve' if x == 0 else 'Diminuiu') == variation]
            symbol = 'cross' if year == 2021 else 'circle' if year == 2019 else 'circle'
            color = 'blue' if variation == 'Aumentou' else 'red' if variation == 'Diminuiu' else 'black'           
            line_key = f'{year}_{variation}'
            lines_info[line_key] = dict(
                x=df_variation['rating_old'],
                y=df_variation['rating_new'],
                mode='markers',
                marker=dict(symbol=symbol, size=5, color=color),
                name = f'{int(year)} - {variation}',                
                customdata = df_variation[custom_data].values,
                hovertemplate='<br>'.join([
                    'Título do Artigo: %{customdata[0]}',
                    'Lista de Notas Antigas: %{customdata[1]}',
                    'Média Antiga: %{customdata[2]:.2f}',
                    'Lista de Notas Novas: %{customdata[3]}',
                    'Média Nova: %{customdata[4]:.2f}',
                    'Diferença na Média: %{customdata[5]:.2f}'
                    ]) + '<extra></extra>'
            )
    
    # Adiciona todas as linhas de uma vez ao plot
    for line_key, line_info in lines_info.items():
        fig_var_conf.add_trace(go.Scatter(**line_info))
        
    # Exibe a legenda
    fig_var_conf.update_layout(showlegend=True, legend_title_text='Variação de Nota por Ano')
    st.plotly_chart(fig_var_conf)


    # Montar gráfico de barras para variação da média por ano
    var_counts_2019 = filtered_df[filtered_df['year'] == 2019]['dif_mean'].apply(lambda x: 'Aumentou' if x > 0 else 'Manteve' if x == 0 else 'Diminuiu').value_counts().reset_index()
    var_counts_2021 = filtered_df[filtered_df['year'] == 2021]['dif_mean'].apply(lambda x: 'Aumentou' if x > 0 else 'Manteve' if x == 0 else 'Diminuiu').value_counts().reset_index()
    var_counts_total = df_total_year['dif_mean'].apply(lambda x: 'Aumentou' if x > 0 else 'Manteve' if x == 0 else 'Diminuiu').value_counts().reset_index()
    
    # Adicionar coluna de ano
    var_counts_2019.columns = ['Variação', 'Quantidade']
    var_counts_2019['Ano'] = '2019'
    var_counts_2021.columns = ['Variação', 'Quantidade']
    var_counts_2021['Ano'] = '2021'
    var_counts_total.columns = ['Variação', 'Quantidade']
    var_counts_total['Ano'] = 'Total'

    var_counts_combined = pd.concat([var_counts_2019, var_counts_2021, var_counts_total])

    fig_var_bar = px.bar(var_counts_combined, x='Variação', y='Quantidade', color='Ano', barmode='group',
                          title='Número de Artigos por Variação de Nota',
                          color_discrete_map={'2019': 'green', '2021': 'orange', 'Total': 'purple'})
    
    st.plotly_chart(fig_var_bar)    
    
else:
    if st.session_state.pares:
        filtered_rows = []
        for index, row in new_df.iterrows():         
            for pair in st.session_state.pares:
                if pair == ("Todas", "Todas"):
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif pair[0] == "Todas" and row['rating_new'] == pair[1]:
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif pair[1] == "Todas" and row['rating_old'] == pair[0]:
                    filtered_rows.append(row['id_paper'].astype('int64'))
                elif (row['rating_old'], row['rating_new'].astype('int64')) == pair:
                    filtered_rows.append(row['id_paper'].astype('int64'))

        filtered_df = df_grouped[df_grouped['id_paper'].isin(filtered_rows)]            
        

    filtered_df = filtered_df[filtered_df['decision'].isin(final_to_show)]
    df_total_year = filtered_df.copy()
    filtered_df = filtered_df[filtered_df['year'].isin(years_to_show)]
    filtered_df['Ano'] = filtered_df['year'].apply(lambda x: 'square' if x == 2021 else 'circle' if x == 2019 else 'circle')
    
    filtered_df['decision'] = filtered_df['decision'].apply(lambda x: 'Aprovado' if x == 1 else 'Reprovado')
    fig_decisao = px.scatter(filtered_df, x='rating_old', y='rating_new', color='decision', 
                             color_discrete_map={'Aprovado': 'blue', 'Reprovado': 'red'}, symbol='Ano',
                             labels={'rating_new': 'Média Nova', 'rating_old': 'Média Antiga', 'dif_mean': 'Diferença na Média',
                                     'decision': 'Situação Final'},
                             title='Gráfico de Notas com Decisão Final')
    
    custom_data = ['title', 'list_rating_old', 'rating_old', 'list_rating_new', 'rating_new', 'dif_mean', 'decision']
    
    lines_info = {}
    fig_decisao.data = []
    for year in filtered_df['year'].unique():
        df_year = filtered_df[filtered_df['year'] == year]
        for decision in df_year['decision'].unique():
            df_decision = df_year[df_year['decision'] == decision]
            symbol = 'cross' if year == 2021 else 'circle' if year == 2019 else 'circle'
            color = 'blue' if decision == 'Aprovado' else 'red'
            line_key = f'{year}_{decision}'  # Chave única para cada linha
            lines_info[line_key] = dict(
                x=df_decision['rating_old'],
                y=df_decision['rating_new'],
                mode='markers',
                marker=dict(symbol=symbol, size=5, color=color),
                name = f'{int(year)} - {decision}',
                customdata = df_decision[custom_data].values,
                hovertemplate='<br>'.join([
                    'Título do Artigo: %{customdata[0]}',
                    'Lista de Notas Antigas: %{customdata[1]}',
                    'Média Antiga: %{customdata[2]:.2f}',
                    'Lista de Notas Novas: %{customdata[3]}',
                    'Média Nova: %{customdata[4]:.2f}',
                    'Diferença na Média: %{customdata[5]:.2f}'
                    ]) + '<extra></extra>'
            )
    
    # Adiciona todas as linhas de uma vez ao plot
    for line_key, line_info in lines_info.items():
        fig_decisao.add_trace(go.Scatter(**line_info))
    
    # Atualiza o layout para exibir a legenda
    fig_decisao.update_layout(showlegend=True, legend_title_text='Situação Final por Ano')
    st.plotly_chart(fig_decisao)

    # Criar gráfico de barras
    df_total_year['decision'] = df_total_year['decision'].apply(lambda x: 'Aprovado' if x == 1 else 'Reprovado')
    dec_counts_2019 = filtered_df[filtered_df['year'] == 2019]['decision'].value_counts().reset_index()
    dec_counts_2021 = filtered_df[filtered_df['year'] == 2021]['decision'].value_counts().reset_index()
    dec_counts_total = df_total_year['decision'].value_counts().reset_index()
    
    # Adicionar colunas de ano
    dec_counts_2019.columns = ['Decisão', 'Quantidade']
    dec_counts_2019['Ano'] = '2019'
    dec_counts_2021.columns = ['Decisão', 'Quantidade']
    dec_counts_2021['Ano'] = '2021'
    dec_counts_total.columns = ['Decisão', 'Quantidade']
    dec_counts_total['Ano'] = 'Total'
    
    # Combinar os DataFrames
    dec_counts_combined = pd.concat([dec_counts_2019, dec_counts_2021, dec_counts_total])
    
    # Criar o gráfico
    fig_dec_bar = px.bar(dec_counts_combined, x='Decisão', y='Quantidade', color='Ano', barmode='group',
                         title='Número de Artigos por Decisão Final',
                         color_discrete_map={'2019': 'green', '2021': 'orange', 'Total': 'purple'})

    st.plotly_chart(fig_dec_bar)