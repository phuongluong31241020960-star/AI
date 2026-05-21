# import csv
# import math
# import random

# # Tọa độ 20 đỉnh từ Vertex.csv đã cung cấp trước đó
# vertices = [
#     (0, 12, 34), (1, 85, 22), (2, 56, 78), (3, 90, 10), (4, 5, 95),
#     (5, 45, 45), (6, 73, 60), (7, 20, 80), (8, 33, 15), (9, 60, 5),
#     (10, 88, 88), (11, 15, 50), (12, 50, 90), (13, 75, 30), (14, 10, 10),
#     (15, 95, 50), (16, 40, 70), (17, 25, 25), (18, 65, 20), (19, 5, 70)
# ]

# def calculate_distance(v1, v2, mode="standard"):
#     """
#     Tính trọng số cạnh giữa 2 đỉnh
#     mode: "standard" (Euclid), "asymmetric" (bất đối xứng), "sparse" (thiếu cạnh)
#     """
#     dist = math.sqrt((v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    
#     if mode == "asymmetric":
#         # Làm trọng số đi và về khác nhau một chút (sai lệch 10-30%)
#         return round(dist * random.uniform(0.7, 1.3), 2)
    
#     return round(dist, 2)

# def generate_edge_file(filename, mode="standard", sparsity=0.0):
#     """
#     Tạo file CSV chứa danh sách cạnh
#     sparsity: tỉ lệ cạnh bị xóa (0.0 đến 1.0)
#     """
#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["index_1", "index_2", "weight"])
        
#         edge_count = 0
#         for i in range(len(vertices)):
#             for j in range(len(vertices)):
#                 if i == j: continue # Không tự nối chính mình
                
#                 # Quyết định xem có giữ cạnh này không (cho trường hợp Sparse)
#                 if random.random() < sparsity:
#                     continue 
                
#                 v1 = vertices[i]
#                 v2 = vertices[j]
#                 weight = calculate_distance(v1, v2, mode)
                
#                 writer.writerow([v1[0], v2[0], weight])
#                 edge_count += 1
                
#     print(f"Đã tạo file {filename} thành công với {edge_count} cạnh!")

# # --- CHẠY THỬ CÁC TRƯỜNG HỢP ---

# # 1. Đồ thị đầy đủ chuẩn (Symmetric)
# generate_edge_file("Edge_Full.csv", mode="standard")

# # 2. Đồ thị bất đối xứng (Asymmetric)
# generate_edge_file("Edge_Asymmetric.csv", mode="asymmetric")

# # 3. Đồ thị thiếu cạnh (Sparse - Xóa 30% số cạnh)
# generate_edge_file("Edge_Sparse.csv", mode="standard", sparsity=0.3)

import random
import math
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QComboBox
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QTimer
import sys
import time

# 1. Class City
class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.screen_x = 0
        self.screen_y = 0

# 2. Class Route
class Route:
    def __init__(self, route_list, adj_matrix):
        self.route = route_list
        self.adj_matrix = adj_matrix
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        total_dist = 0
        for i in range(len(self.route)):
            u = self.route[i].id
            v = self.route[(i + 1) % len(self.route)].id
            weight = self.adj_matrix[u][v]
            if weight == float('inf'):
                return float('inf')
            total_dist += weight
        return total_dist

# 3. Class GreedySolver
class GreedySolver:
    @staticmethod
    def generate_route(cities, adj_matrix, start_node_idx):
        unvisited = list(cities)
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
            if next_node is None: next_node = unvisited[0]
            unvisited.remove(next_node)
            path.append(next_node)
            curr = next_node
        return Route(path, adj_matrix)

# 4. Class CuckooOptimizer
class CuckooOptimizer:
    def __init__(self, cities, adj_matrix, pop_size, pa):
        self.cities = cities
        self.adj_matrix = adj_matrix
        self.pop_size = pop_size
        self.pa = pa
        self.population = []
        self.best_route = None
        self.init_population()

    def init_population(self):
        # Store initial greedy fitness for comparison
        greedy_routes = []
        for i in range(self.pop_size):
            start_idx = i % len(self.cities)
            greedy_routes.append(GreedySolver.generate_route(self.cities, self.adj_matrix, start_idx))
        self.population = greedy_routes
        self.best_route = min(self.population, key=lambda x: x.fitness)
        # Return the best fitness found during initialization (greedy best)
        return self.best_route.fitness

    def discrete_levy_flight(self, current_route):
        beta = 1.5
        sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) / (math.gamma((1 + beta) / 2) * beta * 2**((beta - 1) / 2)))**(1 / beta)
        u = np.random.normal(0, sigma)
        v = np.random.normal(0, 1)
        step = u / (abs(v)**(1 / beta))
        k = max(1, int(abs(step) * 3))
        new_list = list(current_route.route)
        for _ in range(k):
            idx1, idx2 = random.sample(range(len(new_list)), 2)
            new_list[idx1], new_list[idx2] = new_list[idx2], new_list[idx1]
        return Route(new_list, self.adj_matrix)

    def next_generation(self):
        i = random.randint(0, self.pop_size - 1)
        new_nest = self.discrete_levy_flight(self.population[i])
        j = random.randint(0, self.pop_size - 1)
        if new_nest.fitness < self.population[j].fitness: self.population[j] = new_nest
        self.population.sort(key=lambda x: x.fitness)
        for k in range(int(self.pop_size * (1 - self.pa)), self.pop_size):
            self.population[k] = self.discrete_levy_flight(self.population[0])
        current_best = min(self.population, key=lambda x: x.fitness)
        if current_best.fitness < self.best_route.fitness: 
            self.best_route = current_best
            return self.best_route, True # Indicate that best route was updated
        return self.best_route, False # Indicate no update

# Data loading function
def load_graph_data(edge_file): # Renamed and made a function
    v_df = pd.read_csv('Vertex.csv')
    e_df = pd.read_csv(edge_file)
    v_df.columns = v_df.columns.str.strip()
    e_df.columns = e_df.columns.str.strip()

    cities_data = [City(int(row['index']), row['x'], row['y']) for _, row in v_df.iterrows()]
    num_nodes = len(cities_data)
    adj_matrix_data = [[float('inf')] * num_nodes for _ in range(num_nodes)]
    for _, row in e_df.iterrows():
        u, v, w = int(row['index_1']), int(row['index_2']), float(row['weight'])
        if u < num_nodes and v < num_nodes: adj_matrix_data[u][v] = adj_matrix_data[v][u] = w

    # --- Auto Scaling and Centering for PyQt ---
    min_x = min(c.x for c in cities_data)
    max_x = max(c.x for c in cities_data)
    min_y = min(c.y for c in cities_data)
    max_y = max(c.y for c in cities_data)

    range_x = max_x - min_x if max_x != min_x else 1
    range_y = max_y - min_y if max_y != min_y else 1

    padding = 50
    draw_width = 800 - 2 * padding
    draw_height = 600 - 2 * padding

    scale = min(draw_width / range_x, draw_height / range_y)

    for c in cities_data:
        c.screen_x = int((c.x - min_x) * scale + padding)
        c.screen_y = int((c.y - min_y) * scale + padding)
    
    return cities_data, adj_matrix_data

# Initial load of graph data
cities_data, adj_matrix_data = load_graph_data('Edge_Full.csv')

class GraphWidget(QWidget):
    def __init__(self, cities, adj_matrix):
        super().__init__()
        self.cities = cities
        self.adj_matrix = adj_matrix
        self.best_route = None
        self.setMinimumSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw graph base (edges)
        painter.setPen(QPen(QColor(70, 70, 70), 1))
        for i in range(len(self.cities)):
            for j in range(i + 1, len(self.cities)):
                if self.adj_matrix[i][j] != float('inf'):
                    p1_x, p1_y = self.cities[i].screen_x, self.cities[i].screen_y
                    p2_x, p2_y = self.cities[j].screen_x, self.cities[j].screen_y
                    painter.drawLine(p1_x, p1_y, p2_x, p2_y)
        
        # Draw cities
        painter.setBrush(QColor(150, 150, 150))
        for c in self.cities:
            painter.drawEllipse(c.screen_x - 5, c.screen_y - 5, 10, 10)
            # Optionally draw city IDs
            painter.setPen(QColor(200, 200, 200))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(c.screen_x + 7, c.screen_y + 3, str(c.id))

        # Draw best route
        if self.best_route:
            painter.setPen(QPen(QColor(255, 0, 0), 3))
            for i in range(len(self.best_route.route)):
                c1 = self.best_route.route[i]
                c2 = self.best_route.route[(i + 1) % len(self.best_route.route)]
                painter.drawLine(c1.screen_x, c1.screen_y, c2.screen_x, c2.screen_y)

class MainWindow(QMainWindow):
    def __init__(self, cities, adj_matrix):
        super().__init__()
        # self.cities and self.adj_matrix will be set by loadGraphConfig
        self.optimizer = None
        self.gen = 0
        self.max_generations = 500 # Default max generations
        self.state = "START"
        self.initial_greedy_fitness = float('inf') # Store initial greedy fitness
        self.cuckoo_execution_time = 0
        self.greedy_execution_time = 0
        self.convergence_generation = 0

        self.initUI()
        self.loadGraphConfig('Edge_Full.csv') # Initial load
        self.initOptimizer()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)

    def initUI(self):
        self.setWindowTitle('Cuckoo Search TSP (PyQt6)')
        self.setGeometry(100, 100, 1000, 600) # Main window size

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Graph Visualization Area
        self.graph_widget = GraphWidget(self.cities if hasattr(self, 'cities') else [], self.adj_matrix if hasattr(self, 'adj_matrix') else [])
        main_layout.addWidget(self.graph_widget)

        # UI Control Area
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel("<b style='color: gold;'>CONFIGURATIONS</b>")
        self.title_label.setFont(QFont("Arial", 14))
        control_layout.addWidget(self.title_label)
        
        control_layout.addSpacing(20)

        # Graph Selection
        self.graph_selection_label = QLabel("Select Graph:")
        self.graph_combo_box = QComboBox()
        self.graph_combo_box.addItem("Edge_Full.csv", 'Edge_Full.csv')
        self.graph_combo_box.addItem("Edge_Asymmetric.csv", 'Edge_Asymmetric.csv')
        self.graph_combo_box.addItem("Edge_Sparse.csv", 'Edge_Sparse.csv')
        self.graph_combo_box.currentIndexChanged.connect(self.onGraphSelected)
        control_layout.addWidget(self.graph_selection_label)
        control_layout.addWidget(self.graph_combo_box)

        control_layout.addSpacing(20)

        self.pop_size_label = QLabel("Pop Size:")
        self.pop_size_spinbox = QSpinBox()
        self.pop_size_spinbox.setRange(2, 100)
        self.pop_size_spinbox.setValue(20)
        self.pop_size_spinbox.valueChanged.connect(self.updateOptimizerParams)
        control_layout.addWidget(self.pop_size_label)
        control_layout.addWidget(self.pop_size_spinbox)

        self.pa_label = QLabel("Pa:")
        self.pa_spinbox = QDoubleSpinBox()
        self.pa_spinbox.setRange(0.0, 1.0)
        self.pa_spinbox.setSingleStep(0.05)
        self.pa_spinbox.setValue(0.25)
        self.pa_spinbox.valueChanged.connect(self.updateOptimizerParams)
        control_layout.addWidget(self.pa_label)
        control_layout.addWidget(self.pa_spinbox)
        
        self.max_gen_label = QLabel("Max Generations:")
        self.max_gen_spinbox = QSpinBox()
        self.max_gen_spinbox.setRange(10, 5000)
        self.max_gen_spinbox.setSingleStep(10)
        self.max_gen_spinbox.setValue(self.max_generations)
        self.max_gen_spinbox.valueChanged.connect(self.updateMaxGenerations)
        control_layout.addWidget(self.max_gen_label)
        control_layout.addWidget(self.max_gen_spinbox)

        control_layout.addSpacing(30)

        self.start_button = QPushButton("Start Algorithm")
        self.start_button.clicked.connect(self.startSimulation)
        control_layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.resetSimulation)
        self.reset_button.setEnabled(False)
        control_layout.addWidget(self.reset_button)

        control_layout.addStretch(1)

        self.generation_label = QLabel("Gen: 0")
        self.generation_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.generation_label)

        self.fitness_label = QLabel("Fitness: N/A")
        self.fitness_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.fitness_label)

        # New labels for performance metrics
        self.improvement_rate_label = QLabel("Improvement: N/A")
        self.improvement_rate_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.improvement_rate_label)

        self.execution_time_label = QLabel("Exec Time (Cuckoo): N/A")
        self.execution_time_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.execution_time_label)

        self.greedy_time_label = QLabel("Exec Time (Greedy): N/A")
        self.greedy_time_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.greedy_time_label)

        self.convergence_gen_label = QLabel("Convergence Gen: N/A")
        self.convergence_gen_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.convergence_gen_label)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.status_label)

        main_layout.addLayout(control_layout)
    
    def loadGraphConfig(self, edge_file_path):
        self.cities, self.adj_matrix = load_graph_data(edge_file_path)
        # Update graph_widget with new data
        self.graph_widget.cities = self.cities
        self.graph_widget.adj_matrix = self.adj_matrix
        self.graph_widget.best_route = None # Clear previous route
        self.graph_widget.update()

    def onGraphSelected(self, index):
        if self.state == "START": # Only allow changes in START state
            selected_edge_file = self.graph_combo_box.itemData(index)
            self.loadGraphConfig(selected_edge_file)
            self.initOptimizer() # Re-initialize optimizer with new graph

    def initOptimizer(self):
        pop_size = self.pop_size_spinbox.value()
        pa = self.pa_spinbox.value()

        # Measure Greedy initialization time
        start_greedy_time = time.perf_counter()
        self.optimizer = CuckooOptimizer(self.cities, self.adj_matrix, pop_size, pa)
        self.initial_greedy_fitness = self.optimizer.best_route.fitness if self.optimizer and self.optimizer.best_route else float('inf')
        end_greedy_time = time.perf_counter()
        self.greedy_execution_time = (end_greedy_time - start_greedy_time) * 1000 # in milliseconds

        if self.optimizer.best_route: # Check if best_route exists after init
            self.graph_widget.best_route = self.optimizer.best_route
            self.fitness_label.setText(f"Fitness: {self.optimizer.best_route.fitness:.1f}")
        else:
            self.graph_widget.best_route = None
            self.fitness_label.setText("Fitness: N/A")
        
        # Reset performance metrics when optimizer is re-initialized
        self.improvement_rate_label.setText("Improvement: N/A")
        self.execution_time_label.setText("Exec Time (Cuckoo): N/A")
        self.greedy_time_label.setText(f"Exec Time (Greedy): {self.greedy_execution_time:.2f} ms")
        self.convergence_gen_label.setText("Convergence Gen: N/A")
        self.convergence_generation = 0

        self.graph_widget.update()

    def updateOptimizerParams(self):
        if self.state == "START": # Only allow changes in START state
            self.initOptimizer()

    def updateMaxGenerations(self, value):
        self.max_generations = value

    def startSimulation(self):
        if self.state == "START" or self.state == "FINISHED":
            self.state = "RUNNING"
            self.gen = 0
            # Re-initialize optimizer if starting new run or re-running after finish
            self.initOptimizer()
            self.cuckoo_start_time = time.perf_counter() # Record start time for Cuckoo optimization
            self.timer.start(30) # 30 ms for simulation step
            self.start_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.pop_size_spinbox.setEnabled(False)
            self.pa_spinbox.setEnabled(False)
            self.max_gen_spinbox.setEnabled(False)
            self.graph_combo_box.setEnabled(False)
            self.status_label.setText("Status: Running...")
            self.status_label.setStyleSheet("color: yellow;")

    def resetSimulation(self):
        self.timer.stop()
        self.state = "START"
        self.gen = 0
        # Reload initial graph configuration and re-initialize optimizer
        self.loadGraphConfig(self.graph_combo_box.itemData(self.graph_combo_box.currentIndex()))
        self.initOptimizer()
        self.generation_label.setText("Gen: 0")
        self.fitness_label.setText(f"Fitness: {self.optimizer.best_route.fitness:.1f}" if self.optimizer and self.optimizer.best_route else "Fitness: N/A")
        self.start_button.setText("Start Algorithm")
        self.start_button.setEnabled(True)
        self.reset_button.setEnabled(False)
        self.pop_size_spinbox.setEnabled(True)
        self.pa_spinbox.setEnabled(True)
        self.max_gen_spinbox.setEnabled(True)
        self.graph_combo_box.setEnabled(True)
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("color: white;")
        
        # Reset new metrics
        self.improvement_rate_label.setText("Improvement: N/A")
        self.execution_time_label.setText("Exec Time (Cuckoo): N/A")
        self.greedy_time_label.setText("Exec Time (Greedy): N/A")
        self.convergence_gen_label.setText("Convergence Gen: N/A")
        self.convergence_generation = 0
        self.cuckoo_execution_time = 0
        self.initial_greedy_fitness = float('inf')

        self.graph_widget.best_route = None
        self.graph_widget.update()

    def update_simulation(self):
        if self.state == "RUNNING":
            if self.gen < self.max_generations:
                best, updated = self.optimizer.next_generation()
                if updated:
                    self.convergence_generation = self.gen # Update convergence generation
                self.graph_widget.best_route = best
                self.generation_label.setText(f"Gen: {self.gen}")
                self.fitness_label.setText(f"Fitness: {best.fitness:.1f}")
                self.graph_widget.update() # Trigger repaint
                self.gen += 1
            else:
                self.timer.stop()
                self.state = "FINISHED"
                self.cuckoo_execution_time = (time.perf_counter() - self.cuckoo_start_time) * 1000 # in milliseconds

                # Calculate Improvement Rate
                improvement_rate = 0.0
                if self.initial_greedy_fitness != float('inf') and self.initial_greedy_fitness != 0:
                    improvement_rate = ((self.initial_greedy_fitness - self.optimizer.best_route.fitness) / self.initial_greedy_fitness) * 100

                self.status_label.setText(f"Status: Finished! Best Fitness: {self.optimizer.best_route.fitness:.1f}")
                self.status_label.setStyleSheet("color: lime;")
                self.start_button.setText("Run Again")
                self.start_button.setEnabled(True)
                self.graph_combo_box.setEnabled(True) # Allow changing graph after finish

                # Display new metrics
                self.improvement_rate_label.setText(f"Improvement: {improvement_rate:.2f}%")
                self.execution_time_label.setText(f"Exec Time (Cuckoo): {self.cuckoo_execution_time:.2f} ms")
                self.convergence_gen_label.setText(f"Convergence Gen: {self.convergence_generation}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(cities_data, adj_matrix_data)
    window.show()
    sys.exit(app.exec())