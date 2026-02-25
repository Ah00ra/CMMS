from PyQt5 import QtWidgets, uic
import sys
import db_service as db
import jdatetime as jd

from PyQt5.QtWidgets import QLineEdit, QMessageBox
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression
import jdatetime as jd

class JalaliDateEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("1403-12-25")

        # Fixed regex - escape properly for 1400-1499 range
        regex = QRegularExpression(r"1[4-5]\d{2}-(0[1-9]|1[0-2])-(0?[1-9]|[12]?\d|3[01])?")
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        text = self.text().strip()
        if text and not self.is_valid_jalali(text):
            QMessageBox.warning(self, "خطا", "تاریخ جلالی معتبر نیست")
            self.setFocus()

    def is_valid_jalali(self, date_str):
        try:
            jd.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_jalali_date(self):
        text = self.text().strip()
        if not self.is_valid_jalali(text):
            return None
        return jd.datetime.strptime(text, "%Y-%m-%d").date()


    def get_date_string(self):
        text = self.text().strip()
        if not self.is_valid_jalali(text):
            return None
        
        # FIX: Always normalize to YYYY-MM-DD format
        date_obj = jd.datetime.strptime(text, "%Y-%m-%d").date()
        return date_obj.strftime("%Y-%m-%d")  # Always "1404-12-03"

    def set_jalali_date(self, jalali_date):
        if isinstance(jalali_date, jd.date):
            self.setText(jalali_date.strftime("%Y-%m-%d"))



class AddFailureDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db

        uic.loadUi("sarlak_add_failure.ui", self) 
        
        today = jd.datetime.now().date()
        self.date_edit.set_jalali_date(today)
        # self.date_input.set_jalali_date(today)
        self.insert_failue_sl.clicked.connect(self.on_add_clicked)


    def on_add_clicked(self):
        now = jd.datetime.now().strftime("%Y-%m-%d")
        date_str = self.date_edit.get_date_string()
        if not date_str:
                QMessageBox.warning(self, "خطا", "لطفاً تاریخ معتبر وارد کنید")
                return



        device_name = self.device_sl.currentText()
        stop_reason = self.stop_reason_sl.currentText()  
        start_time = self.start_time_sl.text()
        duration = self.duration_sl.value()
        desc = self.failure_desc_sl.toPlainText()


        print(f"Adding failure: {device_name}, {date_str}, {start_time}, {stop_reason}, {duration}, {desc}")
        date = jd.datetime.now().strftime("%Y-%m-%d")

        self.db.insert_failure(device_name, date_str, start_time, stop_reason, duration, desc)
        self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AddFailureDialog()
    win.show()
    sys.exit(app.exec_())
