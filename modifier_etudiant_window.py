from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
from models import Etudiant  # Ajoute cet import si tu as la liste des niveaux/filieres dans Etudiant

class ModifierEtudiantWindow(QDialog):
    def __init__(self, etudiant, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Étudiant")
        self.etudiant = etudiant
        layout = QVBoxLayout(self)

        # Nom
        layout.addWidget(QLabel("Nom:"))
        self.nom_input = QLineEdit(etudiant.nom)
        layout.addWidget(self.nom_input)

        # Prénom
        layout.addWidget(QLabel("Prénom:"))
        self.prenom_input = QLineEdit(etudiant.prenom)
        layout.addWidget(self.prenom_input)

        # Date de naissance
        layout.addWidget(QLabel("Date de naissance:"))
        self.date_naissance_input = QDateEdit()
        self.date_naissance_input.setDisplayFormat("yyyy-MM-dd")
        self.date_naissance_input.setDate(QDate.fromString(etudiant.date_naissance, "yyyy-MM-dd"))
        layout.addWidget(self.date_naissance_input)

        # Sexe
        layout.addWidget(QLabel("Sexe:"))
        self.sexe_combo = QComboBox()
        self.sexe_combo.addItems(["F", "H"])
        self.sexe_combo.setCurrentText(etudiant.sexe)
        layout.addWidget(self.sexe_combo)

        # Filière (ComboBox)
        layout.addWidget(QLabel("Filière:"))
        self.filiere_combo = QComboBox()
        # Remplir selon le niveau actuel
        niveaux = Etudiant.NIVEAUX if hasattr(Etudiant, "NIVEAUX") else []
        filieres = []
        if hasattr(Etudiant, "FILIERES"):
            filieres = Etudiant.FILIERES.get(etudiant.niveau, [])
        self.filiere_combo.addItems(filieres)
        self.filiere_combo.setCurrentText(etudiant.filiere)
        layout.addWidget(self.filiere_combo)

        # Niveau (ComboBox)
        layout.addWidget(QLabel("Niveau:"))
        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(niveaux)
        self.niveau_combo.setCurrentText(etudiant.niveau)
        layout.addWidget(self.niveau_combo)

        # Mettre à jour la liste des filières quand le niveau change
        self.niveau_combo.currentTextChanged.connect(self.on_niveau_change)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_sauvegarder = QPushButton("Sauvegarder")
        self.btn_annuler = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_sauvegarder)
        btn_layout.addWidget(self.btn_annuler)
        layout.addLayout(btn_layout)

        self.btn_sauvegarder.clicked.connect(self.accept)
        self.btn_annuler.clicked.connect(self.reject)

    def on_niveau_change(self, niveau):
        self.filiere_combo.clear()
        if hasattr(Etudiant, "FILIERES"):
            filieres = Etudiant.FILIERES.get(niveau, [])
            self.filiere_combo.addItems(filieres)

    def get_donnees(self):
        return {
            "nom": self.nom_input.text(),
            "prenom": self.prenom_input.text(),
            "date_naissance": self.date_naissance_input.date().toString("yyyy-MM-dd"),
            "sexe": self.sexe_combo.currentText(),
            "filiere": self.filiere_combo.currentText(),
            "niveau": self.niveau_combo.currentText()
        }