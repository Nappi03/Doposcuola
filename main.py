import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableView, QDialog, QFormLayout, \
    QLineEdit, QDateEdit, QComboBox, QMessageBox, QHBoxLayout, QLabel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QDate

def create_database():
    conn = sqlite3.connect("studenti.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Studenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nominativo TEXT NOT NULL,
        Classe TEXT NOT NULL,
        Data_Inizio DATE NOT NULL,
        Anticipato BOOLEAN DEFAULT 0,
        Costo REAL NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


class BoolDelegate(QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == 1:
            return "Sì"
        elif value == 0:
            return "No"
        return super().displayText(value, locale)



class CustomSqlTableModel(QSqlTableModel):
    def data(self, index, role=Qt.DisplayRole):
        if index.column() == 3 and role == Qt.DisplayRole:  # Colonna della data
            date_value = super().data(index, role)
            if date_value:
                date = QDate.fromString(date_value, "yyyy-MM-dd")
                return date.toString("dd-MM-yyyy")  # Formato giorno-mese-anno
        return super().data(index, role)



class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super(AddStudentDialog, self).__init__(parent)

        self.setWindowTitle("Aggiungi Studente")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QFormLayout(self)

        font = QFont("Arial", 15)
        label_font = QFont("Arial", 15)

        self.nominativo_label = QLabel("Nominativo:", self)
        self.nominativo_label.setFont(label_font)
        self.classe_label = QLabel("Classe:", self)
        self.classe_label.setFont(label_font)
        self.data_inizio_label = QLabel("Data Inizio:", self)
        self.data_inizio_label.setFont(label_font)
        self.anticipato_label = QLabel("Anticipato:", self)
        self.anticipato_label.setFont(label_font)
        self.costo_label = QLabel("Costo:", self)
        self.costo_label.setFont(label_font)

        self.nominativo_input = QLineEdit(self)
        self.nominativo_input.setFont(font)

        self.classe_input = QLineEdit(self)
        self.classe_input.setFont(font)

        self.data_inizio_input = QDateEdit(self)
        self.data_inizio_input.setCalendarPopup(True)
        self.data_inizio_input.setDate(QDate.currentDate())
        self.data_inizio_input.setFont(font)

        self.anticipato_input = QComboBox(self)
        self.anticipato_input.addItems(["No", "Sì"])
        self.anticipato_input.setFont(font)

        self.costo_input = QLineEdit(self)
        self.costo_input.setFont(font)

        self.layout.addRow(self.nominativo_label, self.nominativo_input)
        self.layout.addRow(self.classe_label, self.classe_input)
        self.layout.addRow(self.data_inizio_label, self.data_inizio_input)
        self.layout.addRow(self.anticipato_label, self.anticipato_input)
        self.layout.addRow(self.costo_label, self.costo_input)

        self.add_button = QPushButton("Aggiungi", self)
        self.add_button.setFont(font)
        self.add_button.clicked.connect(self.add_student)

        self.layout.addWidget(self.add_button)

    def add_student(self):
        nominativo = self.nominativo_input.text()
        classe = self.classe_input.text()
        data_inizio = self.data_inizio_input.date().toString("yyyy-MM-dd")
        anticipato = 1 if self.anticipato_input.currentText() == "Sì" else 0
        costo = float(self.costo_input.text().replace('€ ', '').replace(',', '.'))

        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO Studenti (Nominativo, Classe, Data_Inizio, Anticipato, Costo)
        VALUES (?, ?, ?, ?, ?)
        ''', (nominativo, classe, data_inizio, anticipato, costo))

        conn.commit()
        conn.close()

        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Studenti")
        self.setGeometry(100, 100, 1100, 500)

        self.layout = QVBoxLayout(self)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("studenti.db")
        self.db.open()

        # Usa il modello personalizzato
        self.model = CustomSqlTableModel(self)
        self.model.setTable("Studenti")
        self.model.select()

        # Personalizza le intestazioni
        self.model.setHeaderData(1, Qt.Horizontal, "Nome e Cognome")
        self.model.setHeaderData(2, Qt.Horizontal, "Classe")
        self.model.setHeaderData(3, Qt.Horizontal, "Data Inizio")
        self.model.setHeaderData(4, Qt.Horizontal, "Anticipato")
        self.model.setHeaderData(5, Qt.Horizontal, "Costo")

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSortingEnabled(True)

        font = QFont("Arial", 15)
        self.view.setFont(font)
        self.view.horizontalHeader().setFont(QFont("Arial", 15))

        # Nascondi la colonna ID (indice 0)
        self.view.hideColumn(0)

        # Imposta le larghezze delle colonne
        self.view.setColumnWidth(1, 350)
        self.view.setColumnWidth(2, 200)
        self.view.setColumnWidth(3, 150)
        self.view.setColumnWidth(4, 120)
        self.view.setColumnWidth(5, 100)

        # Applica il delegato BoolDelegate alla colonna "Anticipato" (indice 4)
        self.view.setItemDelegateForColumn(4, BoolDelegate(self))

        self.layout.addWidget(self.view)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Aggiungi Studente", self)
        self.add_button.setFont(QFont("Arial", 14))
        self.add_button.clicked.connect(self.open_add_dialog)

        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Elimina Studente Selezionato", self)
        self.delete_button.setFont(QFont("Arial", 14))
        self.delete_button.clicked.connect(self.delete_student)

        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

    def open_add_dialog(self):
        dialog = AddStudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.model.select()

    def delete_student(self):
        selected_row = self.view.currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Errore", "Seleziona una riga per eliminare uno studente")
            return

        confirm = QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questo studente?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.model.removeRow(selected_row)
            self.model.submitAll()
            self.model.select()




if __name__ == "__main__":
    create_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
