import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableView, QDialog, QFormLayout, \
    QLineEdit, QDateEdit, QComboBox, QHBoxLayout, QLabel, QStyledItemDelegate, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt, QDate, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont


# Funzione per creare il database
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


class MonthDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MonthDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(["No", "Sì"])
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentIndex(1 if value == "Sì" else 0)  # Imposta l'editor per "Sì" o "No"

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

        # Aggiorna il valore nel database
        row = index.row()
        col = index.column()
        student_id = model.data(model.index(row, 0))  # Ottieni l'ID dello studente
        self.update_database(student_id, col, 1 if value == "Sì" else 0)

    def update_database(self, student_id, month_column, value):
        month_columns = ["settembre", "ottobre", "novembre", "dicembre", "gennaio",
                         "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto"]

        month_name = month_columns[month_column - 6]  # Le colonne 6-17 corrispondono ai mesi

        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        query = f"UPDATE Studenti SET {month_name} = ? WHERE id = ?"
        cursor.execute(query, (value, student_id))
        conn.commit()
        conn.close()


class ClassDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ClassDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        # Usa un QLineEdit per modificare la classe
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        # Imposta il valore attuale della classe nell'editor
        value = index.data(Qt.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        # Ottieni il nuovo valore dall'editor e aggiorna il modello
        value = editor.text().strip()
        model.setData(index, value, Qt.EditRole)

        # Aggiorna il valore nel database
        row = index.row()
        student_id = model.data(model.index(row, 0))  # Ottieni l'ID dello studente
        self.update_database(student_id, value)

    def update_database(self, student_id, new_class):
        # Aggiorna il campo "Classe" nel database
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        query = "UPDATE Studenti SET Classe = ? WHERE id = ?"
        cursor.execute(query, (new_class, student_id))
        conn.commit()
        conn.close()


class AnticipatoDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(AnticipatoDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(["No", "Sì"])
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentIndex(1 if value == "Sì" else 0)  # Imposta "Sì" o "No"

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

        # Aggiorna il valore nel database
        row = index.row()
        student_id = model.data(model.index(row, 0))  # Ottieni l'ID dello studente
        self.update_database(student_id, 1 if value == "Sì" else 0)

    def update_database(self, student_id, anticipato_value):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        query = "UPDATE Studenti SET Anticipato = ? WHERE id = ?"
        cursor.execute(query, (anticipato_value, student_id))
        conn.commit()
        conn.close()


class CostDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(CostDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        # Usa un QLineEdit per permettere la modifica del costo
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        # Imposta il valore attuale nell'editor
        value = index.data(Qt.DisplayRole)
        value = value.replace('€ ', '')  # Rimuovi il simbolo dell'euro per l'editing
        editor.setText(value)

    def setModelData(self, editor, model, index):
        # Ottieni il nuovo valore dall'editor
        value = editor.text().replace(',', '.').strip()  # Rimuovi eventuali spazi bianchi e correggi i decimali
        try:
            value_float = float(value)  # Verifica che sia un numero valido
        except ValueError:
            QMessageBox.warning(None, "Errore", "Il costo inserito non è valido!")
            return

        # Formatta il valore come euro e aggiornalo nel modello
        formatted_value = f"€ {value_float:.2f}"
        model.setData(index, formatted_value, Qt.EditRole)

        # Aggiorna il valore nel database
        row = index.row()
        student_id = model.data(model.index(row, 0))  # Ottieni l'ID dello studente
        self.update_database(student_id, value_float)

    def update_database(self, student_id, new_cost):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        query = "UPDATE Studenti SET Costo = ? WHERE id = ?"
        cursor.execute(query, (new_cost, student_id))
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

        # Crea il QTabWidget
        self.tabs = QTabWidget()

        # Tab per la tabella degli studenti
        self.student_tab = QWidget()
        self.student_tab_layout = QVBoxLayout(self.student_tab)

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
        self.view.setEditTriggers(QTableView.DoubleClicked | QTableView.SelectedClicked)
        self.view.setSortingEnabled(True)

        font = QFont("Arial", 12)
        self.view.setFont(font)
        self.view.horizontalHeader().setFont(QFont("Arial", 12))

        # Imposta le larghezze delle colonne
        column_widths = [0, 250, 120, 120, 100, 90, 90, 90, 90, 90, 80, 80, 80, 80, 80, 80, 80, 80, 80]
        for i, width in enumerate(column_widths):
            self.view.setColumnWidth(i, width)

        # Delegato per i mesi
        for col in range(6, 18):
            self.view.setItemDelegateForColumn(col, MonthDelegate(self))

        # Delegato per la colonna azioni
        self.view.setItemDelegateForColumn(18, ButtonDelegate(self))

        # Delegato per la colonna del costo (colonna 5)
        self.view.setItemDelegateForColumn(5, CostDelegate(self))

        # Delegato per la colonna della classe (colonna 2)
        self.view.setItemDelegateForColumn(2, ClassDelegate(self))

        # Delegato per la colonna anticipato (colonna 4)
        self.view.setItemDelegateForColumn(4, AnticipatoDelegate(self))

        self.student_tab_layout.addWidget(self.view)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Aggiungi Studente", self)
        self.add_button.setFont(QFont("Arial", 12))
        self.add_button.clicked.connect(self.open_add_dialog)
        self.button_layout.addWidget(self.add_button)
        self.student_tab_layout.addLayout(self.button_layout)

        # Aggiungi la scheda con la tabella al QTabWidget
        self.tabs.addTab(self.student_tab, "Studenti")

        # Scheda economia
        self.economy_tab = EconomyTab()
        self.tabs.addTab(self.economy_tab, "Economia")

        self.layout.addWidget(self.tabs)

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Studenti")
        rows = cursor.fetchall()
        conn.close()

        self.model.setRowCount(0)  # Clear existing rows
        for row in rows:
            row = list(row)  # Convert to a mutable list
            row[4] = "Sì" if row[4] == 1 else "No"  # Convert 1 to 'Sì' and 0 to 'No'

            # Aggiungi il simbolo dell'euro al valore del costo
            row[5] = f"€ {row[5]:.2f}"  # Formatta il costo con il simbolo dell'euro e due decimali

            # Modifica per formattare la data come giorno-mese-anno
            row[3] = QDate.fromString(row[3], "yyyy-MM-dd").toString("dd/MM/yyyy")

            for i in range(6, 18):
                row[i] = "Sì" if row[i] == 1 else "No"  # Converti 1 a 'Sì' e 0 a 'No'

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

        font = QFont("Arial", 12)
        label_font = QFont("Arial", 12)

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


class EconomyTab(QWidget):
    def __init__(self, parent=None):
        super(EconomyTab, self).__init__(parent)
        self.setWindowTitle("Economia")
        self.setGeometry(100, 100, 1200, 500)

        self.layout = QVBoxLayout(self)

        # Usa QStandardItemModel per la tabella economica
        self.economy_model = QStandardItemModel(0, 13)  # 12 mesi + Totale
        self.economy_model.setHorizontalHeaderLabels([
            "Settembre", "Ottobre", "Novembre",
            "Dicembre", "Gennaio", "Febbraio", "Marzo",
            "Aprile", "Maggio", "Giugno", "Luglio",
            "Agosto", "Totale assoluto"
        ])

        self.economy_view = QTableView(self)
        self.economy_view.setModel(self.economy_model)
        self.economy_view.setSortingEnabled(True)
        self.economy_view.horizontalHeader().setFont(QFont("Arial", 12))
        self.economy_view.setFont(QFont("Arial", 12))

        # Imposta le larghezze delle colonne
        column_widths = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 120]
        for i, width in enumerate(column_widths):
            self.economy_view.setColumnWidth(i, width)

        self.layout.addWidget(self.economy_view)

        # Carica i dati economici
        self.load_economy_data()

    def load_economy_data(self):
        conn = sqlite3.connect("studenti.db")
        cursor = conn.cursor()

        # Calcola il totale per ogni mese
        month_columns = ["settembre", "ottobre", "novembre", "dicembre", "gennaio",
                         "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto"]

        totals = {month: 0.0 for month in month_columns}

        for month in month_columns:
            cursor.execute(f'''
            SELECT SUM(Costo) FROM Studenti WHERE {month} = 1
            ''')
            result = cursor.fetchone()[0]
            totals[month] = result if result else 0.0

        total = sum(totals.values())

        # Inserisci i dati nella tabella
        row_data = [f"€ {totals[month]:.2f}" for month in month_columns] + [f"€ {total:.2f}"]
        self.economy_model.setRowCount(0)  # Clear existing rows
        row_items = [QStandardItem(data) for data in row_data]
        self.economy_model.appendRow(row_items)

        conn.close()


if __name__ == "__main__":
    try:
        #create_database()

        app = QApplication(sys.argv)
        window = MainWindow()
        window.showMaximized()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
