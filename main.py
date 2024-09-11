import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableView, QDialog, QFormLayout, \
    QLineEdit, QDateEdit, QComboBox, QHBoxLayout, QLabel, QStyledItemDelegate, QMessageBox
from PyQt5.QtCore import Qt, QDate, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QPainter

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
        Costo REAL NOT NULL,
        settembre BOOLEAN DEFAULT 0,
        ottobre BOOLEAN DEFAULT 0,
        novembre BOOLEAN DEFAULT 0,
        dicembre BOOLEAN DEFAULT 0,
        gennaio BOOLEAN DEFAULT 0,
        febbraio BOOLEAN DEFAULT 0,
        marzo BOOLEAN DEFAULT 0,
        aprile BOOLEAN DEFAULT 0,
        maggio BOOLEAN DEFAULT 0,
        giugno BOOLEAN DEFAULT 0,
        luglio BOOLEAN DEFAULT 0,
        agosto BOOLEAN DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 18:  # Colonna del bottone di eliminazione
            button_rect = option.rect
            painter.save()
            painter.setBrush(Qt.red)
            painter.drawRect(button_rect)
            painter.setPen(Qt.white)
            painter.drawText(button_rect, Qt.AlignCenter, "Elimina")
            painter.restore()
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() == 18 and event.type() == event.MouseButtonRelease:
            # Trova l'ID dello studente nella riga selezionata
            student_id = model.data(model.index(index.row(), 0))
            if student_id:
                self.delete_student(student_id)
                model.removeRow(index.row())
        return super().editorEvent(event, model, option, index)

    def delete_student(self, student_id):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Studenti WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Studenti")
        self.setGeometry(100, 100, 1300, 500)

        self.layout = QVBoxLayout(self)

        # Usa QStandardItemModel
        self.model = QStandardItemModel(0, 19)  # 18 colonne dati + 1 colonna azioni
        self.model.setHorizontalHeaderLabels([
            "ID", "Nome e Cognome", "Classe", "Data Inizio", "Anticipato", "Costo",
            "Settembre", "Ottobre", "Novembre", "Dicembre", "Gennaio", "Febbraio",
            "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Azioni"
        ])

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectItems)
        self.view.setSelectionMode(QTableView.NoSelection)
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSortingEnabled(True)

        font = QFont("Arial", 15)
        self.view.setFont(font)
        self.view.horizontalHeader().setFont(QFont("Arial", 15))

        # Imposta le larghezze delle colonne
        column_widths = [0, 300, 150, 150, 120, 100, 100, 100, 100, 100, 90, 90, 80, 80, 80, 80, 80, 80, 100]
        for i, width in enumerate(column_widths):
            self.view.setColumnWidth(i, width)

        self.view.setItemDelegateForColumn(18, ButtonDelegate(self))  # Delegato per colonna Azioni

        self.layout.addWidget(self.view)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Aggiungi Studente", self)
        self.add_button.setFont(QFont("Arial", 14))
        self.add_button.clicked.connect(self.open_add_dialog)

        self.button_layout.addWidget(self.add_button)
        self.layout.addLayout(self.button_layout)

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Studenti")
        rows = cursor.fetchall()
        conn.close()

        self.model.setRowCount(0)  # Clear existing rows
        for row in rows:
            items = [QStandardItem(str(field)) for field in row]
            items.append(QStandardItem())  # Colonna Azioni
            self.model.appendRow(items)

    def open_add_dialog(self):
        dialog = AddStudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

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

if __name__ == "__main__":
    create_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
