# services/ocrspace_service.py
import requests
import re
import os

class OCRSpaceService:
    """
    Cloud-based OCR Service using OCR.space API.
    Supports Vietnamese text recognition.
    """
    
    API_ENDPOINT = "https://api.ocr.space/parse/image"
    
    # Full list of Vietnam provinces
    VIETNAM_PROVINCES = [
        "Hà Nội", "TP. Hồ Chí Minh", "Hải Phòng", "Đà Nẵng", "Cần Thơ", "Huế",
        "Cao Bằng", "Điện Biên", "Lai Châu", "Sơn La", "Lạng Sơn", "Quảng Ninh",
        "Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Tuyên Quang", "Lào Cai", "Thái Nguyên",
        "Phú Thọ", "Bắc Ninh", "Hưng Yên", "Ninh Bình", "Quảng Trị", "Quảng Ngãi",
        "Gia Lai", "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
        "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang"
    ]

    def __init__(self):
        """Initialize OCR.space service with API key."""
        self.api_key = self._load_api_key()
        if self.api_key:
            print("OCR.space API đã sẵn sàng!")
        else:
            print("⚠️ Chưa có API Key! Vui lòng thêm vào file ocrspace_config.txt")

    def _load_api_key(self):
        """Load API key from config file or environment."""
        # Try environment variable first
        api_key = os.environ.get('OCRSPACE_API_KEY')
        if api_key:
            return api_key
        
        # Try config file
        config_paths = [
            'ocrspace_config.txt',
            os.path.join(os.path.dirname(__file__), '..', 'ocrspace_config.txt')
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    key = f.read().strip()
                    if key:
                        return key
        
        return None

    def extract_text(self, image_path, lang='vie'):
        """Extract text from image using OCR.space API."""
        if not self.api_key:
            print("Error: API Key not configured!")
            return None
        
        try:
            print(f"Đang gửi ảnh lên OCR.space...")
            
            with open(image_path, 'rb') as f:
                payload = {
                    'apikey': self.api_key,
                    'language': 'vnm',  # Vietnamese
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2  # Engine 2 is better for Asian languages
                }
                
                files = {
                    'file': f
                }
                
                response = requests.post(
                    self.API_ENDPOINT,
                    data=payload,
                    files=files,
                    timeout=30
                )
            
            result = response.json()
            
            if result.get('IsErroredOnProcessing'):
                error_msg = result.get('ErrorMessage', ['Unknown error'])
                print(f"OCR.space Error: {error_msg}")
                return None
            
            # Extract text from all parsed results
            parsed_results = result.get('ParsedResults', [])
            if not parsed_results:
                print("Không tìm thấy text trong ảnh!")
                return None
            
            raw_text = parsed_results[0].get('ParsedText', '')
            
            print("\n----- OCR.space RAW OUTPUT START -----")
            print(raw_text)
            print("----- OCR.space RAW OUTPUT END -----\n")
            
            return raw_text
            
        except requests.exceptions.Timeout:
            print("Error: Request timeout!")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"OCR.space Error: {e}")
            return None

    def parse_order_info(self, raw_text):
        """Parse order information with flexible patterns for OCR errors."""
        if not raw_text:
            return self._get_empty_info()
        
        info = self._get_empty_info()
        lines = raw_text.split('\n')
        
        def find_province(text):
            text_lower = text.lower()
            for prov in self.VIETNAM_PROVINCES:
                if prov.lower() in text_lower:
                    return prov
            
            # Heuristic for common OCR errors
            if 'nẵng' in text_lower and 'đà' in text_lower:
                return "Đà Nẵng"
            if 'chí minh' in text_lower or 'hcm' in text_lower or 'sài gòn' in text_lower:
                return "TP. Hồ Chí Minh"
            if 'hà nội' in text_lower or 'hn' in text_lower:
                return "Hà Nội"
            return None

        # --- SECTION DETECTION ---
        current_section = "sender"
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Switch section
            if 'người nhận' in line_lower:
                current_section = "receiver"
            elif 'người gửi' in line_lower:
                current_section = "sender"
                
            # --- NAME ---
            if 'người' in line_lower and ('gửi' in line_lower or 'nhận' in line_lower) and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    if len(name) > 2:
                        if 'gửi' in line_lower:
                            info["sender_name"] = name
                        elif 'nhận' in line_lower:
                            info["receiver_name"] = name

            # --- PHONE ---
            if re.search(r'sđt|sdt|đt|phone|điện thoại', line_lower):
                phones = re.findall(r'[0-9][\d\.\-\s]{8,12}', line)
                for phone in phones:
                    clean = re.sub(r'[^\d]', '', phone)
                    if 10 <= len(clean) <= 11:
                        if not clean.startswith('0'):
                            clean = '0' + clean
                        if current_section == "sender" and not info["sender_phone"]:
                            info["sender_phone"] = clean
                        elif current_section == "receiver" and not info["receiver_phone"]:
                            info["receiver_phone"] = clean

            # --- EMAIL ---
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.[\w]+', line)
            if emails:
                if current_section == "sender" and not info["sender_email"]:
                    info["sender_email"] = emails[0]
                elif current_section == "receiver" and not info["receiver_email"]:
                    info["receiver_email"] = emails[0]

            # --- ADDRESS ---
            # Match: "Địa chỉ gửi:", "Địa chỉ nhận:", "Địa chi gửi:" (OCR typo), "ĐC:"
            if 'địa ch' in line_lower or 'dc:' in line_lower.replace(' ', ''):
                if ':' in line:
                    parts = line.split(':', 1)
                    addr_content = parts[1].strip()
                    if addr_content:
                        # Determine section from line content
                        if 'gửi' in line_lower:
                            info["sender_address"] = addr_content
                        elif 'nhận' in line_lower:
                            info["receiver_address"] = addr_content
                        elif current_section == "sender" and not info["sender_address"]:
                            info["sender_address"] = addr_content
                        elif current_section == "receiver" and not info["receiver_address"]:
                            info["receiver_address"] = addr_content
            
            # --- PROVINCE ---
            prov = find_province(line)
            if prov:
                if current_section == "sender" and not info["sender_province"]:
                    info["sender_province"] = prov
                elif current_section == "receiver" and not info["receiver_province"]:
                    info["receiver_province"] = prov
            
            # --- WARD (Xã/Phường) ---
            # Look for ward patterns: "Phường X", "Xã Y", "TT. Z"
            ward_match = re.search(r'(Phường|Xã|TT\.|Thị trấn)\s+[\w\s]+', line, re.IGNORECASE)
            if ward_match:
                ward_text = ward_match.group(0).strip()
                if current_section == "sender" and not info.get("sender_ward"):
                    info["sender_ward"] = ward_text
                elif current_section == "receiver" and not info.get("receiver_ward"):
                    info["receiver_ward"] = ward_text

            # --- ITEM NAME ---
            if 'tên hàng' in line_lower and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    info["item_name"] = parts[1].strip()

            # --- WEIGHT ---
            if 'trọng lượng' in line_lower or 'khối lượng' in line_lower:
                numbers = re.findall(r'[\d\.,]+', line)
                for num in numbers:
                    try:
                        val = float(num.replace(',', '.'))
                        if val < 1000:
                            info["weight"] = val
                            break
                    except: pass

            # --- PACKAGE COUNT ---
            if 'số kiện' in line_lower:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    try:
                        info["package_count"] = int(numbers[0])
                    except: pass
            
            # --- SHIPPING COST ---
            if 'phí vận' in line_lower or 'cước' in line_lower:
                numbers = re.findall(r'[\d\.,]+', line)
                for num in numbers:
                    try:
                        val = float(num.replace(',', '').replace('.', ''))
                        if val > 1000:
                            info["shipping_cost"] = val
                            break
                    except: pass
            
            # --- COD ---
            if 'thu hộ' in line_lower or 'cod' in line_lower:
                numbers = re.findall(r'[\d\.,]+', line)
                for num in numbers:
                    try:
                        val = float(num.replace(',', '').replace('.', ''))
                        if val > 1000:
                            info["cod_amount"] = val
                            info["has_cod"] = True
                            break
                    except: pass

            # --- DELIVERY NOTE ---
            if 'ghi chú' in line_lower or 'lưu ý' in line_lower:
                content = ""
                if ':' in line:
                    parts = line.split(':', 1)
                    content = parts[1].strip()
                
                # Check next line for continuation
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if ':' not in next_line and not re.match(r'^[\d\.\s]+(vnđ|vnd)?$', next_line.lower()):
                        content += " " + next_line
                
                if len(content) > 3:
                    info["delivery_note"] = content

        # --- DIMENSIONS ---
        dim_match = re.search(r'(\d+)\s*[xX×]\s*(\d+)\s*[xX×]\s*(\d+)', raw_text)
        if dim_match:
            info["dimensions"] = f"{dim_match.group(1)}x{dim_match.group(2)}x{dim_match.group(3)} cm"

        # Debug print
        print("\n--- PARSED DATA ---")
        for k, v in info.items():
            if v:
                print(f"{k}: {v}")
        print("-------------------\n")

        return info

    def _get_empty_info(self):
        """Return empty info structure."""
        return {
            "sender_name": "",
            "sender_phone": "",
            "sender_email": "",
            "sender_address": "",
            "sender_province": "",
            "sender_ward": "",
            "receiver_name": "",
            "receiver_phone": "",
            "receiver_email": "",
            "receiver_address": "",
            "receiver_province": "",
            "receiver_ward": "",
            "item_name": "",
            "weight": 0.0,
            "package_count": 1,
            "dimensions": "",
            "shipping_cost": 0.0,
            "cod_amount": 0.0,
            "has_cod": False,
            "delivery_note": ""
        }
