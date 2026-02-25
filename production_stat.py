# production_stat.py
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
import jdatetime as jd
from db_service import DBService  # Use your existing service!
from add_failure_sl_dialog import AddFailureDialog
from PyQt5.QtCore import pyqtSignal


import jdatetime as jd


class ProductionStats(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db  # Receive db from launcher!
        uic.loadUi("prod_stat_sl.ui", self)
        self.setWindowTitle("آمار تولید")
        self.addFailureBtn.clicked.connect(self.open_add_failure_dialog)
        self.cmb_period_filter.currentTextChanged.connect(self.load_table_data)

        self.prodTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.prodTable.customContextMenuRequested.connect(self.on_table_context_menu)

        self.load_table_data()

    def get_date_range(self,option):
        today = jd.date.today()
        if option == "امروز":
            return today, today

        elif option == "هفته اخیر":
            return today - jd.timedelta(days=7), today

        elif option == "ماه اخیر":
            return today - jd.timedelta(days=30), today

        elif option == "سه ماه اخیر":
            return today - jd.timedelta(days=90), today

        elif option == "سال اخیر":
            return today - jd.timedelta(days=180), today

        elif option == "شیش ماه اخیر":
            return today - jd.timedelta(days=365), today

        elif option == "نمایش همه":
            return None, None


    # def apply_period_filter(self):
    #     period = self.cmb_period_filter.currentText()
    #     print(period)
    #     from_date, to_date = self.get_date_range("امروز")
    #     print(from_date, to_date)
    #     rows = self.db.get_all_failures_sl(from_date, to_date)   
    #     print(rows, "****")

    def load_table_data(self):
        period = self.cmb_period_filter.currentText()
        from_date, to_date = self.get_date_range(period)
        rows = self.db.get_all_failures_sl(from_date, to_date)   
        #rows = self.db.get_all_failures_sl()   

        # 2) Configure table
        self.prodTable.clearContents()
        self.prodTable.setRowCount(0)
        self.prodTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.prodTable.setColumnHidden(0, True) 


        self.prodTable.setColumnCount(7)
        self.prodTable.setHorizontalHeaderLabels([
            "ID", "دستگاه", "تاریخ", "زمان شروع", "علت توقف", "مدت", "توضیحات"
         ])
        # 3) Fill table
        for row_idx, row in enumerate(rows):
            self.prodTable.insertRow(row_idx)
            for col_idx, value in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(value) if value is not None else "")
                self.prodTable.setItem(row_idx, col_idx, item)


    def open_add_failure_dialog(self):
        dialog = AddFailureDialog(self.db, self)  # pass self as parent
        dialog.exec_()  # opens modal dialog (blocks until closed)
        self.load_table_data()


    def on_table_context_menu(self, pos):
        index = self.prodTable.indexAt(pos)
        if not index.isValid():
            return

        menu = QtWidgets.QMenu(self)
        delete_action = menu.addAction("حذف این خرابی")
        action = menu.exec_(self.prodTable.viewport().mapToGlobal(pos))

        if action == delete_action:
            self.delete_selected_failure()


    def delete_selected_failure(self):
        row = self.prodTable.currentRow()
        if row < 0:
            return

        id_item = self.prodTable.item(row, 0)  # hidden ID column
        if not id_item:
            return

        failure_id = int(id_item.text())

        reply = QtWidgets.QMessageBox.question(
            self,
            "تایید حذف",
            "این خرابی حذف شود؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        if self.db.delete_failure(failure_id):
            # remove from UI
            self.prodTable.removeRow(row)
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "خطا",
                "حذف در دیتابیس انجام نشد."
            )




if __name__ == "__main__":
    # Quick local test
    from db_service import DBService
    app = QtWidgets.QApplication(sys.argv)
    db = DBService("/home/ahoora/work/CMMS/god.db")
    win = ProductionStats(db)
    win.show()
    sys.exit(app.exec_())
