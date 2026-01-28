import sys
from PyQt5 import QtWidgets, uic
from db_service import DBService
from add_equipment_dialog import AddEquipmentDialog
from equip_detail import EquipDetail
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox
#from PyQt5.QtGui import QColor

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        uic.loadUi("main_window.ui", self)      # main.ui from Qt Designer
        self.setWindowTitle("لیست تجهیزات و دستگاه های شیما کفش")
        #self.refreshBut.clicked.connect(self.load_equips_table)
        self.load_equips_table()
        self.addEquipmentButton.clicked.connect(self.open_add_equipment_dialog) 
        self.equipmentTable.itemDoubleClicked.connect(self.equip_double_clicked)

        self.equipmentTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.equipmentTable.customContextMenuRequested.connect(self.open_context_menu)

    def load_equips_table(self):
        equips = self.db.load_equipment_table()
        self.equipmentTable.verticalHeader().setVisible(False)
        self.equipmentTable.setRowCount(0)
        self.equipmentTable.setSortingEnabled(True)

        header = self.equipmentTable.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        for row_idx, (code, loc, typ) in enumerate(equips):
            
            #TODO: this_priority = db.get_equip_priority(code)
            self.equipmentTable.insertRow(row_idx)
            self.equipmentTable.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(code)))
            self.equipmentTable.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(loc))
            self.equipmentTable.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(typ))
            # self.equipmentTable.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(this_priority)))


    def open_add_equipment_dialog(self):
        dialog = AddEquipmentDialog(self.db, self)  # pass self as parent
        dialog.exec_()  # opens modal dialog (blocks until closed)
        #refresh and reaload equipmetn table
        self.load_equips_table()
    

    def equip_double_clicked(self, item):
        row = item.row()    
        equip_code_item = self.equipmentTable.item(row, 3)
        equip_code = equip_code_item.text()

        detail = EquipDetail(self.db, self)
        detail.create_table(equip_code)
        detail.show()  

    def open_context_menu(self, position):
        index = self.equipmentTable.indexAt(position)
        if not index.isValid():
            return

        row = index.row()
        equip_code = self.equipmentTable.item(row, 3).text()  # ستون کد دستگاه

        menu = QMenu(self)

        #open_action = QAction("🔍 Open device", self)
        delete_action = QAction("🗑 Delete device", self)

        #open_action.triggered.connect(
            #lambda: self.show_write_device_detail(equip_code)
        #)

        delete_action.triggered.connect(
            lambda: self.delete_device(equip_code)
        )

        #menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec_(self.equipmentTable.viewport().mapToGlobal(position))

    def delete_device(self, equip_code):
        reply = QMessageBox.question(
            self,
            "Delete device",
            f"Are you sure you want to delete device {equip_code}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.db.delete_equipment(equip_code)
        
        self.load_equips_table()
        pass

if __name__ == "__main__":
    
    # app = QtWidgets.QApplication(sys.argv)
    # db = DBService("/home/ahoora/work/CMMS/god.db")
    # win = MainWindow(db)
    # win.show()
    # sys.exit(app.exec_())
    from http_service import HttpDBService  # NEW - for server mode
    
    app = QtWidgets.QApplication(sys.argv)
    
    # TEMPORARY: test HTTP mode (FastAPI server must be running!)
    # db = HttpDBService("http://127.0.0.1:8000")
    
    # To switch back to local SQLite, use:
    # from db_service import DBService
    db = DBService("/home/ahoora/work/CMMS/god.db")
    
    win = MainWindow(db)
    win.show()
    sys.exit(app.exec_())
