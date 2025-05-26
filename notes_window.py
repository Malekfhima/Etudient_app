from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from database import Database
from models import Note, Matiere, ResultatEtudiant, Etudiant

class NotesWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
        self.selected_etudiant = None
        self.matieres = []
        self.current_trimestre = 1
        self.statusBar()  # Créer la barre de statut

    def setup_ui(self):
        self.setWindowTitle("Gestion des Notes")
        self.setMinimumSize(1200, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Section de filtrage
        filter_layout = QHBoxLayout()
        
        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(Etudiant.NIVEAUX)
        
        self.filiere_combo = QComboBox()
        
        # Ajout du sélecteur de trimestre
        self.trimestre_combo = QComboBox()
        self.trimestre_combo.addItems(['Trimestre 1', 'Trimestre 2', 'Trimestre 3'])
        
        filter_layout.addWidget(QLabel("Niveau:"))
        filter_layout.addWidget(self.niveau_combo)
        filter_layout.addWidget(QLabel("Filière:"))
        filter_layout.addWidget(self.filiere_combo)
        filter_layout.addWidget(QLabel("Trimestre:"))
        filter_layout.addWidget(self.trimestre_combo)
        filter_layout.addStretch()
        
        # Bouton de rafraîchissement
        self.btn_refresh = QPushButton("Rafraîchir la liste")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        filter_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(filter_layout)
        
        # Table des étudiants
        self.table_etudiants = QTableWidget()
        self.table_etudiants.setColumnCount(9)
        self.table_etudiants.setHorizontalHeaderLabels([
            "Matricule", "Nom", "Prénom", 
            "Moyenne T1", "Moyenne T2", "Moyenne T3",
            "Moyenne Générale", "Mention", "Action"
        ])
        self.table_etudiants.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_etudiants.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_etudiants.setSelectionMode(QTableWidget.SingleSelection)
        self.table_etudiants.setAlternatingRowColors(True)
        main_layout.addWidget(self.table_etudiants)
        
        # Section des notes
        notes_layout = QVBoxLayout()
        
        notes_header = QHBoxLayout()
        notes_header.addWidget(QLabel("Notes de l'étudiant"))
        self.etudiant_label = QLabel("")
        notes_header.addWidget(self.etudiant_label)
        notes_header.addStretch()
        
        notes_layout.addLayout(notes_header)
        
        # Table des notes
        self.table_notes = QTableWidget()
        self.table_notes.setColumnCount(5)
        self.table_notes.setHorizontalHeaderLabels([
            "Matière", "Coefficient", "Note CC", "Note Examen", "Moyenne"
        ])
        self.table_notes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_notes.setAlternatingRowColors(True)
        notes_layout.addWidget(self.table_notes)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        self.btn_enregistrer = QPushButton("Enregistrer les notes")
        self.btn_calculer = QPushButton("Calculer les moyennes")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_calculer)
        buttons_layout.addWidget(self.btn_enregistrer)
        notes_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(notes_layout)
        
        # Connexions des signaux
        self.niveau_combo.currentTextChanged.connect(self.niveau_change)
        self.filiere_combo.currentTextChanged.connect(self.filiere_change)
        self.trimestre_combo.currentIndexChanged.connect(self.trimestre_change)
        self.btn_refresh.clicked.connect(self.rafraichir_liste)
        self.btn_calculer.clicked.connect(self.calculer_moyennes)
        self.btn_enregistrer.clicked.connect(self.enregistrer_notes)
        
        # Initialiser les filières
        self.niveau_change(self.niveau_combo.currentText())

    def rafraichir_liste(self):
        """Force le rechargement de la liste des étudiants"""
        try:
            niveau = self.niveau_combo.currentText()
            filiere = self.filiere_combo.currentText()
            
            if niveau and filiere:
                self.charger_classement()
                self.statusBar().showMessage("Liste des étudiants rafraîchie", 3000)
        except Exception as e:
            print(f"Erreur lors du rafraîchissement: {str(e)}")
            QMessageBox.critical(self, "Erreur", "Impossible de rafraîchir la liste des étudiants")

    def niveau_change(self, niveau):
        """Met à jour les filières disponibles en fonction du niveau sélectionné"""
        try:
            self.filiere_combo.clear()
            if niveau in Etudiant.FILIERES:
                self.filiere_combo.addItems(Etudiant.FILIERES[niveau])
                print(f"Filières chargées pour {niveau}: {Etudiant.FILIERES[niveau]}")  # Debug
            self.charger_classement()
        except Exception as e:
            print(f"Erreur dans niveau_change: {str(e)}")  # Debug
            QMessageBox.critical(self, "Erreur", f"Erreur lors du changement de niveau : {str(e)}")

    def filiere_change(self, filiere):
        """Met à jour la liste des étudiants quand la filière change"""
        try:
            if filiere:  # Vérifier que la filière n'est pas vide
                print(f"Changement de filière vers: {filiere}")  # Debug
                self.charger_classement()
        except Exception as e:
            print(f"Erreur dans filiere_change: {str(e)}")  # Debug
            QMessageBox.critical(self, "Erreur", f"Erreur lors du changement de filière : {str(e)}")

    def trimestre_change(self, index):
        self.current_trimestre = index + 1
        if self.selected_etudiant:
            self.afficher_notes(self.selected_etudiant)

    def charger_classement(self):
        """Charge et affiche les étudiants selon le niveau et la filière sélectionnés"""
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()
        
        if not niveau or not filiere:
            self.table_etudiants.setRowCount(0)
            return
            
        try:
            print(f"Chargement des étudiants pour {niveau} - {filiere}")
            
            # Récupérer tous les étudiants
            tous_etudiants = self.db.get_all_etudiants()
            print(f"Nombre total d'étudiants: {len(tous_etudiants)}")
            
            # Filtrer les étudiants
            etudiants_filtres = [
                etudiant for etudiant in tous_etudiants
                if etudiant.niveau == niveau and etudiant.filiere == filiere
            ]
            print(f"Nombre d'étudiants filtrés: {len(etudiants_filtres)}")
            
            # Mettre à jour le tableau
            self.table_etudiants.setRowCount(len(etudiants_filtres))
            
            for row, etudiant in enumerate(etudiants_filtres):
                # Calculer les moyennes par trimestre
                moyennes_trim = self.calculer_moyennes_trimestres(etudiant.matricule)
                
                # Calculer la moyenne générale
                if all(trim in moyennes_trim for trim in [1, 2, 3]):
                    moyenne_generale = (moyennes_trim[1] + moyennes_trim[2] + (2 * moyennes_trim[3])) / 4
                else:
                    moyenne_generale = 0.0
                
                # Déterminer la mention
                mention = ResultatEtudiant.calculer_mention(moyenne_generale)
                
                # Créer et ajouter les items
                items = [
                    QTableWidgetItem(etudiant.matricule),
                    QTableWidgetItem(etudiant.nom),
                    QTableWidgetItem(etudiant.prenom),
                    QTableWidgetItem(f"{moyennes_trim.get(1, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyennes_trim.get(2, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyennes_trim.get(3, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyenne_generale:.2f}"),
                    QTableWidgetItem(mention)
                ]
                
                for col, item in enumerate(items):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table_etudiants.setItem(row, col, item)
                
                # Ajouter le bouton Gérer les notes
                btn_notes = QPushButton("Gérer les notes")
                btn_notes.clicked.connect(lambda checked, e=etudiant: self.afficher_notes(e))
                self.table_etudiants.setCellWidget(row, 8, btn_notes)
            
            # Message de statut
            if etudiants_filtres:
                self.statusBar().showMessage(f"{len(etudiants_filtres)} étudiant(s) trouvé(s) pour {niveau} - {filiere}")
            else:
                self.statusBar().showMessage(f"Aucun étudiant trouvé pour {niveau} - {filiere}")
                
        except Exception as e:
            print(f"Erreur dans charger_classement: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les étudiants: {str(e)}")
            self.statusBar().showMessage("Erreur lors du chargement des étudiants")

    def calculer_moyennes_trimestres(self, matricule):
        """Calcule les moyennes pour chaque trimestre"""
        try:
            notes_par_matiere = self.db.get_notes_etudiant(matricule)
            moyennes_trim = {1: 0.0, 2: 0.0, 3: 0.0}
            coef_total = {1: 0, 2: 0, 3: 0}
            
            for matiere_id, notes_trimestres in notes_par_matiere.items():
                # Récupérer le coefficient de la matière
                cursor = self.db.conn.execute("SELECT coefficient FROM matieres WHERE id = ?", (matiere_id,))
                coef = cursor.fetchone()[0]
                
                for trim, note in notes_trimestres.items():
                    if note.moyenne is not None:
                        moyennes_trim[trim] += note.moyenne * coef
                        coef_total[trim] += coef
            
            # Calculer les moyennes finales par trimestre
            for trim in moyennes_trim:
                if coef_total[trim] > 0:
                    moyennes_trim[trim] = moyennes_trim[trim] / coef_total[trim]
                    
            return moyennes_trim
        except Exception as e:
            print(f"Erreur calcul moyennes trimestres: {str(e)}")
            return {1: 0.0, 2: 0.0, 3: 0.0}

    def afficher_notes(self, etudiant):
        self.selected_etudiant = etudiant
        self.etudiant_label.setText(f"{etudiant.nom} {etudiant.prenom} ({etudiant.matricule})")
        
        try:
            # Récupérer les matières pour ce niveau et cette filière
            self.matieres = self.db.get_matieres(etudiant.niveau, etudiant.filiere)
            
            # Récupérer les notes existantes
            notes = self.db.get_notes_etudiant(etudiant.matricule)
            
            # Remplir la table des notes
            self.table_notes.setRowCount(len(self.matieres))
            
            for row, matiere in enumerate(self.matieres):
                # Matière et coefficient
                self.table_notes.setItem(row, 0, QTableWidgetItem(matiere.nom))
                self.table_notes.setItem(row, 1, QTableWidgetItem(str(matiere.coefficient)))
                
                # Note CC
                note_cc = QDoubleSpinBox()
                note_cc.setRange(0, 20)
                note_cc.setDecimals(2)
                if matiere.id in notes and self.current_trimestre in notes[matiere.id]:
                    note = notes[matiere.id][self.current_trimestre]
                    if note.note_cc is not None:
                        note_cc.setValue(note.note_cc)
                self.table_notes.setCellWidget(row, 2, note_cc)
                
                # Note Examen
                note_exam = QDoubleSpinBox()
                note_exam.setRange(0, 20)
                note_exam.setDecimals(2)
                if matiere.id in notes and self.current_trimestre in notes[matiere.id]:
                    note = notes[matiere.id][self.current_trimestre]
                    if note.note_exam is not None:
                        note_exam.setValue(note.note_exam)
                self.table_notes.setCellWidget(row, 3, note_exam)
                
                # Moyenne (calculée)
                moyenne = QTableWidgetItem()
                if matiere.id in notes and self.current_trimestre in notes[matiere.id]:
                    note = notes[matiere.id][self.current_trimestre]
                    if note.moyenne is not None:
                        moyenne.setText(f"{note.moyenne:.2f}")
                self.table_notes.setItem(row, 4, moyenne)
                
                # Rendre les cellules non-éditables sauf les notes
                for col in [0, 1, 4]:
                    item = self.table_notes.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def calculer_moyennes(self):
        """Calcule les moyennes pour toutes les matières"""
        for row in range(self.table_notes.rowCount()):
            note_cc = self.table_notes.cellWidget(row, 2).value()
            note_exam = self.table_notes.cellWidget(row, 3).value()
            
            if note_cc > 0 or note_exam > 0:
                moyenne = round(0.4 * note_cc + 0.6 * note_exam, 2)
                self.table_notes.item(row, 4).setText(f"{moyenne:.2f}")

    def enregistrer_notes(self):
        if not self.selected_etudiant:
            return
            
        try:
            for row in range(self.table_notes.rowCount()):
                matiere = self.matieres[row]
                note_cc = self.table_notes.cellWidget(row, 2).value()
                note_exam = self.table_notes.cellWidget(row, 3).value()
                
                note = Note(
                    id=None,
                    etudiant_matricule=self.selected_etudiant.matricule,
                    matiere_id=matiere.id,
                    trimestre=self.current_trimestre,
                    note_cc=note_cc if note_cc > 0 else None,
                    note_exam=note_exam if note_exam > 0 else None
                )
                
                self.db.ajouter_note(note)
            
            QMessageBox.information(self, "Succès", "Les notes ont été enregistrées avec succès!")
            self.charger_classement()  # Rafraîchir le classement
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer les notes: {str(e)}")

    def closeEvent(self, event):
        # Ne pas fermer la base de données ici
        super().closeEvent(event) 