from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox,
                             QHeaderView, QLineEdit)
from PyQt5.QtCore import Qt
from database import Database
from models import Note, Matiere, ResultatEtudiant, Etudiant
from datetime import datetime
import os

class NotesWindow(QMainWindow):
    def __init__(self, matricule=None, niveau=None, filiere=None, parent=None):
        super().__init__(parent)
        self.matricule = matricule
        self.niveau = niveau
        self.filiere = filiere
        self.db = Database()
        self.setup_ui()
        self.selected_etudiant = None
        self.matieres = []
        self.current_trimestre = 1
        self.statusBar()  # Créer la barre de statut

    def set_matricule(self, matricule):
        """Définit le matricule de l'étudiant sélectionné"""
        if matricule:
            etudiant = self.db.rechercher_etudiant(matricule)
            if etudiant:
                self.selected_etudiant = etudiant
                self.etudiant_label.setText(f"{etudiant.nom} {etudiant.prenom} ({etudiant.matricule})")
                self.afficher_notes(etudiant)

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
        
        # Groupe pour le niveau
        niveau_group = QVBoxLayout()
        niveau_label = QLabel("Niveau:")
        niveau_label.setStyleSheet("font-weight: bold;")
        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(Etudiant.NIVEAUX)
        self.niveau_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        niveau_group.addWidget(niveau_label)
        niveau_group.addWidget(self.niveau_combo)
        
        # Groupe pour la filière
        filiere_group = QVBoxLayout()
        filiere_label = QLabel("Filière:")
        filiere_label.setStyleSheet("font-weight: bold;")
        self.filiere_combo = QComboBox()
        self.filiere_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        filiere_group.addWidget(filiere_label)
        filiere_group.addWidget(self.filiere_combo)
        
        # Groupe pour le trimestre
        trimestre_group = QVBoxLayout()
        trimestre_label = QLabel("Trimestre:")
        trimestre_label.setStyleSheet("font-weight: bold;")
        self.trimestre_combo = QComboBox()
        self.trimestre_combo.addItems(['Trimestre 1', 'Trimestre 2', 'Trimestre 3'])
        self.trimestre_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        trimestre_group.addWidget(trimestre_label)
        trimestre_group.addWidget(self.trimestre_combo)
        
        # Ajouter les groupes au layout de filtrage
        filter_layout.addLayout(niveau_group)
        filter_layout.addLayout(filiere_group)
        filter_layout.addLayout(trimestre_group)
        filter_layout.addStretch()
        
        # Boutons d'action
        buttons_group = QHBoxLayout()
        
        
        # Bouton Rafraîchir
        self.btn_refresh = QPushButton("Rafraîchir")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        buttons_group.addWidget(self.btn_refresh)
        filter_layout.addLayout(buttons_group)
        
        main_layout.addLayout(filter_layout)
        
        # Table des étudiants
        self.table_etudiants = QTableWidget()
        self.table_etudiants.setColumnCount(12)
        self.table_etudiants.setHorizontalHeaderLabels([
            "Matricule", "Nom", "Prénom", "Date de naissance", "Sexe",
            "Moyenne T1", "Moyenne T2", "Moyenne T3",
            "Moyenne Générale", "Mention", "Décision", "Action"
        ])
        self.table_etudiants.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_etudiants.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_etudiants.setSelectionMode(QTableWidget.SingleSelection)
        self.table_etudiants.setAlternatingRowColors(True)
        self.table_etudiants.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
        """)
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
        self.setup_connections()
        
        # Initialiser les filières
        self.niveau_change(self.niveau_combo.currentText())

    def setup_connections(self):
        """Configure les connexions des signaux"""
        self.niveau_combo.currentTextChanged.connect(self.niveau_change)
        self.filiere_combo.currentTextChanged.connect(self.filiere_change)
        self.trimestre_combo.currentIndexChanged.connect(self.trimestre_change)
        self.btn_refresh.clicked.connect(self.rafraichir_liste)
        self.btn_calculer.clicked.connect(self.calculer_moyennes)
        self.btn_enregistrer.clicked.connect(self.enregistrer_notes)
        self.table_etudiants.itemSelectionChanged.connect(self.on_etudiant_selected)

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
        """Charge et affiche les étudiants selon le niveau et la filière sélectionnés depuis etudiants.txt"""
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()

        if not niveau or not filiere:
            self.table_etudiants.setRowCount(0)
            return

        try:
            etudiants_filtres = []
            if os.path.exists('etudiants.txt'):
                with open('etudiants.txt', 'r', encoding='utf-8') as f:
                    for ligne in f:
                        donnees = ligne.strip().split('|')
                        if len(donnees) == 7:
                            matricule, nom, prenom, date_naissance, sexe, filiere_txt, niveau_txt = donnees
                            if niveau_txt == niveau and filiere_txt == filiere:
                                etudiants_filtres.append({
                                    "matricule": matricule,
                                    "nom": nom,
                                    "prenom": prenom,
                                    "date_naissance": date_naissance,
                                    "sexe": sexe
                                })

            self.table_etudiants.setRowCount(0)  # Vide le tableau avant de le remplir

            for row, etudiant in enumerate(etudiants_filtres):
                moyennes_trim = self.calculer_moyennes_trimestres(etudiant["matricule"])
                moyenne_generale = 0.0
                if all(trim in moyennes_trim for trim in [1, 2, 3]):
                    moyenne_generale = (moyennes_trim[1] + moyennes_trim[2] + (2 * moyennes_trim[3])) / 4
                mention = ResultatEtudiant.calculer_mention(moyenne_generale)
                # --- MODIFIE ICI ---
                if self.niveau_combo.currentText().lower() == "bac" and 7.0 <= moyenne_generale < 10.0:
                    decision = "Contrôle"
                else:
                    decision = "Admis" if moyenne_generale >= 10 else "Refusé"
                # --- FIN MODIF ---

                self.table_etudiants.insertRow(row)
                self.table_etudiants.setItem(row, 0, QTableWidgetItem(etudiant["matricule"]))
                self.table_etudiants.setItem(row, 1, QTableWidgetItem(etudiant["nom"]))
                self.table_etudiants.setItem(row, 2, QTableWidgetItem(etudiant["prenom"]))
                self.table_etudiants.setItem(row, 3, QTableWidgetItem(etudiant["date_naissance"]))
                self.table_etudiants.setItem(row, 4, QTableWidgetItem(etudiant["sexe"]))
                self.table_etudiants.setItem(row, 5, QTableWidgetItem(f"{moyennes_trim[1]:.2f}"))
                self.table_etudiants.setItem(row, 6, QTableWidgetItem(f"{moyennes_trim[2]:.2f}"))
                self.table_etudiants.setItem(row, 7, QTableWidgetItem(f"{moyennes_trim[3]:.2f}"))
                self.table_etudiants.setItem(row, 8, QTableWidgetItem(f"{moyenne_generale:.2f}"))
                self.table_etudiants.setItem(row, 9, QTableWidgetItem(mention))
                self.table_etudiants.setItem(row, 10, QTableWidgetItem(decision))

                # Créer le bouton "Gérer les notes"
                btn_notes = QPushButton("Gérer les notes")
                btn_notes.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                btn_notes.clicked.connect(lambda checked, e=etudiant: self.afficher_notes(
                    Etudiant(
                        matricule=e["matricule"],
                        nom=e["nom"],
                        prenom=e["prenom"],
                        date_naissance=e["date_naissance"],
                        sexe=e["sexe"],
                        filiere=self.filiere_combo.currentText(),
                        niveau=self.niveau_combo.currentText()
                    )
                ))
                self.table_etudiants.setCellWidget(row, 11, btn_notes)  # <-- colonne 11 = "Action"
            
            self.statusBar().showMessage(f"{len(etudiants_filtres)} étudiant(s) trouvé(s) pour {niveau} - {filiere}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les étudiants: {str(e)}")
            self.statusBar().showMessage("Erreur lors du chargement des étudiants", 3000)

    def calculer_moyennes_trimestres(self, matricule):
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()
        nom_fichier = f"notes_{niveau}_{filiere}.txt"
        moyennes = {1: 0.0, 2: 0.0, 3: 0.0}
        coefs = {1: 0, 2: 0, 3: 0}
        totaux = {1: 0.0, 2: 0.0, 3: 0.0}
        if not os.path.exists(nom_fichier):
            return moyennes
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split("|")
                if len(parts) == 5:
                    m, matiere, note_cc, note_exam, trimestre = parts
                    if m == matricule:
                        trimestre = int(trimestre)
                        note_cc = float(note_cc)
                        note_exam = float(note_exam)
                        # Adapte le calcul selon ta règle
                        moyenne = 0.4 * note_cc + 0.6 * note_exam
                        coef = 1  # Mets le vrai coefficient si tu l'as
                        totaux[trimestre] += moyenne * coef
                        coefs[trimestre] += coef
        for t in [1, 2, 3]:
            if coefs[t] > 0:
                moyennes[t] = round(totaux[t] / coefs[t], 2)
        return moyennes

    def afficher_notes(self, etudiant):
        self.selected_etudiant = etudiant
        self.etudiant_label.setText(f"{etudiant.nom} {etudiant.prenom} ({etudiant.matricule})")
        try:
            # Récupérer les matières pour ce niveau et cette filière
            self.matieres = self.db.get_matieres(etudiant.niveau, etudiant.filiere)
            self.table_notes.setRowCount(len(self.matieres))
            # Charger les notes existantes pour cet étudiant et ce trimestre
            notes_existantes = {}
            nom_fichier = f"notes_{etudiant.niveau}_{etudiant.filiere}.txt"
            trimestre = self.trimestre_combo.currentIndex() + 1
            if os.path.exists(nom_fichier):
                with open(nom_fichier, "r", encoding="utf-8") as f:
                    for ligne in f:
                        parts = ligne.strip().split("|")
                        if len(parts) == 5:
                            m, matiere, note_cc, note_exam, trim = parts
                            if m == etudiant.matricule and int(trim) == trimestre:
                                notes_existantes[matiere] = (float(note_cc), float(note_exam))
            
            # Remplir la table des notes
            for row, matiere in enumerate(self.matieres):
                self.table_notes.setItem(row, 0, QTableWidgetItem(matiere.nom))
                self.table_notes.setItem(row, 1, QTableWidgetItem(str(matiere.coefficient)))
                # Note CC (input)
                note_cc = QDoubleSpinBox()
                note_cc.setRange(0, 20)
                note_cc.setDecimals(2)
                # Note Examen (input)
                note_exam = QDoubleSpinBox()
                note_exam.setRange(0, 20)
                note_exam.setDecimals(2)
                # Pré-remplir si note existante
                if matiere.nom in notes_existantes:
                    note_cc.setValue(notes_existantes[matiere.nom][0])
                    note_exam.setValue(notes_existantes[matiere.nom][1])
                self.table_notes.setCellWidget(row, 2, note_cc)
                self.table_notes.setCellWidget(row, 3, note_exam)
                self.table_notes.setItem(row, 4, QTableWidgetItem(""))
                # Rendre les cellules non éditables sauf les inputs
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

        niveau = self.selected_etudiant.niveau
        filiere = self.selected_etudiant.filiere
        matricule = self.selected_etudiant.matricule
        trimestre = self.trimestre_combo.currentIndex() + 1  # 1, 2 ou 3

        try:
            notes_data = []
            total = 0
            coef_total = 0
            for row in range(self.table_notes.rowCount()):
                matiere = self.matieres[row]
                note_cc = self.table_notes.cellWidget(row, 2).value()
                note_exam = self.table_notes.cellWidget(row, 3).value()
                moyenne = round(0.4 * note_cc + 0.6 * note_exam, 2)
                notes_data.append(f"{matricule}|{matiere.nom}|{note_cc:.2f}|{note_exam:.2f}|{trimestre}")
                total += moyenne * matiere.coefficient
                coef_total += matiere.coefficient

            moyenne_trim = round(total / coef_total, 2) if coef_total > 0 else 0.0

            # Nom du fichier par niveau et filière
            nom_fichier = f"notes_{niveau}_{filiere}.txt"
            with open(nom_fichier, "a", encoding="utf-8") as f:
                for ligne in notes_data:
                    f.write(ligne + "\n")

            # Met à jour la colonne du trimestre choisi dans le tableau principal
            selected_rows = self.table_etudiants.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                col = 5 + (trimestre - 1)  # 5 = colonne Moyenne T1
                self.table_etudiants.setItem(row, col, QTableWidgetItem(f"{moyenne_trim:.2f}"))

            QMessageBox.information(self, "Succès", f"Les notes ont été enregistrées et la moyenne du trimestre {trimestre} est {moyenne_trim:.2f} !")
            self.charger_classement()  # Rafraîchir le classement si besoin

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer les notes: {str(e)}")

    def afficher_etudiants(self):
        """Affiche les étudiants selon le niveau et la filière sélectionnés"""
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()
        
        if not niveau or not filiere:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un niveau et une filière")
            return
            
        try:
            # Récupérer et filtrer les étudiants
            tous_etudiants = self.db.get_all_etudiants()
            etudiants_filtres = [
                etudiant for etudiant in tous_etudiants
                if etudiant.niveau == niveau and etudiant.filiere == filiere
            ]
            
            # Mettre à jour le tableau
            self.table_etudiants.setRowCount(len(etudiants_filtres))
            
            for row, etudiant in enumerate(etudiants_filtres):
                # Calculer les moyennes par trimestre
                moyennes_trim = self.calculer_moyennes_trimestres(etudiant.matricule)
                
                # Calculer la moyenne générale
                moyenne_generale = 0.0
                if all(trim in moyennes_trim for trim in [1, 2, 3]):
                    moyenne_generale = (moyennes_trim[1] + moyennes_trim[2] + (2 * moyennes_trim[3])) / 4
                
                # Déterminer la mention
                mention = ResultatEtudiant.calculer_mention(moyenne_generale)
                
                # Créer les items du tableau
                items = [
                    QTableWidgetItem(etudiant.matricule),
                    QTableWidgetItem(etudiant.nom),
                    QTableWidgetItem(etudiant.prenom),
                    QTableWidgetItem(etudiant.date_naissance),
                    QTableWidgetItem(etudiant.sexe),
                    QTableWidgetItem(f"{moyennes_trim.get(1, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyennes_trim.get(2, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyennes_trim.get(3, 0.0):.2f}"),
                    QTableWidgetItem(f"{moyenne_generale:.2f}"),
                    QTableWidgetItem(mention)
                ]
                
                # Ajouter les items au tableau
                for col, item in enumerate(items):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table_etudiants.setItem(row, col, item)
                
                # Ajouter le bouton Gérer les notes
                btn_notes = QPushButton("Gérer les notes")
                btn_notes.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                btn_notes.clicked.connect(lambda checked, e=etudiant: self.afficher_notes(e))
                self.table_etudiants.setCellWidget(row, 10, btn_notes)
            
            # Afficher un message de statut
            message = f"{len(etudiants_filtres)} étudiant(s) trouvé(s) pour {niveau} - {filiere}"
            self.statusBar().showMessage(message, 3000)
            
            # Sauvegarder les résultats dans un fichier
            self.sauvegarder_resultats_filtres(etudiants_filtres, niveau, filiere)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'affichage des étudiants : {str(e)}")
            self.statusBar().showMessage("Erreur lors de l'affichage des étudiants", 3000)

    def sauvegarder_resultats_filtres(self, etudiants, niveau, filiere):
        """Sauvegarde les résultats filtrés dans un fichier texte"""
        try:
            nom_fichier = f"resultats_{niveau}_{filiere}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                f.write(f"=== Résultats pour {niveau} - {filiere} ===\n\n")
                
                for etudiant in etudiants:
                    moyennes = self.calculer_moyennes_trimestres(etudiant.matricule)
                    moyenne_generale = 0.0
                    if all(trim in moyennes for trim in [1, 2, 3]):
                        moyenne_generale = (moyennes[1] + moyennes[2] + (2 * moyennes[3])) / 4
                    
                    f.write(f"Étudiant: {etudiant.nom} {etudiant.prenom}\n")
                    f.write(f"Matricule: {etudiant.matricule}\n")
                    f.write(f"Moyennes par trimestre:\n")
                    f.write(f"  - Trimestre 1: {moyennes.get(1, 0.0):.2f}\n")
                    f.write(f"  - Trimestre 2: {moyennes.get(2, 0.0):.2f}\n")
                    f.write(f"  - Trimestre 3: {moyennes.get(3, 0.0):.2f}\n")
                    f.write(f"Moyenne générale: {moyenne_generale:.2f}\n")
                    f.write(f"Mention: {ResultatEtudiant.calculer_mention(moyenne_generale)}\n")
                    f.write("\n" + "-"*50 + "\n\n")
                
            print(f"Résultats sauvegardés dans {nom_fichier}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des résultats: {str(e)}")

    def closeEvent(self, event):
        # Ne pas fermer la base de données ici
        super().closeEvent(event)

    def afficher_notes_seul_etudiant(self):
        """Affiche la fenêtre de saisie des notes pour un seul étudiant"""
        self.setWindowTitle("Saisie des Notes")
        self.setGeometry(100, 100, 400, 300)
        
        # Effacer le layout central actuel
        for i in reversed(range(self.centralWidget().layout().count())):
            widget = self.centralWidget().layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        layout = QVBoxLayout(self.centralWidget())
        
        label_info = QLabel(f"Saisie des notes pour le matricule : {self.matricule}")
        layout.addWidget(label_info)
        
        # Champs de saisie pour les notes
        self.note1_input = QLineEdit()
        self.note1_input.setPlaceholderText("Note 1")
        layout.addWidget(self.note1_input)

        self.note2_input = QLineEdit()
        self.note2_input.setPlaceholderText("Note 2")
        layout.addWidget(self.note2_input)

        # Bouton pour enregistrer les notes
        btn_enregistrer = QPushButton("Enregistrer les notes")
        layout.addWidget(btn_enregistrer)

        # Connexion du bouton à la méthode d'enregistrement
        btn_enregistrer.clicked.connect(self.enregistrer_notes_seul_etudiant)

    def enregistrer_notes_seul_etudiant(self):
        """Enregistre les notes saisies pour un seul étudiant"""
        note1 = self.note1_input.text()
        note2 = self.note2_input.text()
        
        # Ici tu peux ajouter la logique pour sauvegarder les notes
        QMessageBox.information(self, "Succès", f"Notes enregistrées pour {self.matricule} : {note1}, {note2}")

    def charger_etudiants_filtres(self):
        """Charge les étudiants du fichier texte selon le niveau et la filière sélectionnés"""
        self.liste_etudiants.clear()
        if not self.niveau or not self.filiere:
            return
        if not os.path.exists('etudiants.txt'):
            return
        with open('etudiants.txt', 'r', encoding='utf-8') as f:
            for ligne in f:
                donnees = ligne.strip().split('|')
                if len(donnees) == 7:
                    matricule, nom, prenom, date_naissance, sexe, filiere, niveau = donnees
                    if niveau == self.niveau and filiere == self.filiere:
                        self.liste_etudiants.addItem(f"{matricule} - {nom} {prenom}")
    
    def on_etudiant_selected(self):
        selected_rows = self.table_etudiants.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        matricule = self.table_etudiants.item(row, 0).text()
        nom = self.table_etudiants.item(row, 1).text()
        prenom = self.table_etudiants.item(row, 2).text()
        date_naissance = self.table_etudiants.item(row, 3).text()
        sexe = self.table_etudiants.item(row, 4).text()
        etudiant = Etudiant(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            sexe=sexe,
            filiere=self.filiere_combo.currentText(),
            niveau=self.niveau_combo.currentText()
        )
        self.afficher_notes(etudiant)