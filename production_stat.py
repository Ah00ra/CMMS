# production_stat.py
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
import jdatetime as jd
from db_service import DBService  # Use your existing service!
from add_failure_sl_dialog import AddFailureDialog


class ProductionStats(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db  # Receive db from launcher!
        uic.loadUi("prod_stat_sl.ui", self)
        self.setWindowTitle("آمار تولید")
        self.addFailureBtn.clicked.connect(self.open_add_failure_dialog)

    def open_add_failure_dialog(self):
        dialog = AddFailureDialog(self.db, self)  # pass self as parent
        dialog.exec_()  # opens modal dialog (blocks until closed)



    #     self.load_stats()
    #     self.refreshBtn.clicked.connect(self.load_stats)  # Refresh button
        
    # def load_stats(self):
    #     """Load production statistics from DB"""
    #     try:
    #         # Load failures data (from your original insert_failure function)
    #         failures = self.db.get_failures_stats()  # We'll add this method
    #         self.load_failures_table(failures)
            
    #         # Load other stats
    #         stats_summary = self.db.get_production_summary()
    #         self.update_summary_labels(stats_summary)
            
    #     except Exception as e:
    #         print(f"Error loading stats: {e}")
    #         # TODO: show error popup

    # def load_failures_table(self, failures):
    #     """Fill QTableWidget with failures data"""
    #     self.failuresTable.setRowCount(0)
    #     self.failuresTable.setHorizontalHeaderLabels([
    #         "دستگاه", "تاریخ", "زمان شروع", "علت توقف", 
    #         "مدت (دقیقه)", "توضیحات"
    #     ])
        
    #     for row_idx, failure in enumerate(failures):
    #         self.failuresTable.insertRow(row_idx)
    #         self.failuresTable.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(failure[0]))  # device
    #         self.failuresTable.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(failure[1]))  # tarikh
    #         self.failuresTable.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(failure[2] or ""))  # start_time
    #         self.failuresTable.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(failure[3] or ""))  # stop_reason
    #         self.failuresTable.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(failure[4])))   # duration
    #         self.failuresTable.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(failure[5] or ""))  # description

    # def update_summary_labels(self, summary):
    #     """Update summary labels (total downtime, etc.)"""
    #     self.totalDowntimeLabel.setText(f"{summary['total_hours']} ساعت")
    #     self.avgDowntimeLabel.setText(f"{summary['avg_hours']:.1f} ساعت")
    #     self.topDeviceLabel.setText(summary['top_device'])

if __name__ == "__main__":
    # Quick local test
    from db_service import DBService
    app = QtWidgets.QApplication(sys.argv)
    db = DBService("/home/ahoora/work/CMMS/god.db")
    win = ProductionStats(db)
    win.show()
    sys.exit(app.exec_())
