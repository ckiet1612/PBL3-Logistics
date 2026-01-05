# services/report_service.py
import pandas as pd
from sqlalchemy.orm import Session
from database.db_connection import SessionLocal
from models.order import Order

class ReportService:
    def __init__(self):
        pass

    def export_to_excel(self, file_path):
        """
        Export all orders from the database to an Excel file.
        :param file_path: The destination path to save the .xlsx file.
        :return: (True, message) if successful, (False, error) otherwise.
        """
        session: Session = SessionLocal()
        try:
            # 1. Query all data from the database
            orders = session.query(Order).all()
            
            if not orders:
                return False, "No data to export."

            # 2. Convert object list to a list of dictionaries
            data = []
            for order in orders:
                data.append({
                    "ID": order.id,
                    "Tracking Code": order.tracking_code,
                    "Sender": order.sender_name,
                    "Receiver": order.receiver_name,
                    "Phone": order.receiver_phone,
                    "Address": order.receiver_address,
                    "Weight (kg)": order.weight,
                    "Cost (VND)": order.shipping_cost,
                    "Status": order.status,
                    "Created At": order.created_at
                })

            # 3. Create a Pandas DataFrame
            df = pd.DataFrame(data)

            # 4. Save to Excel
            # index=False means we don't save the row numbers (0, 1, 2...)
            df.to_excel(file_path, index=False)
            
            return True, f"Data exported successfully to {file_path}"

        except Exception as e:
            return False, f"Export failed: {str(e)}"
        finally:
            session.close()