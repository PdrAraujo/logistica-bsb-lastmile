import pandas as pd
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class MotorOtimizacao:
    def __init__(self, caminho_dados):
        # Carrega os dados gerados na Sprint 02
        self.df = pd.read_csv(caminho_dados)
        self.deposito_coord = (-15.8153, -47.9535) # Coordenadas do SIA
        
        # Configuração da Frota: 5 Vans e 5 Motos
        self.veiculos = (['VAN'] * 5) + (['MOTO'] * 5)
        self.capacidades_peso = [800 if v == 'VAN' else 30 for v in self.veiculos]
        
        # Definimos custos fictícios por KM para o algoritmo priorizar o mais barato
        # Vans custam mais que motos por KM no nosso modelo
        self.custos_veiculo = [350 if v == 'VAN' else 150 for v in self.veiculos]

    def gerar_matriz_distancias(self):
        """Cria matriz de distâncias em metros (inteiros) para o OR-Tools"""
        todas_coords = [self.deposito_coord] + list(zip(self.df['lat'], self.df['lon']))
        n = len(todas_coords)
        return [[int(geodesic(todas_coords[i], todas_coords[j]).meters) for j in range(n)] for i in range(n)]

    def resolver_e_retornar_rotas(self):
        """
        Função principal que resolve o problema de roteirização (VRP)
        e retorna uma lista de dicionários com os caminhos.
        """
        # 1. Preparação do Gerenciador e Modelo
        dist_matrix = self.gerar_matriz_distancias()
        manager = pywrapcp.RoutingIndexManager(len(dist_matrix), len(self.veiculos), 0)
        routing = pywrapcp.RoutingModel(manager)

        # 2. Registro do Callback de Distância (Custo)
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return dist_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 3. Adicionar Restrição de Capacidade de Peso
        def weight_callback(from_index):
            node = manager.IndexToNode(from_index)
            # Se for o depósito (0), peso é 0. Senão, pega do DataFrame
            return int(self.df.iloc[node-1]['peso_kg']) if node > 0 else 0

        weight_callback_index = routing.RegisterUnaryTransitCallback(weight_callback)
        routing.AddDimensionWithVehicleCapacity(
            weight_callback_index, 
            0, # sem folga
            self.capacidades_peso, 
            True, # inicia acumulador em zero
            'Capacidade_Peso'
        )

        # 4. Configuração da Busca (Heurística)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = 5 # Limite de 5s para calcular

        # 5. Resolver
        solucao = routing.SolveWithParameters(search_parameters)
        
        # 6. Extração dos resultados
        lista_de_rotas = []
        if solucao:
            for vehicle_id in range(len(self.veiculos)):
                index = routing.Start(vehicle_id)
                caminho_veiculo = []
                distancia_total = 0
                
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    caminho_veiculo.append(node)
                    previous_index = index
                    index = solucao.Value(routing.NextVar(index))
                    distancia_total += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                
                caminho_veiculo.append(manager.IndexToNode(index))
                
                # Só adicionamos veículos que realmente fizeram entregas (mais que sair e voltar ao CD)
                if len(caminho_veiculo) > 2:
                    lista_de_rotas.append({
                        "veiculo": self.veiculos[vehicle_id],
                        "caminho": caminho_veiculo,
                        "distancia_km": round(distancia_total / 1000, 2)
                    })
        
        return lista_de_rotas

# Bloco de teste para execução via terminal
if __name__ == "__main__":
    motor = MotorOtimizacao("data/pedidos_bsb.csv")
    print("⏳ Iniciando otimização de rotas para Brasília...")
    
    resultados = motor.resolver_e_retornar_rotas()
    
    if resultados:
        print(f"✅ {len(resultados)} rotas otimizadas encontradas!\n")
        for i, r in enumerate(resultados):
            print(f"Rota #{i+1} | Veículo: {r['veiculo']} | Distância: {r['distancia_km']}km")
            print(f"Caminho: {r['caminho']}\n")
    else:
        print("❌ Nenhuma solução encontrada que respeite as restrições.")