import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QDialog
from PyQt5.QtCore import QDate, Qt
from ui_main_window import Ui_MainWindow
from database import Database
from models import Etudiant
from notes_window import NotesWindow
from modifier_etudiant_window import ModifierEtudiantWindow

class GestionEtudiantsApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database()
        self.setup_ui()
        self.setup_connections()
        self.current_matricule = None
        self.notes_window = None
        # Charger les étudiants depuis le fichier texte au démarrage
        self.charger_etudiants_txt()
        # Charger tous les étudiants au démarrage
        self.charger_etudiants()

    def setup_ui(self):
        # Configuration des placeholders
        self.nom_input.setPlaceholderText("Entrez le nom...")
        self.prenom_input.setPlaceholderText("Entrez le prénom...")
        self.matricule_search.setPlaceholderText("Rechercher par matricule, nom ou prénom...")
        
        # Configuration des en-têtes du tableau
        self.table_etudiants.setColumnCount(7)
        self.table_etudiants.setHorizontalHeaderLabels([
            "Matricule",
            "Nom",
            "Prénom",
            "Date de naissance",
            "Sexe",
            "Filière",
            "Niveau"
        ])
        # Ajuster la taille des colonnes
        self.table_etudiants.horizontalHeader().setStretchLastSection(True)
        self.table_etudiants.setColumnWidth(0, 120)  # Matricule
        self.table_etudiants.setColumnWidth(1, 150)  # Nom
        self.table_etudiants.setColumnWidth(2, 150)  # Prénom
        self.table_etudiants.setColumnWidth(3, 120)  # Date de naissance
        self.table_etudiants.setColumnWidth(4, 60)   # Sexe
        self.table_etudiants.setColumnWidth(5, 150)  # Filière
        self.table_etudiants.setColumnWidth(6, 100)  # Niveau
        
        # Configuration de la date
        self.date_naissance_input.setDisplayFormat("dd/MM/yyyy")
        self.date_naissance_input.setDate(QDate.currentDate())
        self.date_naissance_input.setMaximumDate(QDate.currentDate())
        
        # Configuration des combobox
        self.niveau_combo.clear()
        self.niveau_combo.addItems(Etudiant.NIVEAUX)
        
        # Définir "1ère année" comme sélection par défaut
        self.niveau_combo.setCurrentText("1ère année")
        
        # Configuration initiale de la filière - seulement "Tronc Commun" pour la 1ère année
        self.filiere_combo.clear()
        self.filiere_combo.addItem("Tronc Commun")
        
        # Configuration initiale des boutons
        self.btn_modifier.setEnabled(False)
        self.btn_supprimer.setEnabled(False)
        
        # Ajouter le bouton Gestion des Notes
        self.btn_notes = QPushButton("Gestion des Notes")
        self.btn_notes.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_notes.setEnabled(True)  # Toujours actif
        self.buttons_layout.addWidget(self.btn_notes)

    def setup_connections(self):
        self.btn_ajouter.clicked.connect(self.ajouter_etudiant)
        self.btn_modifier.clicked.connect(self.modifier_etudiant)
        self.btn_supprimer.clicked.connect(self.supprimer_etudiant)
        self.btn_actualiser.clicked.connect(self.charger_etudiants)
        self.btn_rechercher.clicked.connect(self.rechercher_etudiant)
        self.table_etudiants.itemSelectionChanged.connect(self.selection_changed)
        
        # Connexions pour la validation en temps réel
        self.nom_input.textChanged.connect(self.valider_champs)
        self.prenom_input.textChanged.connect(self.valider_champs)
        
        # Connexion pour le changement de niveau et filière
        self.niveau_combo.currentTextChanged.connect(self.niveau_change)
        self.filiere_combo.currentTextChanged.connect(self.filtrer_etudiants)
        self.btn_notes.clicked.connect(self.ouvrir_gestion_notes)

    def niveau_change(self, niveau):
        try:
            self.filiere_combo.clear()
            if niveau == "1ère année":
                self.filiere_combo.addItem("Tronc Commun")
            elif niveau in Etudiant.FILIERES:
                self.filiere_combo.addItems(Etudiant.FILIERES[niveau])
            self.filiere_combo.setCurrentIndex(0)
            self.filtrer_etudiants()
        except Exception as e:
            print(f"Erreur dans niveau_change: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du changement de niveau : {str(e)}")

    def filtrer_etudiants(self):
        """Filtre et affiche les étudiants selon le niveau et la filière sélectionnés"""
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()
        
        if not niveau or not filiere:
            self.table_etudiants.setRowCount(0)
            self.table_etudiants.setHorizontalHeaderLabels([
                "Matricule", "Nom", "Prénom", "Date de naissance", "Sexe", "Filière", "Niveau"
            ])
            self.statusBar().showMessage("Veuillez sélectionner un niveau et une filière", 3000)
            return

        try:
            tous_etudiants = self.db.get_all_etudiants()
            etudiants_filtres = [
                etudiant for etudiant in tous_etudiants
                if etudiant.niveau == niveau and etudiant.filiere == filiere
            ]
            self.table_etudiants.setRowCount(len(etudiants_filtres))
            self.table_etudiants.setHorizontalHeaderLabels([
                "Matricule", "Nom", "Prénom", "Date de naissance", "Sexe", "Filière", "Niveau"
            ])
            for row, etudiant in enumerate(etudiants_filtres):
                self.afficher_etudiant(row, etudiant)
            if etudiants_filtres:
                self.statusBar().showMessage(f"{len(etudiants_filtres)} étudiant(s) trouvé(s) pour {niveau} - {filiere}", 3000)
            else:
                self.statusBar().showMessage(f"Aucun étudiant trouvé pour {niveau} - {filiere}", 3000)
        except Exception as e:
            print(f"Erreur dans filtrer_etudiants: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de filtrer les étudiants: {str(e)}")
            self.statusBar().showMessage("Erreur lors du filtrage des étudiants", 3000)

    def valider_champs(self):
        """Valide les champs en temps réel et active/désactive les boutons en conséquence"""
        nom_valide = bool(self.nom_input.text().strip())
        prenom_valide = bool(self.prenom_input.text().strip())
        
        self.btn_ajouter.setEnabled(nom_valide and prenom_valide)
        if self.current_matricule:
            self.btn_modifier.setEnabled(nom_valide and prenom_valide)

    def selection_changed(self):
        selected = self.table_etudiants.selectedItems()
        if selected:
            row = selected[0].row()
            self.remplir_formulaire(row)
            self.btn_modifier.setEnabled(True)
            self.btn_supprimer.setEnabled(True)
            self.btn_notes.setEnabled(True)  # Toujours actif
        else:
            self.effacer_formulaire()
            self.btn_modifier.setEnabled(False)
            self.btn_supprimer.setEnabled(False)
            self.btn_notes.setEnabled(True)  # Toujours actif, même sans sélection

    def remplir_formulaire(self, row):
        self.current_matricule = self.table_etudiants.item(row, 0).text()
        etudiant = self.db.rechercher_etudiant(self.current_matricule)
        if etudiant:
            self.matricule_search.setText(self.current_matricule)
            self.nom_input.setText(etudiant.nom)
            self.prenom_input.setText(etudiant.prenom)
            date = QDate.fromString(etudiant.date_naissance, "yyyy-MM-dd")
            self.date_naissance_input.setDate(date)
            self.radio_f.setChecked(etudiant.sexe == 'F')
            self.radio_h.setChecked(etudiant.sexe == 'H')
            
            # Mise à jour du niveau et de la filière
            niveau_index = self.niveau_combo.findText(etudiant.niveau)
            if niveau_index >= 0:
                self.niveau_combo.setCurrentIndex(niveau_index)
                # La filière sera mise à jour automatiquement par le signal niveau_change
                
            filiere_index = self.filiere_combo.findText(etudiant.filiere)
            if filiere_index >= 0:
                self.filiere_combo.setCurrentIndex(filiere_index)

    def get_sexe(self):
        return 'F' if self.radio_f.isChecked() else 'H'

    def valider_formulaire(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire")
            self.nom_input.setFocus()
            return False
            
        if not prenom:
            QMessageBox.warning(self, "Erreur", "Le prénom est obligatoire")
            self.prenom_input.setFocus()
            return False
            
        if self.date_naissance_input.date() > QDate.currentDate():
            QMessageBox.warning(self, "Erreur", "La date de naissance ne peut pas être dans le futur")
            self.date_naissance_input.setFocus()
            return False
            
        return True

    def sauvegarder_etudiant_txt(self, etudiant):
        """Sauvegarde les informations d'un étudiant dans un fichier texte"""
        try:
            with open('etudiants.txt', 'a', encoding='utf-8') as f:  # mode append
                ligne = f"{etudiant.matricule}|{etudiant.nom}|{etudiant.prenom}|{etudiant.date_naissance}|{etudiant.sexe}|{etudiant.filiere}|{etudiant.niveau}\n"
                f.write(ligne)
            print(f"Étudiant sauvegardé dans etudiants.txt: {etudiant.nom} {etudiant.prenom}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde dans le fichier texte: {str(e)}")
            QMessageBox.warning(self, "Avertissement", "Impossible de sauvegarder dans le fichier texte")

    def charger_etudiants_txt(self):
        """Charge et affiche les étudiants depuis le fichier texte"""
        try:
            self.table_etudiants.setRowCount(0)
            if not os.path.exists('etudiants.txt'):
                return
                
            with open('etudiants.txt', 'r', encoding='utf-8') as f:
                lignes = f.readlines()
                
            self.table_etudiants.setRowCount(len(lignes))
            for row, ligne in enumerate(lignes):
                # Découper la ligne en utilisant le séparateur |
                donnees = ligne.strip().split('|')
                if len(donnees) == 7:  # Vérifier que nous avons toutes les données
                    matricule, nom, prenom, date_naissance, sexe, filiere, niveau = donnees
                    etudiant = Etudiant(
                        matricule=matricule,
                        nom=nom,
                        prenom=prenom,
                        date_naissance=date_naissance,
                        sexe=sexe,
                        filiere=filiere,
                        niveau=niveau
                    )
                    self.afficher_etudiant(row, etudiant)
                    
            self.statusBar().showMessage(f"{len(lignes)} étudiant(s) chargé(s) depuis le fichier texte", 3000)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier texte: {str(e)}")
            QMessageBox.critical(self, "Erreur", "Impossible de charger le fichier texte des étudiants")

    def ajouter_etudiant(self):
        if not self.valider_formulaire():
            return

        try:
            etudiant = Etudiant(
                matricule=self.generer_matricule(),
                nom=self.nom_input.text().strip(),
                prenom=self.prenom_input.text().strip(),
                date_naissance=self.date_naissance_input.date().toString("yyyy-MM-dd"),
                sexe=self.get_sexe(),
                filiere=self.filiere_combo.currentText(),
                niveau=self.niveau_combo.currentText()
            )

            if self.db.ajouter_etudiant(etudiant):
                # Sauvegarder dans le fichier texte
                self.sauvegarder_etudiant_txt(etudiant)
                
                QMessageBox.information(self, "Succès", "Étudiant ajouté avec succès!")
                self.effacer_formulaire()
                # Mettre à jour la liste avec le filtre actuel
                self.filtrer_etudiants()
                # Sélectionner le niveau et la filière du nouvel étudiant
                niveau_index = self.niveau_combo.findText(etudiant.niveau)
                if niveau_index >= 0:
                    self.niveau_combo.setCurrentIndex(niveau_index)
                filiere_index = self.filiere_combo.findText(etudiant.filiere)
                if filiere_index >= 0:
                    self.filiere_combo.setCurrentIndex(filiere_index)
                # Afficher un message dans la barre de statut
                self.statusBar().showMessage(f"Étudiant {etudiant.nom} {etudiant.prenom} ajouté avec succès", 3000)
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'ajouter l'étudiant")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")

    def mettre_a_jour_fichier_txt(self):
        """Met à jour le fichier texte avec tous les étudiants actuels"""
        try:
            etudiants = self.db.get_all_etudiants()
            with open('etudiants.txt', 'w', encoding='utf-8') as f:
                for etudiant in etudiants:
                    ligne = f"{etudiant.matricule}|{etudiant.nom}|{etudiant.prenom}|{etudiant.date_naissance}|{etudiant.sexe}|{etudiant.filiere}|{etudiant.niveau}\n"
                    f.write(ligne)
            print("Fichier texte mis à jour avec succès")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du fichier texte: {str(e)}")
            QMessageBox.warning(self, "Avertissement", "Impossible de mettre à jour le fichier texte")

    def modifier_etudiant(self):
        matricule = self.current_matricule
        etudiant = self.get_etudiant_by_matricule(matricule)
        if not etudiant:
            QMessageBox.warning(self, "Erreur", "Étudiant introuvable dans le fichier.")
            return
        dialog = ModifierEtudiantWindow(etudiant, self)
        if dialog.exec_() == QDialog.Accepted:
            donnees = dialog.get_donnees()
            nouvel_etudiant = Etudiant(
                matricule=etudiant.matricule,
                nom=donnees["nom"],
                prenom=donnees["prenom"],
                date_naissance=donnees["date_naissance"],
                sexe=donnees["sexe"],
                filiere=donnees["filiere"],
                niveau=donnees["niveau"]
            )
            if self.db.modifier_etudiant(nouvel_etudiant):
                self.mettre_a_jour_fichier_txt()
                QMessageBox.information(self, "Succès", "Étudiant modifié avec succès!")
                self.charger_etudiants()
                self.effacer_formulaire()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de modifier l'étudiant")

    def supprimer_etudiant(self):
        if not self.current_matricule:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un étudiant")
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cet étudiant ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reponse == QMessageBox.Yes:
            try:
                # Supprimer l'étudiant de la base
                if self.db.supprimer_etudiant(self.current_matricule):
                    # Mettre à jour le fichier texte
                    self.mettre_a_jour_fichier_txt()
                    # Mettre à jour la table et effacer le formulaire
                    self.charger_etudiants()
                    self.effacer_formulaire()
                    QMessageBox.information(self, "Succès", "Étudiant supprimé avec succès!")
                else:
                    QMessageBox.critical(self, "Erreur", "Impossible de supprimer l'étudiant")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")

    def rechercher_etudiant(self):
        """Recherche un étudiant par matricule, nom ou prénom dans le fichier texte"""
        terme = self.matricule_search.text().strip()
        if not terme:
            self.filtrer_etudiants()
            self.statusBar().showMessage("Veuillez entrer un terme de recherche", 3000)
            return

        try:
            if not os.path.exists('etudiants.txt'):
                QMessageBox.information(self, "Information", "Aucun étudiant trouvé (fichier manquant)")
                self.statusBar().showMessage("Aucun étudiant trouvé", 3000)
                self.effacer_formulaire()
                return

            etudiants_trouves = []
            with open('etudiants.txt', 'r', encoding='utf-8') as f:
                for ligne in f:
                    donnees = ligne.strip().split('|')
                    if len(donnees) == 7:
                        matricule, nom, prenom, date_naissance, sexe, filiere, niveau = donnees
                        if (terme.lower() in matricule.lower() or
                            terme.lower() in nom.lower() or
                            terme.lower() in prenom.lower()):
                            etudiant = Etudiant(
                                matricule=matricule,
                                nom=nom,
                                prenom=prenom,
                                date_naissance=date_naissance,
                                sexe=sexe,
                                filiere=filiere,
                                niveau=niveau
                            )
                            etudiants_trouves.append(etudiant)

            self.table_etudiants.setRowCount(0)
            if etudiants_trouves:
                self.table_etudiants.setRowCount(len(etudiants_trouves))
                self.table_etudiants.setHorizontalHeaderLabels([
                    "Matricule", "Nom", "Prénom", "Date de naissance", "Sexe", "Filière", "Niveau"
                ])
                for row, etudiant in enumerate(etudiants_trouves):
                    self.afficher_etudiant(row, etudiant)
                if len(etudiants_trouves) == 1:
                    self.remplir_formulaire(0)
                self.statusBar().showMessage(f"{len(etudiants_trouves)} étudiant(s) trouvé(s) pour '{terme}'", 3000)
            else:
                QMessageBox.information(self, "Information", "Aucun étudiant trouvé")
                self.statusBar().showMessage("Aucun étudiant trouvé", 3000)
                self.effacer_formulaire()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")
            self.statusBar().showMessage("Erreur lors de la recherche", 3000)

    def charger_etudiants(self):
        """Charge tous les étudiants sans filtre"""
        try:
            etudiants = self.db.get_all_etudiants()
            self.table_etudiants.setRowCount(len(etudiants))
            for row, etudiant in enumerate(etudiants):
                self.afficher_etudiant(row, etudiant)
            self.statusBar().showMessage(f"{len(etudiants)} étudiant(s) chargé(s)", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les étudiants: {str(e)}")

    def afficher_etudiant(self, row, etudiant):
        items = [
            QTableWidgetItem(etudiant.matricule),
            QTableWidgetItem(etudiant.nom),
            QTableWidgetItem(etudiant.prenom),
            QTableWidgetItem(etudiant.date_naissance),
            QTableWidgetItem(etudiant.sexe),
            QTableWidgetItem(etudiant.filiere),
            QTableWidgetItem(etudiant.niveau)
        ]
        
        for col, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Rendre les cellules non éditables
            self.table_etudiants.setItem(row, col, item)

    def generer_matricule(self):
        return f"ETU{datetime.now().strftime('%y%m%d%H%M%S')}"

    def effacer_formulaire(self):
        self.current_matricule = None
        self.matricule_search.clear()
        self.nom_input.clear()
        self.prenom_input.clear()
        self.date_naissance_input.setDate(QDate.currentDate())
        self.radio_f.setChecked(True)
        self.niveau_combo.setCurrentText("1ère année")
        self.filiere_combo.setCurrentText("Tronc Commun")
        self.btn_modifier.setEnabled(False)
        self.btn_supprimer.setEnabled(False)
        # NE PAS désactiver le bouton gestion des notes
        # self.btn_notes.setEnabled(False)
        self.table_etudiants.clearSelection()

    def ouvrir_gestion_notes(self):
        niveau = self.niveau_combo.currentText()
        filiere = self.filiere_combo.currentText()
        self.notes_window = NotesWindow(
            matricule=self.current_matricule,
            niveau=niveau,
            filiere=filiere,
            parent=self
        )
        self.notes_window.show()
        self.notes_window.raise_()
        self.notes_window.activateWindow()

    def closeEvent(self, event):
        # Fermer proprement la base de données
        if self.db:
            self.db.close()
        if self.notes_window:
            self.notes_window.close()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.charger_etudiants_txt()

    def get_etudiant_by_matricule(self, matricule):
        """Recherche un étudiant dans etudiants.txt par son matricule"""
        if not matricule:
            return None
        if not os.path.exists('etudiants.txt'):
            return None
        with open('etudiants.txt', 'r', encoding='utf-8') as f:
            for ligne in f:
                donnees = ligne.strip().split('|')
                if len(donnees) == 7 and donnees[0] == matricule:
                    return Etudiant(
                        matricule=donnees[0],
                        nom=donnees[1],
                        prenom=donnees[2],
                        date_naissance=donnees[3],
                        sexe=donnees[4],
                        filiere=donnees[5],
                        niveau=donnees[6]
                    )
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestionEtudiantsApp()
    window.show()
    sys.exit(app.exec_())