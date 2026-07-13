# Dialect2English — Annotation Guide

## 1. Start Label Studio

```bash
pip install -r requirements.txt
label-studio start
```

Mở browser → `http://localhost:8080` → đăng ký / đăng nhập.

## 2. Lấy Access Token

1. Click **avatar** (góc trên phải) → **Account & Settings**
2. Copy **Access Token**
3. Paste vào file `.env`:

```
LABEL_STUDIO_API_KEY=<paste-token-here>
```

## 3. Chạy script tạo project

1. **Pull code mới nhất** (git pull) để lấy dữ liệu mới trong thư mục `dev/`.
2. Mở file `setup_label_studio.py`.
3. Tìm biến `INPUT_FILE` (khoảng dòng 14) và thay đổi đường dẫn tới file CSV được phân công cho bạn. Ví dụ:
   ```python
   INPUT_FILE = 'dev/TenCuaBan_voting_dev.csv' 
   ```
   hoặc
   ```python
   INPUT_FILE = 'test/TenCuaBan_voting_test.csv' 
   ```
4. Chạy script để tạo project:
   ```bash
   python setup_label_studio.py
   ```

Script sẽ tạo ra 2 projects mới (Majority và No Majority) dựa trên file dữ liệu của bạn. Sau khi chạy xong, terminal sẽ in ra URL của các projects này.

## 4. Annotate

1. Mở URL project (ví dụ: `http://localhost:8080/projects/1`)
2. Click **Label All Tasks**
3. Với mỗi task:
   - **MAJORITY** → **Accept** (winner tốt) hoặc **Reject** + viết lại bản dịch
   - **NO MAJORITY** → **Choose A/B/C** hoặc **Re-translate** + viết bản dịch mới
4. Click **Submit** để lưu và chuyển task tiếp theo
