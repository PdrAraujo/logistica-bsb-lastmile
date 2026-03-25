import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from src.otimizador import MotorOtimizacao

# 1. Configuracao da Pagina
st.set_page_config(page_title="Logistica BSB Optimizer", layout="wide")

# 2. Definicoes Globais
CORES_ROTAS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

@st.cache_resource
def carregar_motor():
    return MotorOtimizacao("data/pedidos_bsb.csv")

motor = carregar_motor()

# 3. Gerenciamento de Estado
if 'mapa_objeto' not in st.session_state:
    st.session_state.mapa_objeto = None
if 'resultados_otimizacao' not in st.session_state:
    st.session_state.resultados_otimizacao = None

# --- SIDEBAR ---
st.sidebar.header("Painel de Controle")
st.sidebar.markdown("---")
st.sidebar.write(f"Pedidos: {len(motor.df)}")
st.sidebar.write(f"Peso Total: {motor.df['peso_kg'].sum():.2f} kg")

btn_calcular = st.sidebar.button("Calcular Rotas Otimizadas", use_container_width=True)

# --- LOGICA ---
if btn_calcular:
    with st.spinner('Otimizando rotas...'):
        resultados = motor.resolver_e_retornar_rotas()
        st.session_state.resultados_otimizacao = resultados
        
        m = folium.Map(location=[-15.8153, -47.9535], zoom_start=11, tiles="cartodbpositron")
        folium.Marker([-15.8153, -47.9535], popup="CD SIA", icon=folium.Icon(color='red', icon='home')).add_to(m)
        
        for i, rota in enumerate(resultados):
            cor_atual = CORES_ROTAS[i % len(CORES_ROTAS)]
            coords_linha = []
            
            for node_index in rota['caminho']:
                if node_index == 0:
                    lat, lon = -15.8153, -47.9535
                else:
                    ponto = motor.df.iloc[node_index - 1]
                    lat, lon = ponto['lat'], ponto['lon']
                    folium.CircleMarker(
                        [lat, lon], radius=4, color=cor_atual, fill=True, fill_opacity=0.7,
                        popup=f"ID: {ponto['id_rastreio']}<br>Peso: {ponto['peso_kg']}kg"
                    ).add_to(m)
                coords_linha.append([lat, lon])
            
            folium.PolyLine(coords_linha, color=cor_atual, weight=4, opacity=0.8).add_to(m)
        
        st.session_state.mapa_objeto = m

# --- DISPLAY ---
st.title("Otimizador de Logistica Last-Mile")
st.subheader("Operacao Brasilia-DF")

if st.session_state.resultados_otimizacao:
    res = st.session_state.resultados_otimizacao
    dist_total = sum([r['distancia_km'] for r in res])
    
    # 1. Métricas no topo
    c1, c2, c3 = st.columns(3)
    c1.metric("Veiculos em Operacao", f"{len(res)}")
    c2.metric("Distancia Total Planejada", f"{dist_total:.2f} km")
    c3.metric("Media de Eficiencia", f"{dist_total/len(res):.2f} km/rota")
    
    # 2. Divisão em Abas: Mapa e Itinerário
    tab1, tab2 = st.tabs(["Mapa de Rotas", "Itinerario de Entrega"])
    
    with tab1:
        st_folium(
            st.session_state.mapa_objeto, 
            width=1300, 
            height=600, 
            key="mapa_final_estavel",
            returned_objects=[]
        )
    
    with tab2:
        st.write("### Lista de Despacho por Veiculo")
        for i, rota in enumerate(res):
            with st.expander(f"Rota {i+1} - {rota['veiculo']} ({rota['distancia_km']} km)"):
                # Criar a lista de paradas ordenada
                dados_itinerario = []
                # Pulamos o primeiro (0) e o último (0) que são o CD SIA
                paradas = rota['caminho'][1:-1]
                
                for ordem, node_index in enumerate(paradas, start=1):
                    ponto = motor.df.iloc[node_index - 1]
                    dados_itinerario.append({
                        "Ordem": ordem,
                        "ID Pedido": ponto['id_rastreio'],
                        "Regiao": ponto['ra_destino'],
                        "CEP": ponto['cep'],
                        "Peso (kg)": ponto['peso_kg'],
                        "Prioridade": ponto['prioridade']
                    })
                
                # Exibir como tabela formatada
                st.table(dados_itinerario)
                
                # Botão para baixar a lista em CSV (Simulando o envio para o entregador)
                df_rota = pd.DataFrame(dados_itinerario)
                csv = df_rota.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Baixar Itinerario Rota {i+1}",
                    data=csv,
                    file_name=f"rota_{i+1}_bsb.csv",
                    mime="text/csv",
                )

else:
    st.info("Clique no botao a esquerda para gerar o plano de rotas.")