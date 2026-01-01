import sys
from PyQt5 import QtWidgets, uic
import db_commands as db

from PyQt5.QtCore import Qt
class EquipDetail(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("equip_detail.ui", self) 
        


    def create_table(self, equip_code):
        data = db.get_equip_detail(equip_code)
        location = data['location']
        equip_type = data['equip_type']
        pm_data = data['pm']


        self.equip_codeEdit.setText(str(equip_code))
        self.equip_typeEdit.setText(str(equip_type))
        self.equip_locEdit.setText(str(location))
        # Clear table first
        self.pmTable.setRowCount(0)
        self.pmTable.setLayoutDirection(Qt.RightToLeft)  # RTL layout
        self.pmTable.horizontalHeader().setLayoutDirection(Qt.RightToLeft)  # keep column headers LTR
        
        self.pmTable.setSortingEnabled(True)

        header = self.pmTable.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.pmTable.setHorizontalHeaderLabels(["نام عملیات", "تناوب", "آخرین انجام", "نوبت بعدی", "وضعیت"])

        # Fill table with your data

        for row_idx, (task_name, interval, last_done, next_date, status) in enumerate(pm_data):
            self.pmTable.insertRow(row_idx)
            
            self.pmTable.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(task_name))
            self.pmTable.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(interval)))
            self.pmTable.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(last_done) if last_done else ""))
            self.pmTable.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(next_date))
            self.pmTable.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(status))






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = EquipDetail()
    win.show()
    sys.exit(app.exec_())