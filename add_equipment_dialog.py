from PyQt5 import QtWidgets, uic
import sys
import db_service as db


class AddEquipmentDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):  # ← ADD db parameter
        super().__init__(parent)
        self.db = db                       # ← STORE db
        uic.loadUi("add_equip_detail.ui", self) 
        
        self.saveButton.clicked.connect(self.add_equip)

    def add_equip(self):
        equip_code = self.serialCode.value()
        location = self.locationEdit.text()
        typ = self.typeComboBox.currentText()
        print(typ)
        stat = self.db.add_new_equipment(equip_code, typ, location)
        if stat == "Duplicated":
            print("Equipment with ", equip_code, "Already Exist!")
            #TODO: popup error message to Raise error
        else:
            print("ADDED")
            self.db.add_pm_tasks_for_equipment(equip_code) 
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AddEquipmentDialog()
    win.show()
    sys.exit(app.exec_())
