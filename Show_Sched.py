import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QPushButton, 
                             QVBoxLayout, 
                             QHBoxLayout, 
                             QWidget, 
                             QTableView,
                             )
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

class Show_Sched(QMainWindow):
    def __init__(self):
        super().__init__()
     
        #QMainWindow().__init__(self,parent)
        #self.parent = parent
        self.setWindowTitle("pyNFL Divisions")
        self.setFont(QFont('Arial',16))
        self.resize(382, 350)


        # Create database connection
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("PyNFL.db")
        if not db.open():
            QMessageBox.critical(None,"Database Error {}".format(db.lastError().text()))
            sys.exit(1)

        # Create QSqlTableModel
        self.model = QSqlTableModel()
        self.model.setTable("schedule")

        query = QSqlQuery()
        query.exec_('select week, away_team, home_team from schedule order by week')
        self.model.setQuery(query)

        self.model.select()

        self.model.setHeaderData(0, Qt.Horizontal, "Week")  # Set header for the first column
        self.model.setHeaderData(1,Qt.Horizontal,"Away")
        self.model.setHeaderData(2,Qt.Horizontal,"Home")

        # Create a table view to display model contents
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()
        #self.view.hideColumn(0)
        font = self.view.font()
        for col in range(self.model.columnCount()):
            max_width = 0
            for row in range(self.model.rowCount()):
                index = self.model.index(row,col)
                text = str(index.data())
                metrics = QFontMetrics(font)
                width = metrics.boundingRect(text).width() + 20
                max_width = max(max_width,width)
            self.view.setColumnWidth(col,max_width)

        # Set up layout
        main_layout = QVBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        lay2 = QHBoxLayout()

        main_layout.addLayout(layout)
        main_layout.addLayout(lay2)

        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = Show_Sched()
    window.show()
    sys.exit(app.exec_())

