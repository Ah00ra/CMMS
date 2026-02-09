from PyQt5 import QtWidgets, uic
import sys
import db_service as db
import jdatetime as jd

class AddFailureDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db

        uic.loadUi("sarlak_add_failure.ui", self) 
        
        now = jd.datetime.now().strftime("%Y-%m-%d")
        self.today_date_sl.setText(now)
        self.insert_failue_sl.clicked.connect(self.on_add_clicked)


    def on_add_clicked(self):
        now = jd.datetime.now().strftime("%Y-%m-%d")

        device_name = self.device_sl.currentText()
        stop_reason = self.stop_reason_sl.currentText()  
        start_time = self.start_time_sl.text()
        duration = self.duration_sl.value()
        desc = self.failure_desc_sl.toPlainText()
        print(device_name, start_time, stop_reason, duration, desc)
        date = jd.datetime.now().strftime("%Y-%m-%d")
        self.db.insert_failure(device_name, date, start_time,stop_reason, duration, desc)
        self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AddFailureDialog()
    win.show()
    sys.exit(app.exec_())
