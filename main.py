import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

SUPABASE_URL = st.secrets('SUPABASE_URL')
SUPABASE_KEY = st.secrets('SUPABASE_KEY')

USERNAME = "admin"
PASSWORD = "1234"

st.markdown(
    """
    <style>
    .main {
        width: 1000px;
        margin: 0 auto;
    }
    </style>
    """, 
    unsafe_allow_html=True
)


# Criar sessão para login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Tela de login
if not st.session_state.logged_in:
    st.title("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")
else:
    # Conectar ao Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Função para puxar os dados da tabela
    def get_data_from_supabase():
        response = supabase.table('yuri_banco_de_dados_disparo_duplicate').select('*').execute()

        if response.data:
            return response.data
        else:
            st.error(f"Erro ao acessar dados: {response.error}")
            return None

    # Puxar os dados
    data = get_data_from_supabase()
    
    if data:   
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df["data"], format='%d/%m/%Y')
        df = df.sort_values(by='data', ascending=False)
        df['data'] = df['data'].dt.strftime('%d/%m/%Y')
        
        st.markdown("<h1 style='color: #DC143C;'>📊 Dashboard de Contatos</h1>", unsafe_allow_html=True)
        st.dataframe(df, hide_index=True)
        
        # 1. Gráfico de Pizza: Distribuição de Cancelamentos
        cancel_counts = df["status"].value_counts().reset_index()
        cancel_counts.columns = ['Status', 'Count']

        fig_pie_cancelamentos = px.pie(cancel_counts, values='Count', names='Status', 
                                        title='',
                                        color_discrete_sequence=['#B22222', '#CD5C5C', '#FF7F50', '#D2691E', '#FF4500'],
                                        template='plotly_dark')
        
        fig_pie_cancelamentos.update_traces(textinfo='percent+label')
                
        # 2. Gráfico de Pizza: Distribuição de Contatos por Status 
               
        curso_coluna = df["curso"].value_counts().reset_index()
        curso_coluna.columns = ['Curso', 'Quantidade_curso']
        curso_coluna = curso_coluna.sort_values(by='Quantidade_curso', ascending=False)

        
        
        fig_bar_curso = px.bar(curso_coluna, x='Curso', y='Quantidade_curso', 
                        title='',
                        color='Quantidade_curso',
                        color_continuous_scale='Turbo', 
                        template='plotly_dark')
        
        col1, col2 = st.columns(2)

        # Gráfico de Pizza (Cancelamentos) com legenda interna e sem barra lateral
        with col1:
            st.markdown("<h2 style='color: #DC143C;'>Cancelamentos</h1>", unsafe_allow_html=True)
            fig_pie_cancelamentos.update_traces(
                textinfo='label+percent', 
                insidetextorientation='radial',
                showlegend=False  # Remove a legenda lateral
            )
            st.plotly_chart(fig_pie_cancelamentos, use_container_width=True)

        # Gráfico de Barras (Cursos) sem legenda lateral
        with col2:
            st.markdown("<h2 style='color: #DC143C;'>Contatos por Curso</h1>", unsafe_allow_html=True)
            
            fig_bar_curso = px.bar(curso_coluna, y='Curso', x='Quantidade_curso', 
                                title='',
                                color='Quantidade_curso', 
                                color_continuous_scale='Turbo', 
                                template='plotly_dark')
            fig_bar_curso.update_traces(
                showlegend=False,  # Remove a legenda lateral
                text=curso_coluna['Quantidade_curso'],  # Adiciona o valor nas barras
                textposition='inside',  # Coloca o valor dentro da barra
                texttemplate='%{text}'  # Exibe o valor dentro da barra
            )
            fig_bar_curso.update_coloraxes(showscale=False)  # Remove a barra de cores
            fig_bar_curso.update_layout(xaxis_title="Quantidade", yaxis_title="")  # Ajusta os eixos
            st.plotly_chart(fig_bar_curso, use_container_width=True)

            
        # 3. Gráfico de Linha: Evolução de Contatos ao Longo do Tempo
        
        contatos_por_dia = df["data"].value_counts().sort_index().reset_index()
        contatos_por_dia.columns = ['Data', 'Número de Contatos']

        fig_line = px.line(contatos_por_dia, x='Data', y='Número de Contatos', 
                           title='Evolução de Contatos ao Longo do Tempo',
                           markers=True, 
                           line_shape='linear',
                           template='plotly_dark', 
                           color_discrete_sequence=['#DC143C'])
        
        st.plotly_chart(fig_line)
    
        # 4. Gráfico de Barras: Distribuição dos Prefixos Telefônicos
        df["prefixo"] = df["telefone"].astype(str).str[:2]
        regioes = {
            '11': '(SP)', '21': '(RJ)', '31': '(MG)', '41': '(PR)', 
            '51': '(RS)', '61': '(DF)', '71': '(BA)', '81': '(PE)', 
            '85': '(CE)', '91': '(PA)', '99': '(MA)', 'Outros': 'Outros'
        }
        df["regiao"] = df["prefixo"].map(regioes).fillna("Outros")
        regiao_counts = df["regiao"].value_counts().reset_index()
        regiao_counts.columns = ['Região', 'Quantidade']

        fig_bar = px.bar(regiao_counts, x='Região', y='Quantidade', 
                        title='Distribuição dos Prefixos por Região',
                        color='Quantidade', 
                        color_continuous_scale='Viridis', 
                        template='plotly_dark')
        st.plotly_chart(fig_bar)