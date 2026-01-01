import sys
from PyQt5 import QtWidgets, uic
import db_commands as db
from add_equipment_dialog import AddEquipmentDialog

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_window.ui", self)      # main.ui from Qt Designer
        self.refreshBut.clicked.connect(self.load_equips_table)
        self.addEquipmentButton.clicked.connect(self.open_add_equipment_dialog) 



    def load_equips_table(self):
        equips = db.load_equipment_table()
        self.equipmentTable.verticalHeader().setVisible(False)
        self.equipmentTable.setRowCount(0)
        self.equipmentTable.setSortingEnabled(True)

        header = self.equipmentTable.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        for row_idx, (code, loc, typ) in enumerate(equips):
            # this_priority = db.get_equip_priority(code)
            self.equipmentTable.insertRow(row_idx)
            self.equipmentTable.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(code)))
            self.equipmentTable.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(loc))
            self.equipmentTable.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(typ))
            # self.equipmentTable.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(this_priority)))
    # def open_add_equipment_dialog(self):
    
    # dialog = AddEquipmentDialog(self)  # pass self as parent
    # dialog.exec_()  # opens modal dialog (blocks until closed)

    def open_add_equipment_dialog(self):
        dialog = AddEquipmentDialog(self)  # pass self as parent
        dialog.exec_()  # opens modal dialog (blocks until closed)
        #refresh and reaload equipmetn table
        self.load_equips_table()
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
