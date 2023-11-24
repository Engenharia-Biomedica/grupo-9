## Importando bibliotecas
import pandas as pd
import streamlit as st
#from PIL import Image
import re


def tela_busca():
    st.write("# Pesquise pelo nome da **bactéria**")
    left_col, right_col = st.columns(2)

    with left_col:
        busca = st.text_input(label="Digite aqui", max_chars=50)
        if busca:
            url = 'https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv'
            raw = pd.read_csv(url)
            new_column_names = {
                'ds_tipo_encontro': 'local',
                'dh_prescricao_lancamento': 'data_prescri',
                'cd_sigla_microorganismo': 'sigla_mic',
                'ds_micro_organismo': 'mic',
                'ds_antibiotico_microorganismo': 'antibiotico',
                'cd_interpretacao_antibiograma': 'resposta'
            }
            raw = raw.rename(columns = new_column_names)

            logvet_sigla = list()
            for text in raw['sigla_mic']:
              logvet_sigla.append(bool(re.search(busca, text, re.IGNORECASE)))

            logvet_mic = list()
            for text in raw['mic']:
              logvet_mic.append(bool(re.search(busca, text, re.IGNORECASE)))

            mask = [v1 or v2 for v1, v2 in zip(logvet_sigla, logvet_mic)]
            num_matches = len(set(raw['mic'].loc[mask]))

            if num_matches > 1:
              st.write("#### Você quis dizer: ")
              for i in set(raw['mic'].loc[mask]):
                  st.write(i)
            elif num_matches == 0:
              st.write("Busca sem resultados")

    with right_col:
        st.image("https://weblog.wur.eu/international-students/wp-content/uploads/sites/7/2018/01/pic1.png", use_column_width=True)

    if busca:
        if num_matches == 1:
            i_lb = 1
            i_rb = -1
            desired_cols = ['local', 'data_prescri', 'sigla_mic', 'mic', 'antibiotico', 'resposta']
            desired_rows = mask
            subset = raw.loc[desired_rows, desired_cols]
            subset = subset.dropna(subset=['antibiotico', 'resposta', 'local', 'data_prescri'], how='any') # remove linhas com NANs
            st.write("### Resultados da busca por ", subset['mic'].iloc[0])
            for antibiotico in list(set(subset['antibiotico'])):
                filt = list()
                for med in subset['antibiotico']:
                  filt.append(antibiotico == med)
                sub = subset.loc[filt]
                for j in range(len(sub["data_prescri"])):
                    sub["data_prescri"].iloc[j] = sub["data_prescri"].iloc[j][:4]
                counter = 0
                for resp in sub['resposta']:
                    if 'Resistente' == resp:
                        counter += 1
                N = len(sub['resposta'])
                percent = round((counter/N)*100, 2)
                st.divider()
                st.write(antibiotico, "---------\tPorcentagem de resistência = ", str(percent), "% ------- ( N = ", str(N), ") ------- Score = ")
                lb, rb = st.columns(2)

                # Gráficos
                time_graph = sub.pivot_table(index='resposta', columns='data_prescri', aggfunc='size', fill_value=0)
                space_graph = sub.pivot_table(index='resposta', columns='local', aggfunc='size', fill_value=0)
                #st.write(time_graph, space_graph) # DEBUGGING!!!
                #st.write(time_graph["Resposta"])
                with lb:
                    if st.button("Evolução pelo tempo", key = i_lb):
                        st.bar_chart(data = time_graph, x =None, y = None, color=None, width=0, height=0, use_container_width=True)

                with rb:
                    if st.button("Distribuição espacial", key = i_rb):
                        st.bar_chart(data = space_graph, x=None, y=None, color=None, width=0, height=0, use_container_width=True)

                i_lb += 1
                i_rb -= 1
                #st.write(sub) # DEBUGGING!!!


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
