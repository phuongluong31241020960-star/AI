# AI
Chào bạn, dựa trên các file mã nguồn bạn đã cung cấp (`main.py`, `gui.py`, `algorithms.py`, `models.py`), đây là một ứng dụng giao diện trực quan (GUI) được xây dựng bằng PyQt6 để mô phỏng, giải quyết và phân tích bài toán tìm đường (như TSP) sử dụng thuật toán Tìm kiếm tham lam tốt nhất đầu tiên (Greedy Best-First Search - GBFS).

Dưới đây là bản nháp README chi tiết, chuyên nghiệp và sẵn sàng để bạn sử dụng cho dự án trên GitHub hoặc GitLab.

---

# GBFS Routing Analyzer & Visualizer

Một ứng dụng Desktop trực quan được viết bằng Python và PyQt6, nhằm mục đích mô phỏng, giải quyết và đánh giá hiệu năng của thuật toán **Greedy Best-First Search (GBFS)** trên các đồ thị khác nhau. Dự án hỗ trợ phân tích tỷ lệ thành công (feasibility), tốc độ thực thi (scalability) và mô phỏng các dạng đồ thị đặc thù.

## Tính năng nổi bật

* **Mô phỏng đồ thị đa dạng:** Hỗ trợ tạo đồ thị theo nhiều kiểu phân bố khác nhau như Ngẫu nhiên (Uniform), Phân cụm (Clustered) và Nút chai (Bottleneck).
* **Trực quan hóa lộ trình:** Hiển thị trực tiếp các điểm (City) và lộ trình (Route) trên đồ thị 2D thông qua tích hợp `Matplotlib` vào `PyQt6`.
* **Đánh giá Kịch bản (Scenarios):**
* **Kịch bản 1:** Đánh giá các chỉ số cơ bản của thuật toán GBFS (Chi phí đường đi, Thời gian chạy, Tính khả thi).
* **Kịch bản 2:** Phân tích tỷ lệ sống sót/thành công dựa trên mức độ thưa thớt (Sparsity) của cạnh.
* **Kịch bản 3:** Đánh giá khả năng mở rộng (Scalability) và tốc độ thực thi khi số lượng đỉnh $N$ tăng lên đến 1000.


* **Giao diện thân thiện:** Cho phép người dùng tùy chỉnh Seed, tỷ lệ cắt cạnh (Sparsity) và tương tác trực tiếp qua các Tab thống kê.

## Cấu trúc thư mục

* `main.py`: File khởi chạy chính của ứng dụng. Thiết lập vòng lặp sự kiện (event loop) của PyQt6.
* `gui.py`: Chứa toàn bộ logic giao diện người dùng. Xây dựng các Widget, Tab điều khiển, và biểu đồ Matplotlib (`GraphWidget`).
* `algorithms.py`: Trái tim của dự án, bao gồm:
* `GraphGenerator`: Sinh dữ liệu đồ thị ngẫu nhiên.
* `GreedySolver`: Triển khai thuật toán tìm đường tham lam.
* `GBFSAnalyzer` & `MetricsEvaluator`: Phân tích hiệu suất và chạy các kịch bản test.


* `models.py`: Định nghĩa các cấu trúc dữ liệu cơ bản như `City` (Thành phố), `Route` (Lộ trình), và `RouteMetrics` (Đo lường).

## 🛠 Yêu cầu hệ thống

Đảm bảo bạn đã cài đặt **Python 3.8+**. Cài đặt các thư viện phụ thuộc (dependencies) bằng lệnh sau:

```bash
pip install PyQt6 matplotlib numpy pandas

```

## Hướng dẫn sử dụng

1. **Clone repository** hoặc tải bộ source code này về máy của bạn.
2. **Mở terminal/command prompt** tại thư mục chứa source code.
3. **Khởi chạy ứng dụng** bằng lệnh:

```bash
python main.py

```

4. **Tương tác với ứng dụng:**
* Sử dụng các thanh công cụ để chọn **Loại đồ thị** hoặc điều chỉnh **Seed**.
* Chuyển đổi qua lại giữa các Tab Kịch bản để chạy thử nghiệm và xem biểu đồ phân tích thời gian thực.



## Hình ảnh minh họa

*(Bạn có thể thay thế hình ảnh `image_f5b20d.png` mà bạn tải lên vào thư mục dự án và chèn đường dẫn vào đây để làm tài liệu sinh động hơn).*

```markdown
![Giao diện chính của ứng dụng](đường_dẫn_tới_ảnh/image_f5b20d.png)

```

## Đóng góp (Contributing)

Mọi đóng góp nhằm cải thiện hiệu năng thuật toán, bổ sung các heuristic mới (như A*, Simulated Annealing, Genetic Algorithm) để so sánh với GBFS đều được chào đón. Vui lòng tạo Pull Request hoặc mở Issue để thảo luận.

---

*Hy vọng bản README này giúp dự án của bạn trở nên chuyên nghiệp và dễ tiếp cận hơn. Nếu bạn cần điều chỉnh thêm bất kỳ phần nào cho phù hợp với ý định cá nhân, hãy cho tôi biết nhé!*
