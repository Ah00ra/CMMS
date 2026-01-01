import sys
from PyQt5 import QtWidgets, uic
import db_commands as db
import jdatetime as jd
from PyQt5.QtCore import Qt


class EquipDetail(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("equip_detail.ui", self) 
        self.doneBtn.setEnabled(False)
        self.editBtn.setEnabled(False) 
        self.doneBtn.clicked.connect(self.mark_this_pm_done)
        self.pmTable.itemSelectionChanged.connect(self.on_pm_row_selected)

    def on_pm_row_selected(self):
        selected = self.pmTable.selectionModel().hasSelection()
        self.doneBtn.setEnabled(selected)
        self.editBtn.setEnabled(selected)


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
            if status == True:
                self.pmTable.setItem(row_idx, 4, QtWidgets.QTableWidgetItem("فعال"))
            else:
                self.pmTable.setItem(row_idx, 4, QtWidgets.QTableWidgetItem("غیر فعال"))


    def mark_this_pm_done(self):
        row = self.pmTable.currentRow()
        if row < 0:
            print("NOTHING SELECTED")
            return None

        # a = self.pmTable.item(row, 4).text()  
        now = jd.datetime.now().strftime("%Y-%m-%d")
        task_name = self.pmTable.item(row, 0).text()
        equip_code = self.equip_codeEdit.text()
        print(task_name, equip_code, now)
        db.mark_a_pm_done(equip_code, task_name, now)
        self.create_table(equip_code)





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = EquipDetail()
    win.show()
    sys.exit(app.exec_())