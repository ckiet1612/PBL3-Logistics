# ui/dashboard_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Create a Matplotlib Figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def update_chart(self, orders):
        """
        Receive list of orders, process data, and redraw the chart.
        """
        # 1. Process Data: Count orders by Status
        status_counts = {}
        total_revenue = 0.0
        
        for order in orders:
            status = order.status or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
            total_revenue += order.shipping_cost

        # 2. Prepare data for plotting
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        
        # 3. Clear previous chart
        self.figure.clear()
        
        # 4. Draw Pie Chart
        ax = self.figure.add_subplot(111)
        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax.set_title(f"Order Status Distribution\nTotal Revenue: {total_revenue:,.0f} VND")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha='center')

        # 5. Refresh canvas
        self.canvas.draw()