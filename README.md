# Logistics Management System

## Tài khoản mặc định
- Username: `admin`
- Password: `admin123`

## Cài đặt Development Environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

## Build EXE cho Windows

```bash
pyinstaller --onefile --windowed --name LogisticsApp ^
  --hidden-import PyQt6 ^
  --hidden-import PyQt6.QtWidgets ^
  --hidden-import PyQt6.QtCore ^
  --hidden-import PyQt6.QtGui ^
  --hidden-import PyQt6.sip ^
  --hidden-import sqlalchemy ^
  --hidden-import sqlalchemy.sql.default_comparator ^
  --add-data "data/province_wards.json;data" ^
  main.py
```
