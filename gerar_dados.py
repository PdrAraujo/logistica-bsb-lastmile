import pandas as pd
import random

# Configurações do Centro de Distribuição (SIA)
CD_SIA = {"lat": -15.8153, "lon": -47.9535, "nome": "SIA Trecho 3"}

# Mapeamento de RAs com faixas de CEP e coordenadas aproximadas
REGIOES_BSB = [
    {"ra": "Asa Sul", "ceps": "70300-000", "lat": -15.812, "lon": -47.901},
    {"ra": "Asa Norte", "ceps": "70700-000", "lat": -15.765, "lon": -47.887},
    {"ra": "Águas Claras", "ceps": "71900-000", "lat": -15.839, "lon": -48.024},
    {"ra": "Taguatinga", "ceps": "72000-000", "lat": -15.833, "lon": -48.056},
    {"ra": "Guará", "ceps": "71000-000", "lat": -15.815, "lon": -47.975},
    {"ra": "Ceilândia", "ceps": "72200-000", "lat": -15.820, "lon": -48.110}
]

def gerar_rastreio():
    return f"BSB{random.randint(100000, 999999)}BR"

pedidos = []

for i in range(100):
    regiao = random.choice(REGIOES_BSB)
    
    # Adicionando uma pequena variação aleatória nas coordenadas para não ficarem todas no mesmo ponto
    lat = regiao["lat"] + random.uniform(-0.01, 0.01)
    lon = regiao["lon"] + random.uniform(-0.01, 0.01)
    
    # Simulando peso e volume (E-commerce)
    peso = round(random.uniform(0.5, 30.0), 2)
    volume = round(peso * 0.01, 3) # Volume proporcional ao peso
    
    pedido = {
        "id_rastreio": gerar_rastreio(),
        "ra_destino": regiao["ra"],
        "cep": regiao["ceps"],
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "peso_kg": peso,
        "volume_m3": volume,
        "prioridade": random.choice(["Normal", "Expressa"]),
        "prazo_horas": random.choice([2, 4, 12, 24])
    }
    pedidos.append(pedido)

# Salvando na pasta 'data'
df = pd.DataFrame(pedidos)
df.to_csv("data/pedidos_bsb.csv", index=False)

print("✅ Sucesso! O arquivo 'data/pedidos_bsb.csv' foi gerado com 100 pedidos.")