# import os
import math
import pandas as pd
import numpy as np
from typing import List, Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QTextEdit, QGroupBox, QGridLayout, 
                             QApplication, QRadioButton, QButtonGroup, QTabWidget)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPolygon
from PyQt6.QtCore import QPoint, QTimer

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models import City, Route
from algorithms import MetricsEvaluator, GraphGenerator, GBFSAnalyzer

class GraphWidget(QWidget):
    def __init__(self, cities: List[City], adj_matrix: np.ndarray = None):
        super().__init__()
        self.cities = cities
        self.adj_matrix = adj_matrix
        self.route = None
        self.start_node_name = None
        self.overlay_text = ""
        self.setMinimumSize(550, 550)

    def set_data(self, cities: List[City], adj_matrix: np.ndarray, route: Optional[Route] = None, start_node_name: str = None, overlay_text: str = ""):
        self.cities = cities
        self.adj_matrix = adj_matrix
        self.route = route
        self.start_node_name = start_node_name
        self.overlay_text = overlay_text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = 40
        
        if not self.cities: return
            
        max_x = max(c.x for c in self.cities)
        max_y = max(c.y for c in self.cities)
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        scale_x = width / max_x if max_x > 0 else 1
        scale_y = height / max_y if max_y > 0 else 1

        # Nền đồ thị
        if self.adj_matrix is not None and len(self.cities) <= 50:
            bg_pen = QPen(QColor(130, 130, 130, 40), 1)
            painter.setPen(bg_pen)
            for i in range(len(self.cities)):
                for j in range(len(self.cities)):
                    if i != j and self.adj_matrix[i][j] != float('inf'):
                        x1 = margin + self.cities[i].x * scale_x
                        y1 = margin + self.cities[i].y * scale_y
                        x2 = margin + self.cities[j].x * scale_x
                        y2 = margin + self.cities[j].y * scale_y
                        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Vẽ Tuyến đường
        if self.route and self.route.is_feasible:
            display_route = self.route.get_rotated_cities(self.start_node_name)
            for i in range(len(display_route)):
                curr = display_route[i]
                next_city = display_route[(i + 1) % len(display_route)]
                x1, y1 = margin + curr.x * scale_x, margin + curr.y * scale_y
                x2, y2 = margin + next_city.x * scale_x, margin + next_city.y * scale_y
                
                if curr.name == self.start_node_name:
                    painter.setPen(QPen(QColor(255, 0, 0), 4)) 
                else:
                    painter.setPen(QPen(QColor(0, 150, 255), 2))
                
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 15:
                    mx, my = x1 + dx * 0.5, y1 + dy * 0.5
                    angle = math.atan2(dy, dx)
                    arrow_size = 9 if curr.name == self.start_node_name else 7
                    arrow_color = QColor(255, 0, 0) if curr.name == self.start_node_name else QColor(255, 69, 0)
                    
                    painter.setBrush(QBrush(arrow_color)) 
                    painter.setPen(QPen(arrow_color, 1))
                    p1_x = mx - arrow_size * math.cos(angle - math.pi/6)
                    p1_y = my - arrow_size * math.sin(angle - math.pi/6)
                    p2_x = mx - arrow_size * math.cos(angle + math.pi/6)
                    p2_y = my - arrow_size * math.sin(angle + math.pi/6)
                    
                    poly = QPolygon([QPoint(int(mx), int(my)), QPoint(int(p1_x), int(p1_y)), QPoint(int(p2_x), int(p2_y))])
                    painter.drawPolygon(poly)

        # Nút Trạm
        for city in self.cities:
            x, y = margin + city.x * scale_x, margin + city.y * scale_y
            is_start = (city.name == self.start_node_name)
            
            painter.setBrush(QBrush(QColor(255, 200, 50) if is_start else QColor(50, 200, 50)))
            painter.setPen(QPen(QColor(0, 0, 0), 2 if is_start else 1))
            r_size = 10 if is_start else (5 if len(self.cities) > 20 else 11)
            painter.drawEllipse(int(x - r_size), int(y - r_size), r_size*2, r_size*2)
            
            if len(self.cities) <= 30 or is_start:
                painter.setPen(QColor(255, 255, 255) if self.palette().window().color().value() < 128 else QColor(0, 0, 0))
                painter.setFont(QFont('Arial', 9, QFont.Weight.Bold))
                painter.drawText(int(x - 5), int(y + 4), city.name)

        if self.overlay_text:
            font = QFont('Arial', 11, QFont.Weight.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(self.overlay_text)
            painter.setBrush(QBrush(QColor(255, 255, 255, 220))) 
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawRoundedRect(15, 15, text_width + 20, fm.height() + 10, 5, 5)
            painter.setPen(QColor(200, 40, 40)) 
            painter.drawText(25, 15 + fm.height() - 2, self.overlay_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSP Project Analyzer - PHÂN TÍCH CHUYÊN SÂU GBFS")
        self.setGeometry(50, 50, 1550, 880)
        
        self.cities, self.adj_matrix = [], None
        
        self.gbfs_results = None;  self.gbfs_route = None;  self.gbfs_cost_history = []
        self.cuckoo_results = None; self.cuckoo_route = None; self.cuckoo_cost_history = []
        
        self.gbfs_history_frames = []
        self.cuckoo_history_frames = []
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_next_frame)
        self.animation_frames = []
        self.animation_idx = 0
        self.last_animated_cost = float('inf')
        self.improvement_count = 0
        
        self.init_ui()
        self.generate_new_graph() # Khởi tạo đồ thị mặc định lúc mở app

    def init_ui(self):
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # ==================== TAB 1: MÔ PHỎNG MẠNG LƯỚI ====================
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        
        left_panel = QVBoxLayout()
        
        # Khối: Bộ Sinh Đồ Thị Tùy Chỉnh
        graph_group = QGroupBox("Bộ Sinh Đồ Thị (Tình Huống Thực Nghiệm)")
        graph_layout = QGridLayout()
        
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(['Ngẫu nhiên (Uniform)', 'Phân cụm (Clustered)', 'Nút chai (Bottleneck)', 'Móng ngựa (Horseshoe)'])
        
        self.node_spin = QSpinBox()
        self.node_spin.setRange(10, 500); self.node_spin.setValue(20)
        
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 9999); self.seed_spin.setValue(42)
        
        self.sparsity_spin = QSpinBox()
        self.sparsity_spin.setRange(0, 90); self.sparsity_spin.setValue(0); self.sparsity_spin.setSuffix("%")
        
        self.btn_generate = QPushButton("Tạo Mới Đồ Thị")
        self.btn_generate.setStyleSheet("background-color: #005A9C; color: white; font-weight: bold;")
        self.btn_generate.clicked.connect(self.generate_new_graph)

        graph_layout.addWidget(QLabel("Loại Phân Bố:"), 0, 0); graph_layout.addWidget(self.graph_type_combo, 0, 1)
        graph_layout.addWidget(QLabel("Số Lượng Đỉnh (N):"), 1, 0); graph_layout.addWidget(self.node_spin, 1, 1)
        graph_layout.addWidget(QLabel("Seed Cố Định:"), 2, 0); graph_layout.addWidget(self.seed_spin, 2, 1)
        graph_layout.addWidget(QLabel("Tỷ Lệ Khuyết Cạnh:"), 3, 0); graph_layout.addWidget(self.sparsity_spin, 3, 1)
        graph_layout.addWidget(self.btn_generate, 4, 0, 1, 2)
        
        graph_group.setLayout(graph_layout)
        left_panel.addWidget(graph_group)

        # Chỗ Chọn Điểm Bắt Đầu cho Mô Phỏng
        start_group = QGroupBox("Cấu hình Điểm Xuất Phát")
        start_layout = QVBoxLayout()
        self.start_node_combo = QComboBox()
        start_layout.addWidget(self.start_node_combo)
        start_group.setLayout(start_layout)
        left_panel.addWidget(start_group)

        param_group = QGroupBox("Tham số Cuckoo Search (Đối chiếu)")
        param_layout = QGridLayout()
        self.pop_size_spin = QSpinBox(); self.pop_size_spin.setMaximum(1000); self.pop_size_spin.setValue(20)
        self.max_gen_spin = QSpinBox(); self.max_gen_spin.setMaximum(5000); self.max_gen_spin.setValue(100)
        self.pa_spin = QDoubleSpinBox(); self.pa_spin.setSingleStep(0.01); self.pa_spin.setValue(0.25)
        self.run_count_spin = QSpinBox(); self.run_count_spin.setMaximum(500); self.run_count_spin.setValue(20)
        param_layout.addWidget(QLabel("Quần thể (Nests):"), 0, 0); param_layout.addWidget(self.pop_size_spin, 0, 1)
        param_layout.addWidget(QLabel("Vòng lặp (Max Gen):"), 1, 0); param_layout.addWidget(self.max_gen_spin, 1, 1)
        param_layout.addWidget(QLabel("Tỷ lệ Pa:"), 2, 0); param_layout.addWidget(self.pa_spin, 2, 1)
        param_layout.addWidget(QLabel("Số lượt chạy Test:"), 3, 0); param_layout.addWidget(self.run_count_spin, 3, 1)
        param_group.setLayout(param_layout)
        left_panel.addWidget(param_group)

        button_group = QGroupBox("Mô Phỏng Trực Quan")
        button_layout = QVBoxLayout()
        self.test_gbfs_btn = QPushButton("Chạy Đơn Tuyến: GBFS")
        self.test_gbfs_btn.setStyleSheet("background-color: #2b5c8f; color: white; padding: 5px; font-weight: bold;")
        self.test_gbfs_btn.clicked.connect(self.test_gbfs)
        self.test_cuckoo_btn = QPushButton("Chạy Đối Chiếu: Cuckoo Search")
        self.test_cuckoo_btn.setStyleSheet("background-color: #8f2b2b; color: white; padding: 5px; font-weight: bold;")
        self.test_cuckoo_btn.clicked.connect(self.test_cuckoo)
        self.compare_btn = QPushButton("So Sánh Nhanh Kết Quả")
        self.compare_btn.setStyleSheet("background-color: #2b8f3d; color: white; padding: 7px; font-weight: bold;")
        self.compare_btn.clicked.connect(self.compare_results)
        button_layout.addWidget(self.test_gbfs_btn); button_layout.addWidget(self.test_cuckoo_btn); button_layout.addWidget(self.compare_btn)
        button_group.setLayout(button_layout)
        left_panel.addWidget(button_group)
        left_panel.addStretch()

        mid_panel = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont('Consolas', 10))
        mid_panel.addWidget(QLabel("<b>Log Hệ Thống:</b>"))
        mid_panel.addWidget(self.result_text)

        right_panel = QVBoxLayout()
        view_select_group = QGroupBox("Chế độ Xem Lại Tuyến Lộ Trình")
        view_select_layout = QHBoxLayout()
        
        self.radio_gbfs = QRadioButton("Đường GBFS"); self.radio_gbfs.toggled.connect(self.switch_route_view)
        self.radio_cuckoo = QRadioButton("Đường Cuckoo"); self.radio_cuckoo.toggled.connect(self.switch_route_view)
        
        self.replay_btn = QPushButton("▶ Phát Hoạt Ảnh Tiến Hóa")
        self.replay_btn.setStyleSheet("background-color: #ff8c00; color: white; font-weight: bold;")
        self.replay_btn.clicked.connect(self.start_animation)
        self.replay_btn.setEnabled(False)
        self.radio_gbfs.setChecked(True)
        
        self.view_group = QButtonGroup()
        self.view_group.addButton(self.radio_gbfs); self.view_group.addButton(self.radio_cuckoo)
        view_select_layout.addWidget(self.radio_gbfs); view_select_layout.addWidget(self.radio_cuckoo); view_select_layout.addWidget(self.replay_btn)
        view_select_group.setLayout(view_select_layout)
        right_panel.addWidget(view_select_group)

        graph_group_box = QGroupBox("Bản Đồ Mạng Lưới (Thời Gian Thực)")
        graph_layout_box = QVBoxLayout()
        self.graph_widget = GraphWidget(self.cities, self.adj_matrix)
        graph_layout_box.addWidget(self.graph_widget)
        graph_group_box.setLayout(graph_layout_box)
        right_panel.addWidget(graph_group_box)

        tab1_layout.addLayout(left_panel, 2)
        tab1_layout.addLayout(mid_panel, 3)
        tab1_layout.addLayout(right_panel, 4)
        
        # ==================== TAB 2: PHÂN TÍCH CHUYÊN SÂU GBFS ====================
        tab2 = QWidget()
        tab2_layout = QHBoxLayout(tab2)
        
        # --- CỘT 1: ĐIỀU KHIỂN & LOG (Tỷ lệ 2) ---
        t2_left_panel = QVBoxLayout()
        t2_param_group = QGroupBox("Tham Số Đầu Vào Khảo Sát (Batch Testing)")
        t2_param_layout = QGridLayout()
        
        self.t2_graph_type = QComboBox()
        self.t2_graph_type.addItems(['Ngẫu nhiên (Uniform)', 'Phân cụm (Clustered)', 'Nút chai (Bottleneck)', 'Móng ngựa (Horseshoe)'])
        self.t2_graph_type.currentTextChanged.connect(self.update_t2_sparsity_label) # Link cập nhật nhãn
        
        self.t2_n = QSpinBox(); self.t2_n.setRange(10, 1000); self.t2_n.setValue(50)
        self.t2_seed = QSpinBox(); self.t2_seed.setRange(0, 9999); self.t2_seed.setValue(42)
        
        self.t2_sparsity_label = QLabel("Độ Thưa Ngẫu nhiên (?):")
        self.t2_sparsity_label.setStyleSheet("color: #c0392b; font-weight: bold;")
        self.t2_sparsity = QSpinBox(); self.t2_sparsity.setRange(0, 90); self.t2_sparsity.setValue(0); self.t2_sparsity.setSuffix("%")
        self.update_t2_sparsity_label()
        
        t2_param_layout.addWidget(QLabel("Dạng Đồ Thị:"), 0, 0); t2_param_layout.addWidget(self.t2_graph_type, 0, 1)
        t2_param_layout.addWidget(QLabel("Số Đỉnh (N):"), 1, 0); t2_param_layout.addWidget(self.t2_n, 1, 1)
        t2_param_layout.addWidget(QLabel("Seed Mẫu:"), 2, 0); t2_param_layout.addWidget(self.t2_seed, 2, 1)
        t2_param_layout.addWidget(self.t2_sparsity_label, 3, 0); t2_param_layout.addWidget(self.t2_sparsity, 3, 1)
        t2_param_group.setLayout(t2_param_layout)
        t2_left_panel.addWidget(t2_param_group)

        t2_control_group = QGroupBox("Kích Hoạt Kịch Bản Thực Nghiệm")
        t2_control_layout = QVBoxLayout()
        self.btn_kb1 = QPushButton("1. Sự Phụ Thuộc Điểm Xuất Phát")
        self.btn_kb1.setStyleSheet("background-color: #2b5c8f; color: white; padding: 7px; font-weight: bold;")
        self.btn_kb1.clicked.connect(self.run_kb1)
        self.btn_kb2 = QPushButton("2. Sức Chịu Đựng Đồ Thị Thưa")
        self.btn_kb2.setStyleSheet("background-color: #8f2b2b; color: white; padding: 7px; font-weight: bold;")
        self.btn_kb2.clicked.connect(self.run_kb2)
        self.btn_kb3 = QPushButton("3. Tốc Độ Mở Rộng (Scalability)")
        self.btn_kb3.setStyleSheet("background-color: #6a2b8f; color: white; padding: 7px; font-weight: bold;")
        self.btn_kb3.clicked.connect(self.run_kb3)
        
        t2_control_layout.addWidget(self.btn_kb1); t2_control_layout.addWidget(self.btn_kb2); t2_control_layout.addWidget(self.btn_kb3)
        t2_control_group.setLayout(t2_control_layout)
        t2_left_panel.addWidget(t2_control_group)
        
        self.t2_result_text = QTextEdit()
        self.t2_result_text.setReadOnly(True)
        self.t2_result_text.setFont(QFont('Consolas', 10))
        t2_left_panel.addWidget(QLabel("<b>Kết Quả & Phân Tích Thông Số:</b>"))
        t2_left_panel.addWidget(self.t2_result_text)
        
        # --- CỘT 2: HIỂN THỊ ĐỒ THỊ TRỰC QUAN (Tỷ lệ 3) ---
        t2_mid_panel = QVBoxLayout()
        t2_mid_panel.addWidget(QLabel("<b>Đồ thị Đại diện (Bảo vệ chu trình):</b>"))
        self.t2_graph_widget = GraphWidget([], None)
        t2_mid_panel.addWidget(self.t2_graph_widget)
        
        # --- CỘT 3: BIỂU ĐỒ & XUẤT EXCEL (Tỷ lệ 4) ---
        t2_right_panel = QVBoxLayout()
        self.figure_t2 = Figure()
        self.canvas_t2 = FigureCanvas(self.figure_t2)
        t2_right_panel.addWidget(QLabel("<b>Biểu Đồ Trực Quan Tình Huống:</b>"))
        t2_right_panel.addWidget(self.canvas_t2)
        
        self.export_excel_btn = QPushButton("📊 Xuất Số Liệu Ra Excel (Giai Đoạn 3)")
        self.export_excel_btn.setStyleSheet("background-color: #1d6f42; color: white; padding: 10px; font-weight: bold;")
        self.export_excel_btn.setEnabled(False)
        t2_right_panel.addWidget(self.export_excel_btn)
        
        tab2_layout.addLayout(t2_left_panel, 2)
        tab2_layout.addLayout(t2_mid_panel, 3)
        tab2_layout.addLayout(t2_right_panel, 4)

        tabs.addTab(tab1, "Tối ưu Trực quan & Mô phỏng")
        tabs.addTab(tab2, "Thực Nghiệm Chuyên Sâu GBFS")

    def generate_new_graph(self):
        n = self.node_spin.value(); seed = self.seed_spin.value()
        sparsity = self.sparsity_spin.value(); g_type = self.graph_type_combo.currentText()
        self.cities, self.adj_matrix, _ = GraphGenerator.generate_graph(n, seed, sparsity, g_type)
        self.graph_widget.set_data(self.cities, self.adj_matrix, None)
        self.populate_start_nodes()
        self.gbfs_results = None; self.cuckoo_results = None
        self.result_text.setText(f"✅ ĐÃ SINH ĐỒ THỊ MỚI:\n- Loại: {g_type}\n- Đỉnh: {n} | Seed: {seed} | Khuyết: {sparsity}%\n- Lưu ý: Lõi thuật toán đã bảo vệ 1 chu trình Hamilton bí mật để đảm bảo luôn tồn tại đáp án hoàn hảo!")
        self.figure_t2.clear()
        self.canvas_t2.draw()

    def populate_start_nodes(self):
        self.start_node_combo.clear()
        for city in self.cities:
            self.start_node_combo.addItem(f"Điểm {city.name}", city.id)

    def switch_route_view(self):
        self.animation_timer.stop() 
        has_data = bool(self.gbfs_route or self.cuckoo_route)
        self.replay_btn.setEnabled(has_data)
        self.replay_btn.setText("▶ Phát Hoạt Ảnh Tiến Hóa")
        
        start_id = self.start_node_combo.currentData()
        start_name = self.cities[start_id].name if (start_id is not None and start_id < len(self.cities)) else None

        if self.radio_gbfs.isChecked() and self.gbfs_route:
            t = f"Kết quả GBFS: Chi phí = {self.gbfs_route.fitness:.2f}"
            self.graph_widget.set_data(self.cities, self.adj_matrix, self.gbfs_route, start_name, t)
            self.animation_frames = self.gbfs_history_frames
        elif self.radio_cuckoo.isChecked() and self.cuckoo_route:
            t = f"Kết quả Cuckoo: Chi phí = {self.cuckoo_route.fitness:.2f}"
            self.graph_widget.set_data(self.cities, self.adj_matrix, self.cuckoo_route, start_name, t)
            self.animation_frames = self.cuckoo_history_frames
    
    def update_t2_sparsity_label(self):
        g_type = self.t2_graph_type.currentText()
        if "Uniform" in g_type:
            self.t2_sparsity_label.setText("Tỷ lệ Khuyết (Random) (?):")
            self.t2_sparsity_label.setToolTip("Xóa NGẪU NHIÊN các cạnh không thuộc chu trình Hamilton.")
        elif "Clustered" in g_type:
            self.t2_sparsity_label.setText("Tỷ lệ Cắt Xuyên Cụm (?):")
            self.t2_sparsity_label.setToolTip("Chỉ nhắm mục tiêu XÓA CÁC CẠNH NỐI GIỮA CÁC CỤM KHÁC NHAU để cô lập các cụm.")
        elif "Bottleneck" in g_type:
            self.t2_sparsity_label.setText("Tỷ lệ Cắt Cầu Nối (?):")
            self.t2_sparsity_label.setToolTip("Chỉ nhắm mục tiêu XÓA CÁC CẠNH NỐI GIỮA HAI BỜ để biến đồ thị thành nút thắt cổ chai.")
        elif "Horseshoe" in g_type:
            self.t2_sparsity_label.setText("Tỷ lệ Cắt Đường Tắt (?):")
            self.t2_sparsity_label.setToolTip("Chỉ nhắm mục tiêu XÓA CÁC CẠNH NHẢY CÓC (shortcut) qua rãnh chữ U.")

    def test_gbfs(self):
        start_id = self.start_node_combo.currentData()
        runs = self.run_count_spin.value()
        self.test_gbfs_btn.setEnabled(False)
        QApplication.processEvents()

        self.gbfs_results, self.gbfs_route, self.gbfs_history_frames, self.gbfs_cost_history = MetricsEvaluator.evaluate_gbfs_stability(self.cities, self.adj_matrix, runs, start_id)
        route_str = " -> ".join(self.gbfs_route.get_route_names()) if self.gbfs_route.is_feasible else "KHÔNG TÌM THẤY LỜI GIẢI KHẢ THI (Dính ngõ cụt đồ thị thưa)"

        result_text = f"""
{'='*60}
[BÁO CÁO GBFS] Lượt chạy: {runs} | Xuất phát: Điểm {self.cities[start_id].name}
{'='*60}
- Chi phí tốt nhất (Min Cost)  : {self.gbfs_results['best_cost']:.2f}
- Chi phí tệ nhất (Max Cost)   : {self.gbfs_results['worst_cost']:.2f}
- Thời gian thực thi trung bình: {self.gbfs_results['avg_execution_time']:.2f} ms
- Tỷ lệ khả thi đường đi      : {self.gbfs_results['feasibility_rate'] * 100:.1f}%

▶ Lộ trình tối ưu cục bộ:
{route_str}
"""
        self.radio_gbfs.setChecked(True)
        self.graph_widget.set_data(self.cities, self.adj_matrix, self.gbfs_route, self.cities[start_id].name, f"GBFS | Chi phí: {self.gbfs_route.fitness:.2f}")
        self.result_text.setText(result_text)
        self.test_gbfs_btn.setEnabled(True)
        self.update_convergence_plot()

    def test_cuckoo(self):
        start_id = self.start_node_combo.currentData()
        runs = self.run_count_spin.value()
        self.result_text.setText(f"Đang phân tích Cuckoo Search ({runs} lượt)...")
        self.test_cuckoo_btn.setEnabled(False)
        QApplication.processEvents()

        self.cuckoo_results, self.cuckoo_route, self.cuckoo_history_frames, self.cuckoo_cost_history = MetricsEvaluator.evaluate_cuckoo_stability(
            self.cities, self.adj_matrix, self.pop_size_spin.value(), 
            self.max_gen_spin.value(), self.pa_spin.value(), runs, start_id)

        best_route_str = " -> ".join(self.cuckoo_route.get_route_names(self.cities[start_id].name)) if self.cuckoo_route.is_feasible else "KHÔNG TÌM THẤY LỜI GIẢI KHẢ THI"

        result_text = f"""
{'='*60}
[BÁO CÁO CUCKOO SEARCH] Lượt chạy: {runs}
{'='*60}
- Chi phí tốt nhất (Min Cost)  : {self.cuckoo_results['best_cost']:.2f}
- Chi phí tệ nhất (Max Cost)   : {self.cuckoo_results['worst_cost']:.2f}
- Thời gian thực thi trung bình: {self.cuckoo_results['avg_execution_time']:.2f} ms
- Tỷ lệ khả thi đường đi      : {self.cuckoo_results['feasibility_rate'] * 100:.1f}%

▶ Lộ trình tối ưu chuỗi:
{best_route_str}
"""
        self.radio_cuckoo.setChecked(True)
        self.graph_widget.set_data(self.cities, self.adj_matrix, self.cuckoo_route, self.cities[start_id].name, f"Cuckoo | Chi phí: {self.cuckoo_cost_history[-1]:.2f}")
        self.result_text.setText(result_text)
        self.test_cuckoo_btn.setEnabled(True)
        self.update_convergence_plot()

    def start_animation(self):
        if self.radio_gbfs.isChecked(): self.animation_frames = self.gbfs_history_frames
        elif self.radio_cuckoo.isChecked(): self.animation_frames = self.cuckoo_history_frames

        if not self.animation_frames: return
            
        self.animation_idx = 0
        self.improvement_count = 0
        self.last_animated_cost = float('inf')
        self.replay_btn.setEnabled(False)
        self.replay_btn.setText("⏳ Đang phát...")
        self.animation_timer.start(120) 

    def animate_next_frame(self):
        if self.animation_idx < len(self.animation_frames):
            frame_route = self.animation_frames[self.animation_idx]
            start_id = self.start_node_combo.currentData()
            start_name = self.cities[start_id].name if start_id is not None else None
            cost = frame_route.fitness
            
            overlay_str = f"Gen {self.animation_idx} | Chi phí: {cost:.2f}"
            if self.animation_idx == 0:
                self.result_text.append(f"➔ Khởi tạo | Chi phí: {cost:.2f}")
                self.last_animated_cost = cost
            elif cost < self.last_animated_cost:
                self.improvement_count += 1
                self.result_text.append(f"➔ Cải thiện {self.improvement_count} | Chi phí: {cost:.2f}")
                self.last_animated_cost = cost
            
            self.graph_widget.set_data(self.cities, self.adj_matrix, frame_route, start_name, overlay_str)
            self.animation_idx += 1
        else:
            self.animation_timer.stop()
            self.replay_btn.setEnabled(True)
            self.replay_btn.setText("▶ Phát Hoạt Ảnh Tiến Hóa")
            self.result_text.append("✅ Đã phát xong chu kỳ tiến hóa.")

    def update_convergence_plot(self):
        self.figure_t2.clear()
        ax = self.figure_t2.add_subplot(111)
        
        if len(self.gbfs_cost_history) > 0:
            ax.plot(self.gbfs_cost_history, label='GBFS', color='#2b5c8f', linestyle='--', linewidth=2)
        if len(self.cuckoo_cost_history) > 0:
            ax.plot(self.cuckoo_cost_history, label='Cuckoo Search', color='#8f2b2b', linewidth=2)
            
        ax.set_title('Bản đồ Đường cong Hội tụ Thuật toán', fontsize=12, fontweight='bold')
        ax.set_xlabel('Thế hệ tiến hóa (Generations)')
        ax.set_ylabel('Chi phí quãng đường tốt nhất (Best Cost)')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        self.figure_t2.tight_layout() 
        self.canvas_t2.draw()

    def compare_results(self):
        if not self.gbfs_results or not self.cuckoo_results:
            self.result_text.setText("⚠ Vui lòng chạy cả 2 thuật toán!")
            return

        g_cost = self.gbfs_results['best_cost']
        c_cost = self.cuckoo_results['best_cost']
        imp_str = "N/A" if g_cost == float('inf') else f"{((g_cost - c_cost) / g_cost * 100):+.2f}%"

        result_text = f"""
{'=' * 60}
BẢNG SO SÁNH ĐỐI CHIẾU
{'=' * 60}
[1] GBFS:  Chi phí = {g_cost:.2f}  | Tỷ lệ khả thi = {self.gbfs_results['feasibility_rate']*100}%
[2] Cuckoo: Chi phí = {c_cost:.2f} | Tỷ lệ khả thi = {self.cuckoo_results['feasibility_rate']*100}%
▶ Cuckoo cải thiện so với GBFS: {imp_str}
"""
        self.result_text.setText(result_text)

    def export_excel_report(self):
        if not self.gbfs_results or not self.cuckoo_results:
            self.result_text.setText("⚠ Bấm chạy các thuật toán trước khi xuất Excel.")
            return
            
        summary_data = {
            'Chỉ số đo lường': ['Min Cost', 'Max Cost', 'Avg Cost', 'Avg Time (ms)', 'Feasibility Rate (%)'],
            'GBFS': [self.gbfs_results['best_cost'], self.gbfs_results['worst_cost'], self.gbfs_results['avg_cost'], self.gbfs_results['avg_execution_time'], self.gbfs_results['feasibility_rate']*100],
            'Cuckoo Search': [self.cuckoo_results['best_cost'], self.cuckoo_results['worst_cost'], self.cuckoo_results['avg_cost'], self.cuckoo_results['avg_execution_time'], self.cuckoo_results['feasibility_rate']*100]
        }
        df = pd.DataFrame(summary_data)
        filename = "Bao_Cao_GBFS_vs_Cuckoo.xlsx"
        df.to_excel(filename, index=False)
        self.result_text.append(f"\n✅ Đã xuất thành công tệp: '{filename}'")

    def run_kb1(self):
        n = self.t2_n.value(); seed = self.t2_seed.value(); sparsity = self.t2_sparsity.value(); g_type = self.t2_graph_type.currentText()
        self.t2_result_text.setText("Đang chạy Kịch Bản 1 (Sinh mới đồ thị và Quét toàn bộ điểm xuất phát)...")
        QApplication.processEvents()
        
        res = GBFSAnalyzer.run_scenario_1_starting_points(n, seed, sparsity, g_type)
        self.t2_graph_widget.set_data(res['cities'], res['adj_matrix'], None, None, f"{g_type}\nĐã áp dụng Khuyết cạnh: {sparsity}%")
        
        txt = f"""
[KỊCH BẢN 1] MỨC ĐỘ PHỤ THUỘC ĐIỂM XUẤT PHÁT
Đồ thị: {g_type} | N = {n} | Cắt cạnh bẫy = {sparsity}%
--------------------------------------------------
- Tổng số điểm khả thi  : {len(res['costs'])}/{n} ({res['feasibility_rate']*100:.1f}%)
- Cost Tốt nhất (Min)   : {res['min']:.2f}
- Cost Tệ nhất (Max)    : {res['max']:.2f}
- Chênh lệch (Max-Min)  : {res['max'] - res['min']:.2f}
- Độ lệch chuẩn (Std)   : {res['std']:.2f}
"""
        self.t2_result_text.setText(txt)
        
        self.figure_t2.clear()
        ax = self.figure_t2.add_subplot(111)
        if res['nodes']:
            ax.bar(res['nodes'], res['costs'], color='#2b5c8f')
            ax.axhline(y=res['mean'], color='r', linestyle='--', label=f"Trung bình: {res['mean']:.2f}")
        ax.set_title(f'Phân phối Cost theo Điểm xuất phát')
        ax.set_xlabel('Index Điểm xuất phát')
        ax.set_ylabel('Tổng Chi Phí (Cost)')
        ax.legend()
        self.figure_t2.tight_layout()
        self.canvas_t2.draw()

    def run_kb2(self):
        n = self.t2_n.value(); seed = self.t2_seed.value(); g_type = self.t2_graph_type.currentText()
        self.t2_result_text.setText(f"Đang chạy Kịch Bản 2 (Tăng dần tỷ lệ khuyết cạnh từ 0% -> 90% cho N={n})...")
        QApplication.processEvents()
        
        res = GBFSAnalyzer.run_scenario_2_sparsity_tolerance(n, seed, g_type)
        self.t2_graph_widget.set_data(res['cities'], res['adj_matrix'], None, None, f"{g_type}\n(Mẫu cắt 50% cạnh bẫy)")
        
        txt = f"""
[KỊCH BẢN 2] SỨC CHỊU ĐỰNG ĐỒ THỊ THƯA & BẪY CỤC BỘ
Đồ thị: {g_type} | N = {n} | Seed = {seed}
--------------------------------------------------
- Thuật toán sinh đồ thị bảo đảm 100% đồ thị LUÔN CÓ ĐÁP ÁN (1 chu trình Hamilton được khóa lại).
- Tỷ lệ cắt cạnh tăng dần đồng nghĩa với việc các "mồi nhử" dễ bị lộ, nhưng GBFS vẫn đâm đầu vào ngõ cụt vì tính tham lam không lối thoát.
- Tại mức cắt 50%: Tỷ lệ sống sót = {res['feasibility_rates'][10]:.1f}%
"""
        self.t2_result_text.setText(txt)
        
        self.figure_t2.clear()
        ax = self.figure_t2.add_subplot(111)
        ax.plot(res['sparsity_levels'], res['feasibility_rates'], marker='o', color='#8f2b2b', linewidth=2)
        ax.set_title('Tỷ lệ Sống sót theo Mức độ Cắt cạnh')
        ax.set_xlabel('Tỷ lệ Cắt cạnh (%)')
        ax.set_ylabel('Tỷ lệ Thành công (%)')
        ax.set_ylim(-5, 105)
        ax.grid(True, linestyle=':', alpha=0.7)
        self.figure_t2.tight_layout()
        self.canvas_t2.draw()

    def run_kb3(self):
        seed = self.t2_seed.value()
        self.t2_result_text.setText("Đang chạy Kịch Bản 3...")
        QApplication.processEvents()
        
        res = GBFSAnalyzer.run_scenario_3_scalability(seed)
        self.t2_graph_widget.set_data(res['cities'], res['adj_matrix'], None, None, f"Uniform (Mẫu N=100)\nKiểm tra khả năng Scaling")
        
        txt = f"""
[KỊCH BẢN 3] ĐÁNH GIÁ TỐC ĐỘ THỰC THI (SCALABILITY)
--------------------------------------------------
- GBFS giải quyết bài toán N=1000 trong thời gian {res['execution_times'][-1]:.2f} ms. Đường cong thể hiện rõ độ phức tạp thời gian O(V^2).
"""
        self.t2_result_text.setText(txt)
        
        self.figure_t2.clear()
        ax = self.figure_t2.add_subplot(111)
        ax.plot(res['n_values'], res['execution_times'], marker='s', color='#6a2b8f', linewidth=2)
        ax.set_title('Thời gian Thực thi theo Số lượng Đỉnh (N)')
        ax.set_xlabel('Số lượng Đỉnh N')
        ax.set_ylabel('Thời gian (ms)')
        ax.grid(True, linestyle=':', alpha=0.7)
        self.figure_t2.tight_layout()
        self.canvas_t2.draw()