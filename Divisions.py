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
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

class View_Divisions(QMainWindow):
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
        self.model.setTable("divisions")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.setHeaderData(0, Qt.Horizontal, "Div Code")  # Set header for the first column
        self.model.setHeaderData(1,Qt.Horizontal,"Name")
        self.model.setHeaderData(2,Qt.Horizontal,"Conf Code")
        self.model.select()

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

        # Create a button to submit changes
        submit_button = QPushButton("Submit Changes")
        submit_button.clicked.connect(self.submit_changes)
        del_button = QPushButton("Delete Row")
        del_button.clicked.connect(self.delete_row)
        add_button = QPushButton("Add Row")
        add_button.clicked.connect(self.add_row)

        # Set up layout
        main_layout = QVBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        lay2 = QHBoxLayout()
        lay2.addWidget(submit_button)
        lay2.addWidget(add_button)
        lay2.addWidget(del_button)

        main_layout.addLayout(layout)
        main_layout.addLayout(lay2)

        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def submit_changes(self):
        if self.model.submitAll():
            print("Changes submitted successfully")
        else:
            print("Error submitting changes:", self.model.lastError().text())

    def add_row(self):
        row = self.model.rowCount()
        record = self.model.record()
        #record.setGenerated('player_id', False)    # primary key
        self.model.insertRecord(row, record)

    def delete_row(self):
        indices = self.view.selectionModel().selectedIndexes()
        if len(set(index.column() for index in indices)) == 1:
            rows_to_remove = set(index.row() for index in indices)
            model = self.model
            for row in sorted(rows_to_remove, reverse=True):
                model.removeRow(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = View_Divisions()
    window.show()
    sys.exit(app.exec_())

