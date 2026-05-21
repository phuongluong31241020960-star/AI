import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class RouteMetrics:
    """Lưu trữ metrics của một tuyến đường"""
    start_node: str
    route_path: List[str]
    best_cost: float
    execution_time_ms: float
    edge_details: Dict[Tuple[str, str], float]
    is_feasible: bool

    def get_route_string(self) -> str:
        return "->".join(self.route_path + [self.route_path[0]])

class City:
    def __init__(self, id: int, city_name: str, x: float, y: float):
        self.id = id
        self.name = city_name
        self.x = x
        self.y = y

class Route:
    def __init__(self, route_list: List[City], adj_matrix: np.ndarray):
        self.route = route_list
        self.adj_matrix = adj_matrix
        self.fitness = self.calculate_fitness()
        self.is_feasible = (self.fitness != float('inf'))

    def calculate_fitness(self) -> float:
        total_dist = 0
        for i in range(len(self.route)):
            u = self.route[i].id
            v = self.route[(i + 1) % len(self.route)].id
            weight = self.adj_matrix[u][v]
            if weight == float('inf'):
                return float('inf')
            total_dist += weight
        return total_dist

    # def get_route_names(self, start_node_name: str = None) -> List[str]:
    #     names = [city.name for city in self.route]
    #     if start_node_name and start_node_name in names:
    #         idx = names.index(start_node_name)
    #         names = names[idx:] + names[:idx]
    #     return names
    
    def get_route_names(self, start_node_name: str = None) -> List[str]:
        names = [city.name for city in self.route]
        if start_node_name and start_node_name in names:
            idx = names.index(start_node_name)
            names = names[idx:] + names[:idx]
        return names

    def get_rotated_cities(self, start_node_name: str = None) -> List['City']:
        """Xoay mảng các object City sao cho start_node_name luôn nằm ở index 0 để phục vụ vẽ đồ thị"""
        if not start_node_name:
            return self.route
            
        names = [city.name for city in self.route]
        if start_node_name in names:
            idx = names.index(start_node_name)
            # Cắt và ghép mảng để đẩy start_node lên đầu
            return self.route[idx:] + self.route[:idx]
        return self.route