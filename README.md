## Credit
| NHÓM | 12 |
| --- | --- |
| MÔN HỌC | TRÍ TUỆ NHÂN TẠO |
| HỌC PHẦN | 26D1INF50904201 |
| ĐỀ TÀI | GIẢI BÀI TOÁN TSP |
| MSSV | 31241020960 |
| | 31241023829 |
| | 31241023829 |

---
# Routing Analyzer & Visualizer: GBFS vs. Cuckoo Search

Một ứng dụng Desktop trực quan và mạnh mẽ được xây dựng bằng Python và PyQt6, phục vụ việc mô phỏng, giải quyết và phân tích so sánh bài toán tìm đường (Routing Problem) giữa thuật toán cơ bản Greedy Best-First Search (GBFS) và thuật toán tối ưu hóa thông minh Cuckoo Search (CS).

Ứng dụng không chỉ giải toán mà còn đóng vai trò như một công cụ nghiên cứu, giúp đánh giá độ hội tụ, tốc độ thực thi và độ ổn định của thuật toán metaheuristic so với thuật toán tham lam truyền thống.

## Tính năng nổi bật
### 1. Thuật toán giải toán đa dạng

* **Greedy Best-First Search (GBFS):** Thuật toán tìm kiếm tham lam dựa trên khoảng cách ngắn nhất để xây dựng lộ trình ban đầu một cách nhanh chóng.
* **Cuckoo Search Optimizer:** Thuật toán tối ưu hóa lấy cảm hứng từ tập tính đẻ trứng nhờ của loài chim cúc cu. Sử dụng cơ chế bước nhảy Lévy (Lévy flights) để tối ưu hóa và cải thiện chất lượng lộ trình từ GBFS, giúp tránh bẫy tối ưu cục bộ.

### 2. Mô phỏng đồ thị đa dạng (Graph Generator)
Hỗ trợ sinh tự động các cấu trúc đồ thị thực tế với cơ chế cắt cạnh (Sparsity) tùy chỉnh:

* **Ngẫu nhiên (Uniform):** Các điểm phân bố đều trên không gian 2D.
* **Phân cụm (Clustered):** Các điểm tập trung thành từng cụm (tương tự các đô thị vệ tinh).
* **Nút chai (Bottleneck):** Tạo ra các điểm thắt nút giao thông để thử thách thuật toán.

### 3. Công cụ phân tích và Trực quan hóa chuyên sâu
* **Kịch bản 1:** Đánh giá các chỉ số cơ bản của thuật toán GBFS (Chi phí đường đi, Thời gian chạy, Tính khả thi).
* **Kịch bản 2:** Phân tích tỷ lệ sống sót/thành công dựa trên mức độ thưa thớt (Sparsity) của cạnh.
* **Kịch bản 3:** Đánh giá khả năng mở rộng (Scalability) và tốc độ thực thi khi số lượng đỉnh $N$ tăng lên đến 1000.
* **Trực quan hóa đồ thị động:** Vẽ trực tiếp các nút và đường đi của GBFS hoặc Cuckoo Search. Hỗ trợ tính năng **Replay** để xem hoạt ảnh (animation) quá trình tìm đường hoặc quá trình tiến hóa từng bước.
* **Đồ thị hội tụ (Convergence Plot):** Vẽ biểu đồ Matplotlib thể hiện sự suy giảm chi phí (cost) qua từng thế hệ của Cuckoo Search so với mốc cố định của GBFS.
* **Báo cáo đối chiếu:** Phân tích chi tiết các chỉ số: Chi phí tốt nhất (Min Cost), Chi phí tệ nhất (Max Cost), Thời gian chạy trung bình (ms), và Tỷ lệ tìm được đường đi hợp lệ (Feasibility Rate).
* **Xuất báo cáo Excel:** Tính năng xuất toàn bộ dữ liệu so sánh trực tiếp ra file Excel mang tên `Bao_Cao_GBFS_vs_Cuckoo.xlsx` chỉ với một cú click.

* **Giao diện thân thiện:** Cho phép người dùng tùy chỉnh Seed, tỷ lệ cắt cạnh (Sparsity) và tương tác trực tiếp qua các Tab thống kê.

### 4. **Tương tác với ứng dụng:**
* Sử dụng các thanh công cụ để chọn **Loại đồ thị** hoặc điều chỉnh **Seed**.
* Chuyển đổi qua lại giữa các Tab Kịch bản để chạy thử nghiệm và xem biểu đồ phân tích thời gian thực.

Các tham số cấu hình Cuckoo Search hỗ trợ
| Tham số | Ý nghĩa |
| --- | --- |
| **Population Size** | Số lượng chim cúc cu (kích thước quần thể lời giải). |
| **Max Generations** | Số thế hệ tối đa thuật toán sẽ tiến hóa để tìm đường đi tốt hơn. |
| **Probability ($p_a$)** | Xác suất phát hiện và hủy bỏ trứng của chim chủ nhà (thay thế lời giải xấu). |

<img width="1916" height="1140" alt="image" src="https://github.com/user-attachments/assets/5f767fb6-a143-4767-8463-c05b74ed081f" />
<img width="1919" height="1134" alt="image" src="https://github.com/user-attachments/assets/aa0ef991-b9cb-46ce-b638-6ca81946372b" />

## Hướng dẫn sử dụng

1. Tải toàn bộ file code py và bỏ vào 1 thư mục.
2. Dùng Pycharm (hoặc các IDE khác) mở file thư mục
3. Vào file main.py ấn chạy

## Yêu cầu hệ thống & Cài đặt

Ứng dụng yêu cầu **Python 3.8+**. Để cài đặt tất cả các thư viện cần thiết, bạn chạy lệnh sau trong terminal:

```bash
pip install PyQt6 matplotlib numpy pandas openpyxl

```

> **Lưu ý:** Thư viện `openpyxl` là bắt buộc để hỗ trợ tính năng xuất báo cáo ra file Excel.

---

## Cấu trúc mã nguồn

* `main.py`: File thực thi chính của ứng dụng, khởi tạo vòng lặp sự kiện `QApplication`.
* `gui.py`: Định nghĩa giao diện người dùng (UI) bằng PyQt6, tích hợp canvas của Matplotlib và các luồng xử lý sự kiện tương tác, cập nhật hoạt ảnh.
* `algorithms.py`: Nơi chứa toàn bộ lõi xử lý thuật toán:
* `GraphGenerator`: Tạo ma trận kề và tọa độ các thành phố.
* `GreedySolver`: Triển khai thuật toán GBFS.
* `CuckooOptimizer`: Triển khai thuật toán Cuckoo Search (khởi tạo quần thể, bước nhảy Lévy, loại bỏ trứng với xác suất $p_a$).
* `MetricsEvaluator` & `GBFSAnalyzer`: Đánh giá hiệu năng và chạy các kịch bản kiểm thử diện rộng.


* `models.py`: Định nghĩa các cấu trúc dữ liệu nền tảng gồm `City` (Thành phố), `Route` (Lộ trình), và `RouteMetrics` (Bộ chỉ số đo lường).

---

## Đóng góp (Contributing)

Mọi đóng góp nhằm cải thiện hiệu năng thuật toán, bổ sung các heuristic mới (như A*, Simulated Annealing, Genetic Algorithm) để so sánh với GBFS đều được chào đón. Vui lòng tạo Pull Request hoặc mở Issue để thảo luận.


