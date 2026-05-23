import time
import math
import random
import statistics
import numpy as np
from typing import List, Tuple, Dict
from models import City, Route

class GraphGenerator:
    @staticmethod
    def generate_graph(n: int, seed: int, base_sparsity: int, graph_type: str) -> Tuple[List[City], np.ndarray, float]:
        np.random.seed(seed)
        random.seed(seed)
        coords = []
        labels = []
        centers = []

        if graph_type == "Phân cụm (Clustered)":
            num_clusters = max(3, n // 10)
            centers = [ [random.uniform(20, 180), random.uniform(20, 180)] for _ in range(num_clusters) ]
            for i in range(n):
                cluster_idx = i % num_clusters
                c = centers[cluster_idx]
                x = np.clip(np.random.normal(c[0], 8), 5, 195) 
                y = np.clip(np.random.normal(c[1], 8), 5, 195)
                coords.append([x, y])
                labels.append(cluster_idx)

        elif graph_type == "Nút chai (Bottleneck)":
            for i in range(n):
                if i % 2 == 0: x = np.random.uniform(10, 40); labels.append(0)
                else: x = np.random.uniform(160, 190); labels.append(1)
                y = np.random.uniform(10, 190)
                coords.append([x, y])

        elif graph_type == "Móng ngựa (Horseshoe)":
            for i in range(n):
                angle = math.pi * (i / max(1, n - 1))
                r = 85
                x = 100 + r * math.cos(angle) + random.uniform(-2, 2)
                y = 120 - r * math.sin(angle) + random.uniform(-2, 2)
                coords.append([np.clip(x, 10, 190), np.clip(y, 10, 190)])
                labels.append(i) 

        else: # Uniform
            coords = np.random.uniform(10, 190, (n, 2)).tolist()
            labels = [0] * n

        cities = []
        for i in range(n):
            name = f"V{i}" if i >= 26 else ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T', 'U', 'V', 'W', 'X', 'Y', 'Z'][i]
            cities.append(City(i, name, coords[i][0], coords[i][1]))

        adj_matrix = np.full((n, n), float('inf'))
        for i in range(n):
            for j in range(n):
                if i != j:
                    adj_matrix[i][j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])

        # KHỞI TẠO CHU TRÌNH BẢO VỆ HAMILTON
        if graph_type == "Móng ngựa (Horseshoe)":
            path = list(range(n))
        elif graph_type == "Nút chai (Bottleneck)":
            left_nodes = [i for i in range(n) if labels[i] == 0]
            right_nodes = [i for i in range(n) if labels[i] == 1]
            left_nodes.sort(key=lambda i: coords[i][1])
            right_nodes.sort(key=lambda i: coords[i][1], reverse=True)
            path = left_nodes + right_nodes
        elif graph_type == "Phân cụm (Clustered)":
            clusters = {}
            for idx, lbl in enumerate(labels):
                clusters.setdefault(lbl, []).append(idx)
            cluster_order = sorted(clusters.keys(), key=lambda k: centers[k][0])
            path = []
            for i, lbl in enumerate(cluster_order):
                clusters[lbl].sort(key=lambda idx: coords[idx][1], reverse=(i % 2 != 0))
                path.extend(clusters[lbl])
        else: # Uniform
            cx = sum(c[0] for c in coords) / n
            cy = sum(c[1] for c in coords) / n
            path = list(range(n))
            path.sort(key=lambda i: math.atan2(coords[i][1] - cy, coords[i][0] - cx))

        protected_edges = set()
        protected_cost = 0
        for i in range(n):
            u, v = path[i], path[(i + 1) % n]
            protected_edges.add((min(u, v), max(u, v)))
            protected_cost += adj_matrix[u][v]

        # PHÂN LOẠI VÀ CẮT CẠNH THEO TỶ LỆ TRAP_PROB
        trap_candidates = []
        normal_candidates = []
        
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) in protected_edges:
                    continue
                
                is_trap = False
                if graph_type == "Nút chai (Bottleneck)" and labels[i] != labels[j]:
                    is_trap = True
                elif graph_type == "Phân cụm (Clustered)" and labels[i] != labels[j]:
                    is_trap = True
                elif graph_type == "Móng ngựa (Horseshoe)" and abs(labels[i] - labels[j]) > 4 and abs(labels[i] - labels[j]) < n - 4:
                    is_trap = True
                
                if is_trap: trap_candidates.append((i, j))
                else: normal_candidates.append((i, j))

        if graph_type == "Ngẫu nhiên (Uniform)":
            # Nếu là Uniform, cắt ngẫu nhiên trên toàn đồ thị
            random.shuffle(normal_candidates)
            num_remove = int(len(normal_candidates) * (base_sparsity / 100.0))
            for k in range(num_remove):
                u, v = normal_candidates[k]
                adj_matrix[u][v] = float('inf')
                adj_matrix[v][u] = float('inf')
        else:
            # Nếu đồ thị đặc biệt, chỉ cắt mục tiêu vào các cạnh bẫy
            random.shuffle(trap_candidates)
            num_remove = int(len(trap_candidates) * (base_sparsity / 100.0))
            for k in range(num_remove):
                u, v = trap_candidates[k]
                adj_matrix[u][v] = float('inf')
                adj_matrix[v][u] = float('inf')

        return cities, adj_matrix, protected_cost

class GreedySolver:
    @staticmethod
    def generate_route(cities: List[City], adj_matrix: np.ndarray, start_node_idx: int) -> Route:
        unvisited = list(cities)
        if start_node_idx >= len(cities):
            start_node_idx = 0
        curr = unvisited.pop(start_node_idx)
        path = [curr]

        while unvisited:
            next_node = None
            min_d = float('inf')
            for node in unvisited:
                dist = adj_matrix[curr.id][node.id]
                if dist < min_d:
                    min_d = dist
                    next_node = node

            if next_node is None: 
                next_node = unvisited[0]
            
            unvisited.remove(next_node)
            path.append(next_node)
            curr = next_node

        return Route(path, adj_matrix)

class CuckooOptimizer:
    "class CuckooOptimizer:
    def __init__(self, cities: List[City], adj_matrix: np.ndarray, pop_size: int = 20, max_gen: int = 100, pa: float = 0.25, warm_start_route: Route = None):
        self.cities = cities
        self.adj_matrix = adj_matrix
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.pa = pa
        self.population = []
        self.best_route = None
        self.convergence_generation = 0
        self.history = [] 
        self.route_history = []
        self.initialize_population()

    def initialize_population(self, warm_start_route: Route = None):
        if warm_start_route is not None and warm_start_route.is_feasible:
            self.population.append(warm_start_route)
            for _ in range(1, self.pop_size):
                mutated_list = list(warm_start_route.route)
                idx1, idx2 = random.sample(range(len(mutated_list)), 2)
                mutated_list[idx1], mutated_list[idx2] = mutated_list[idx2], mutated_list[idx1]
                self.population.append(Route(mutated_list, self.adj_matrix))
        else:
            for _ in range(self.pop_size):
                random_list = list(self.cities)
                random.shuffle(random_list)
                self.population.append(Route(random_list, self.adj_matrix))

        self.best_route = min(self.population, key=lambda x: x.fitness)
        self.history.append(self.best_route.fitness)
        self.route_history.append(self.best_route)"

    def initialize_population(self, warm_start_route: Route = None):
        if warm_start_route is not None and warm_start_route.is_feasible:
            self.population.append(warm_start_route)
            for _ in range(1, self.pop_size):
                mutated_list = list(warm_start_route.route)
                idx1, idx2 = random.sample(range(len(mutated_list)), 2)
                mutated_list[idx1], mutated_list[idx2] = mutated_list[idx2], mutated_list[idx1]
                self.population.append(Route(mutated_list, self.adj_matrix))
        else:
            for _ in range(self.pop_size):
                random_list = list(self.cities)
                random.shuffle(random_list)
                self.population.append(Route(random_list, self.adj_matrix))

        self.best_route = min(self.population, key=lambda x: x.fitness)
        self.history.append(self.best_route.fitness)
        self.route_history.append(self.best_route)"

    def discrete_levy_flight(self, current_route: Route) -> Route:
        beta = 1.5
        sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
        u = np.random.normal(0, sigma)
        v = np.random.normal(0, 1)
        step = u / (abs(v) ** (1 / beta))
        k = max(1, int(abs(step) * 3))

        new_list = list(current_route.route)
        for _ in range(k):
            if len(new_list) < 2: break
            idx1, idx2 = random.sample(range(len(new_list)), 2)
            new_list[idx1], new_list[idx2] = new_list[idx2], new_list[idx1]

        return Route(new_list, self.adj_matrix)

    def next_generation(self) -> Tuple[Route, bool]:
        i = random.randint(0, self.pop_size - 1)
        new_nest = self.discrete_levy_flight(self.population[i])
        j = random.randint(0, self.pop_size - 1)

        if new_nest.fitness < self.population[j].fitness:
            self.population[j] = new_nest

        self.population.sort(key=lambda x: x.fitness)

        for k in range(int(self.pop_size * (1 - self.pa)), self.pop_size):
            self.population[k] = self.discrete_levy_flight(self.population[0])

        current_best = min(self.population, key=lambda x: x.fitness)
        is_updated = False

        if current_best.fitness < self.best_route.fitness:
            self.best_route = current_best
            is_updated = True
            
        self.history.append(self.best_route.fitness)
        self.route_history.append(self.best_route)
        return self.best_route, is_updated

class MetricsEvaluator:
    @staticmethod
    def _calculate_stats(results: List[float], times: List[float]) -> Dict:
        feasible_results = [r for r in results if r != float('inf')]
        return {
            'results': results,
            'best_cost': min(results) if results else float('inf'),
            'worst_cost': max(feasible_results) if feasible_results else float('inf'),
            'avg_cost': statistics.mean(feasible_results) if feasible_results else float('inf'),
            'std_dev': statistics.stdev(feasible_results) if len(feasible_results) > 1 else 0,
            'execution_times': times,
            'avg_execution_time': statistics.mean(times) if times else 0,
            'feasibility_rate': len(feasible_results) / len(results) if results else 0
        }

    @staticmethod
    def evaluate_gbfs_stability(cities: List[City], adj_matrix: np.ndarray, num_runs: int = 10, start_node: int = 0) -> Tuple[Dict, Route, List[Route], List[float]]:
        results, times = [], []
        best_route = None
        
        for _ in range(num_runs):
            start_time = time.perf_counter()
            route = GreedySolver.generate_route(cities, adj_matrix, start_node)
            exec_time = (time.perf_counter() - start_time) * 1000
            results.append(route.fitness)
            times.append(exec_time)
            if best_route is None or route.fitness < best_route.fitness:
                best_route = route

        stats = MetricsEvaluator._calculate_stats(results, times)
        stats['algorithm'] = 'GBFS'
        stats['num_runs'] = num_runs
        stats['is_deterministic'] = len(set(results)) == 1
        dummy_history = [best_route.fitness] * 101
        return stats, best_route, [best_route], dummy_history

    @staticmethod
    def evaluate_cuckoo_stability(cities: List[City], adj_matrix: np.ndarray, pop_size: int = 20, max_gen: int = 100, pa: float = 0.25, num_runs: int = 20, start_node: int = 0) -> Tuple[Dict, Route, List[Route], List[float]]:
        results, times, convergence_gens = [], [], []
        best_route = None
        best_route_history = []
        best_cost_history = []
        
        for _ in range(num_runs):
            start_time = time.perf_counter()
            gbfs_route = GreedySolver.generate_route(cities, adj_matrix, start_node)
            optimizer = CuckooOptimizer(cities, adj_matrix, pop_size, max_gen, pa, gbfs_route)

            for gen in range(max_gen):
                best, updated = optimizer.next_generation()
                if updated:
                    optimizer.convergence_generation = gen

            exec_time = (time.perf_counter() - start_time) * 1000
            results.append(optimizer.best_route.fitness)
            times.append(exec_time)
            convergence_gens.append(optimizer.convergence_generation)
            
            if best_route is None or optimizer.best_route.fitness < best_route.fitness:
                best_route = optimizer.best_route
                best_route_history = optimizer.route_history
                best_cost_history = optimizer.history

        stats = MetricsEvaluator._calculate_stats(results, times)
        stats['algorithm'] = 'Cuckoo'
        stats['num_runs'] = num_runs
        stats['convergence_gens'] = convergence_gens
        stats['avg_convergence_gen'] = statistics.mean(convergence_gens) if convergence_gens else 0
        return stats, best_route, best_route_history, best_cost_history

class GBFSAnalyzer:
    @staticmethod
    def run_scenario_1_starting_points(n: int, seed: int, sparsity: int, graph_type: str) -> Dict:
        cities, adj_matrix, _ = GraphGenerator.generate_graph(n, seed, sparsity, graph_type)
        results = []
        valid_routes = 0
        for start_idx in range(n):
            route = GreedySolver.generate_route(cities, adj_matrix, start_idx)
            if route.is_feasible:
                results.append(route.fitness)
                valid_routes += 1
            else:
                results.append(float('inf'))
        
        feasible_results = [r for r in results if r != float('inf')]
        return {
            'costs': feasible_results, 'nodes': [i for i, r in enumerate(results) if r != float('inf')],
            'min': min(feasible_results) if feasible_results else float('inf'),
            'max': max(feasible_results) if feasible_results else float('inf'),
            'mean': statistics.mean(feasible_results) if feasible_results else float('inf'),
            'std': statistics.stdev(feasible_results) if len(feasible_results) > 1 else 0,
            'feasibility_rate': valid_routes / n if n > 0 else 0,
            'cities': cities, 'adj_matrix': adj_matrix # Trả về để vẽ đồ thị
        }

    @staticmethod
    def run_scenario_2_sparsity_tolerance(n: int, seed: int, graph_type: str) -> Dict:
        sparsity_levels = list(range(0, 95, 5)) 
        feasibility_rates = []
        
        for sp in sparsity_levels:
            cities, adj_matrix, _ = GraphGenerator.generate_graph(n, seed, sp, graph_type)
            valid_routes = sum(1 for i in range(n) if GreedySolver.generate_route(cities, adj_matrix, i).is_feasible)
            feasibility_rates.append((valid_routes / n) * 100)
            
        # Sinh 1 graph mẫu ở mức Sparsity 50% để hiển thị trực quan UI
        sample_cities, sample_adj, _ = GraphGenerator.generate_graph(n, seed, 50, graph_type)
        return {'sparsity_levels': sparsity_levels, 'feasibility_rates': feasibility_rates, 'cities': sample_cities, 'adj_matrix': sample_adj}

    @staticmethod
    def run_scenario_3_scalability(seed: int) -> Dict:
        n_values = [10, 50, 100, 200, 500, 800, 1000]
        execution_times = []
        for n in n_values:
            cities, adj_matrix, _ = GraphGenerator.generate_graph(n, seed, 0, "Ngẫu nhiên (Uniform)")
            times = []
            for _ in range(3): 
                start_time = time.perf_counter()
                GreedySolver.generate_route(cities, adj_matrix, 0)
                times.append((time.perf_counter() - start_time) * 1000)
            execution_times.append(statistics.mean(times))
            
        sample_cities, sample_adj, _ = GraphGenerator.generate_graph(100, seed, 0, "Ngẫu nhiên (Uniform)")
        return {'n_values': n_values, 'execution_times': execution_times, 'cities': sample_cities, 'adj_matrix': sample_adj}
