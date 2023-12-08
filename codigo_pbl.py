## Importando bibliotecas
import pandas as pd
import streamlit as st
import re
from datetime import timedelta

# Estética
css = """ 
<style>
    [data-testid="stSidebarContent"]{
        background-color: #40608f;
    }

    [data-testid="stVerticalBlock"]{
        background-color: #4bccb4;
       padding-top: 10px;
       padding-right: 10px;
       padding-bottom: 10px;
       padding-left: 10px;
       border-radius: 10px;
    }
    # class="st-emotion-cache-1wmy9hl e1f1d6gn0"
    # data-testid="stVerticalBlock"

    [class="main st-emotion-cache-uf99v8 ea3mdgi5"]{
        background-color: white;
    }

    [data-testid="stHeader"]{
        background-color: #40608f;
    }

    [level="1"]{
        color: #ffffff;


</style>
"""
st.markdown(css, unsafe_allow_html=True)








def tela_busca():
    st.write("# Pesquise pelo nome da **bactéria**")
    
    # Importando os dados
    raw = pd.read_csv('https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv')
    
    # Mudando o nome das colunas por motivos práticos
    new_column_names = {
        'ds_tipo_encontro': 'local',
        'dh_prescricao_lancamento': 'data_remedio',
        'cd_sigla_microorganismo': 'sigla_mic',
        'ds_micro_organismo': 'mic',
        'ds_antibiotico_microorganismo': 'antibiotico',
        'cd_interpretacao_antibiograma': 'resposta',
        'dh_liberacao_exame': 'data_exame',
        'id_prontuario': 'paciente'
    }
    raw = raw.rename(columns = new_column_names)

    # Removendo colunas indesejadas e linhas com incompletudes
    raw = raw[['local', 'data_remedio', 'mic', 'sigla_mic', 'antibiotico', 'resposta', 'data_exame', 'paciente']]
    raw = raw.dropna()
    
    # Mudando para formato de data e horário as colunas com datas e horários no formato numérico
    raw['data_remedio'] = pd.to_datetime(raw['data_remedio'])
    raw['data_exame'] = pd.to_datetime(raw['data_exame'])
    
    # Criando coluna ano_remedio
    raw['ano_remedio'] = raw['data_remedio'].dt.year
    
    left_col, right_col = st.columns(2)
    # Imagem da bactéria wolverine
    with right_col:
        st.image("https://weblog.wur.eu/international-students/wp-content/uploads/sites/7/2018/01/pic1.png", width=300)
        #st.image("https://www.uvpediatrics.com/wp-content/uploads/2016/04/superbugs4.gif", width=250)
    with left_col:
        # Criando busca
        busca = st.text_input(label="Digite aqui o noma da bactéria", placeholder="ex.: streptococcus", max_chars=50)
        
        # Criando o slider do período
        periodo = st.slider("Selecione o período da busca", min_value = min(raw["ano_remedio"]), max_value = max(raw["ano_remedio"]), value = (min(raw["ano_remedio"]),max(raw["ano_remedio"])))
        intervalo = [year for year in list(set(raw['ano_remedio'])) if periodo[0] <= year <= periodo[1]]
        raw = raw[raw['ano_remedio'].isin(intervalo)]
        
        # Criando seleção de locais
        #locais = st.multiselect('Selecione os locais que deseja observar', set(raw['local']), set(raw['local']))
        
        # Criando toggle dos 30 dias
        if st.toggle("Selecione se quiser remover todos os exames feitos a menos de 30 dias de outro exame pelo mesmo paciente"):
            raw['data_exame'] = pd.to_datetime(raw['data_exame'])
            raw.sort_values(by=['paciente', 'data_exame'], inplace=True)
            filtered_raw = raw.groupby('paciente', group_keys=False).apply(lambda group: group[(group['data_exame'].diff().isnull()) | (group['data_exame'].diff() >= timedelta(days=30))])
            raw = filtered_raw.copy()

    # Quando der enter na busca
    if busca:
        # Subsetting somente com as linhas que tem a bactéria
        raw = raw[(raw['mic'].str.contains(busca, case=False, flags=re.IGNORECASE)) | (raw['sigla_mic'].str.contains(busca, case=False, flags=re.IGNORECASE))]
        # Número de bacérias que deram match na busca
        num_matches = len(set(raw['mic']))
            
        if num_matches > 1:
            st.write("#### Você quis dizer: ")
            for i in set(raw['mic']):
                st.write(i)
        elif num_matches == 0:
            st.write("Busca sem resultados")
        else:
            i_lb = 1
            i_rb = -1

            bacteria = raw['mic'].iloc[0]
            #st.write("### Resultados da busca por ", bacteria)
            st.write("#", bacteria)

            if periodo[0]==periodo[1]: # seria legal se desse pra fazer isso numa linha só
                st.write("##### (", str(len(raw['mic'])), "casos registrados de ", bacteria, " em ", str(periodo[0]), ")")
            else:
                st.write("##### (", str(len(raw['mic'])), "casos registrados de ", bacteria, " de ", str(periodo[0]), " a ", str(periodo[1]), ")")
                    
            for antibiotico in list(set(raw['antibiotico'])):
                    
                # Criando subset de mesma bactéria e mesmo antibiótico
                sub = raw[raw['antibiotico'].str.contains(antibiotico)]
                if len(sub. index) != 0:
                    # Calculando as porcentagens
                    counts = (sub['resposta'] == "Resistente").sum()
                    N = len(sub['resposta'])
                    percent = round((counts/N)*100, 2)
                    st.divider()
                    st.write("#", antibiotico) 
                    st.write("### Porcentagem de resistência = ", str(percent), "%")
                    if periodo[0]==periodo[1]: # seria legal se desse pra fazer isso numa linha só
                        st.write("(", str(N), " casos de ", bacteria, " tratados com ", antibiotico, " em ", str(periodo[0]), ")")
                    else:
                        st.write("(", str(N), " casos de ", bacteria, " tratados com ", antibiotico, " de ", str(periodo[0]), " a ", str(periodo[1]), ")")
                        
                    # Ajustando os dados para os gráficos
                    time_graph = sub.pivot_table(index='ano_remedio', columns='resposta', aggfunc='size', fill_value=0)                
                    row_sums = time_graph.sum(axis=1)
                    time_graph = time_graph.div(row_sums, axis=0) * 100
                    space_graph = sub.pivot_table(index='local', columns='resposta', aggfunc='size', fill_value=0)
                    row_sums = space_graph.sum(axis=1)
                    space_graph = space_graph.div(row_sums, axis=0) * 100
                    
                    # Plotando os gráficos
                    lb, rb = st.columns(2)
                    with lb:
                        if st.button("Evolução pelo tempo", key = i_lb):
                            st.bar_chart(data = time_graph, x = None, y = None, color=None, width=0, height=0, use_container_width=True)
                                
                    with rb:
                        if st.button("Distribuição espacial", key = i_rb):
                            st.bar_chart(data = space_graph, x=None, y=None, color=None, width=0, height=0, use_container_width=True)
                                
                    i_lb += 1
                    i_rb -= 1         

    











def sobre_nos():
    st.write("## Sobre nós")
    left_col, right_col = st.columns(2)
    with left_col:
        st.write("Somos o grupo 9 do segundo semestre da T1 curso de Engenharia Biomédica da Faculdade Israelita de Ciências da Saúde Albert Einstein.")
        st.write("Somos: Ana Carolina Akemy, Felipe Iannarelli, Graziele Rodrigues, Helena Gomes, Pedro Henrique Oliveira, Sophia Nickerson, Yuri Castriota")
        st.write("Nosso objetivo com este projeto é providenciar uma nova ferramenta que ajude médicos e instituições de saúde no controle do surgimento de bactérias resistentes a antibióticos.")
    with right_col:
        st.image("https://s1.static.brasilescola.uol.com.br/be/vestibular/albert-einstein-57f7747aebe93.jpg", width=250)
        st.image("https://medicinasa.com.br/wp-content/uploads/2022/06/Centro-de-Ensino-e-Pesquisa-do-Einstein-3.jpg", width=250)
        
def sobre_analise():
    st.write("## Sobre os dados e a análise")
    left_col, right_col = st.columns(2)
    with left_col:
        st.write("#### De onde são os dados afinal?")
        st.write("Os dados utilizados neste estudo pertencem à rede de serviços de saúde prestados pela Sociedade Israelita Albert Einstein. Aqui há dados de 28.219 pacientes coletados em 48 diferentes locais da rede, datas desde 2016, 6 microrganismos, 45 antibióticos, e 5 tipos de resposta.")
        st.image("https://runfun.com.br/runfun2021/wp-content/uploads/2020/03/Logo-Hospital-Albert-Einstein.png")
    with right_col:
        st.write("#### Como interpretar a análise?")
        st.write("Após a busca por uma bactéria, todos os antibióticos que já foram utilizados para tratá-la aparecerão em baixo.")
        st.write("A porcentagem indica quantos de todos os casos tratados com aquele antibiótico desenvolveram resistência ao tratamento. O N indica quantos casos foram tratados com aquele antibiótico e é uma métrica importante para julgar a porcentagem.")
        #st.image("https://runfun.com.br/runfun2021/wp-content/uploads/2020/03/Logo-Hospital-Albert-Einstein.png")

def principal():
    st.sidebar.write("# Painel de Monitoramento de Resistência Microbiana a Antibióticos")
    selected_page = st.sidebar.radio("Navegação", ("Tela de busca", "Sobre os dados e as análises", "Sobre nós"))
    st.sidebar.write("# Como funciona o site:")
    st.sidebar.write("Aqui você pode buscar por **bactérias** e descobrir para quais **antibióticos** esses microorganismos apresentam maior resistência ou sensibilidade. Além disso, é possível observar o crescimento com o tempo da resistência aos antibióticos e quais alas hospitalares são mais afetadas.")
    if selected_page == "Tela de busca":
        tela_busca()
    elif selected_page == "Sobre nós":
        sobre_nos()
    elif selected_page == "Sobre os dados e as análises":
        sobre_analise()

principal()

