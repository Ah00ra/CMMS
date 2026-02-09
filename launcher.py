# launcher.py - SIMPLE VERSION
import sys
from PyQt5 import QtWidgets, uic
from db_service import DBService  # Local mode (change to HttpDBService later)
from production_stat import ProductionStats


class Launcher(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("launcher.ui", self)
        
        self.setWindowTitle("CMMS Launcher")
        self.setFixedSize(self.size())
        
        # Create DB service ONCE here
        self.db = DBService("/home/ahoora/work/CMMS/god.db")
        
        # Connect buttons
        self.equipmentsBtn.clicked.connect(self.open_equipments)
        self.productionStatsBtn.clicked.connect(self.open_production_stats)  # Later
    
    def open_production_stats(self):
        production_win = ProductionStats(self.db, self)  # pass self as parent
        production_win.show() 

    def open_equipments(self):
        """Launch Equipment Management app"""
        from main import MainWindow
        self.equipWindow = MainWindow(self.db)
        self.equipWindow.show()
        # self.hide()  # <-- COMMENT OUT to keep launcher visible

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())

    