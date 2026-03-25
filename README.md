# 🚚 Otimizador de Logística: Last-Mile Brasília (E-commerce)

Este projeto aplica **Pesquisa Operacional** e **Data Science** para otimizar rotas de entrega de um e-commerce partindo do **SIA (Setor de Indústria e Abastecimento)** para as diversas RAs do Distrito Federal.

## 🎯 Objetivo de Negócio
Maximizar a ocupação da frota (Vans e Motos) e reduzir a quilometragem total rodada, priorizando pedidos de entrega expressa e respeitando as restrições de volume.

## 🛠️ Tecnologias e Metodologias
- **Linguagem:** Python 3.10+
- **Otimização:** Google OR-Tools (Vehicle Routing Problem)
- **Dashboard:** Streamlit & Plotly
- **Mapas:** Folium (OpenStreetMap)
- **Gestão:** Metodologia Ágil (Scrum/Kanban)

## 📍 Diferencial do Projeto
Diferente de modelos genéricos, este projeto utiliza a lógica de endereçamento e CEPs reais de **Brasília-DF**, considerando a distribuição geográfica entre o Plano Piloto e Cidades Satélites.

## 🚀 Como executar
1. Instale as dependências: `pip install -r requirements.txt` (em breve)
2. Execute o dashboard: `streamlit run app.py`