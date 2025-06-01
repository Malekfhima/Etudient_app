import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from models import Etudiant, Matiere, Note, ResultatEtudiant
import os

class DatabaseError(Exception):
    """Classe d'exception personnalisée pour les erreurs de base de données"""
    pass

class Database:
    def __init__(self, db_name='etudiants.db'):
        try:
            self.conn = sqlite3.connect(db_name)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la connexion à la base de données: {str(e)}")

    def create_tables(self):
        # Supprimer les anciennes tables si elles existent
        self.conn.executescript("""
            DROP TABLE IF EXISTS notes;
            DROP TABLE IF EXISTS matieres;
            DROP TABLE IF EXISTS etudiants;
        """)
        
        queries = [
            """
            CREATE TABLE IF NOT EXISTS etudiants (
                matricule TEXT PRIMARY KEY,
                nom TEXT NOT NULL CHECK(length(nom) > 0),
                prenom TEXT NOT NULL CHECK(length(prenom) > 0),
                date_naissance DATE NOT NULL,
                sexe TEXT NOT NULL CHECK(sexe IN ('F', 'H')),
                filiere TEXT NOT NULL,
                niveau TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS matieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                coefficient INTEGER NOT NULL CHECK(coefficient > 0),
                niveau TEXT NOT NULL,
                filiere TEXT NOT NULL,
                UNIQUE(nom, niveau, filiere)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant_matricule TEXT NOT NULL,
                matiere_id INTEGER NOT NULL,
                trimestre INTEGER NOT NULL CHECK(trimestre IN (1, 2, 3)),
                note_cc REAL CHECK(note_cc >= 0 AND note_cc <= 20),
                note_exam REAL CHECK(note_exam >= 0 AND note_exam <= 20),
                FOREIGN KEY (etudiant_matricule) REFERENCES etudiants(matricule) ON DELETE CASCADE,
                FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE,
                UNIQUE(etudiant_matricule, matiere_id, trimestre)
            )
            """
        ]
        
        try:
            for query in queries:
                self.conn.execute(query)
            self.conn.commit()
            
            # Ajouter les matières par défaut
            self.ajouter_matieres_par_defaut()
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la création des tables: {str(e)}")

    def ajouter_matieres_par_defaut(self):
        matieres = [
            # 1ère Année Secondaire (Tronc Commun)
            ('Arabe', 2, '1ère année', 'Tronc Commun'),
            ('Français', 2, '1ère année', 'Tronc Commun'),
            ('Anglais', 2, '1ère année', 'Tronc Commun'),
            ('Mathématiques', 3, '1ère année', 'Tronc Commun'),
            ('Physique-Chimie', 2, '1ère année', 'Tronc Commun'),
            ('Sciences de la Vie et de la Terre', 2, '1ère année', 'Tronc Commun'),
            ('Histoire-Géographie', 1, '1ère année', 'Tronc Commun'),
            ('Éducation islamique', 1, '1ère année', 'Tronc Commun'),
            ('Informatique', 1, '1ère année', 'Tronc Commun'),
            ('Philosophie', 1, '1ère année', 'Tronc Commun'),
        ]

        # Matières communes pour 2ème année, 3ème année et Bac
        niveaux = ['2ème année', '3ème année', 'Bac']
        for niveau in niveaux:
            # Sciences Expérimentales
            matieres.extend([
                ('Arabe', 2, niveau, 'Sciences Expérimentales'),
                ('Français', 2, niveau, 'Sciences Expérimentales'),
                ('Anglais', 2, niveau, 'Sciences Expérimentales'),
                ('Mathématiques', 4, niveau, 'Sciences Expérimentales'),
                ('Physique-Chimie', 4, niveau, 'Sciences Expérimentales'),
                ('Sciences de la Vie et de la Terre', 4, niveau, 'Sciences Expérimentales'),
                ('Philosophie', 1, niveau, 'Sciences Expérimentales'),
            ])

            # Mathématiques
            matieres.extend([
                ('Arabe', 2, niveau, 'Mathématiques'),
                ('Français', 2, niveau, 'Mathématiques'),
                ('Anglais', 2, niveau, 'Mathématiques'),
                ('Mathématiques', 6, niveau, 'Mathématiques'),
                ('Physique-Chimie', 5, niveau, 'Mathématiques'),
                ('Sciences Industrielles', 3, niveau, 'Mathématiques'),
                ('Philosophie', 1, niveau, 'Mathématiques'),
            ])

            # Lettres
            matieres.extend([
                ('Arabe', 4, niveau, 'Lettres'),
                ('Français', 3, niveau, 'Lettres'),
                ('Anglais', 2, niveau, 'Lettres'),
                ('Histoire-Géographie', 3, niveau, 'Lettres'),
                ('Philosophie', 3, niveau, 'Lettres'),
                ('Mathématiques', 1, niveau, 'Lettres'),
            ])

            # Économie et Gestion
            matieres.extend([
                ('Arabe', 2, niveau, 'Économie et Gestion'),
                ('Français', 2, niveau, 'Économie et Gestion'),
                ('Anglais', 2, niveau, 'Économie et Gestion'),
                ('Mathématiques', 3, niveau, 'Économie et Gestion'),
                ('Économie', 4, niveau, 'Économie et Gestion'),
                ('Gestion', 4, niveau, 'Économie et Gestion'),
                ('Mathématiques Financières', 3, niveau, 'Économie et Gestion'),
            ])

            # Technique
            matieres.extend([
                ('Arabe', 2, niveau, 'Technique'),
                ('Français', 2, niveau, 'Technique'),
                ('Anglais', 2, niveau, 'Technique'),
                ('Mathématiques', 3, niveau, 'Technique'),
                ('Physique-Chimie', 2, niveau, 'Technique'),
                ('Sciences Techniques', 6, niveau, 'Technique'),
                ('Informatique', 1, niveau, 'Technique'),
            ])

            # Informatique
            matieres.extend([
                ('Arabe', 2, niveau, 'Informatique'),
                ('Français', 2, niveau, 'Informatique'),
                ('Anglais', 2, niveau, 'Informatique'),
                ('Mathématiques', 4, niveau, 'Informatique'),
                ('Physique', 2, niveau, 'Informatique'),
                ('Informatique', 6, niveau, 'Informatique'),
                ('Algorithmes', 3, niveau, 'Informatique'),
                ('Base de données', 3, niveau, 'Informatique'),
                ('Programmation', 4, niveau, 'Informatique'),
            ])
        
        query = "INSERT OR IGNORE INTO matieres (nom, coefficient, niveau, filiere) VALUES (?, ?, ?, ?)"
        try:
            self.conn.executemany(query, matieres)
            self.conn.commit()
        except sqlite3.Error:
            pass  # Ignorer les erreurs si les matières existent déjà

    def get_matieres(self, niveau: str, filiere: str) -> List[Matiere]:
        """Récupère toutes les matières pour un niveau et une filière donnés"""
        query = "SELECT * FROM matieres WHERE niveau = ? AND filiere = ?"
        try:
            cursor = self.conn.execute(query, (niveau, filiere))
            return [Matiere(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la récupération des matières: {str(e)}")

    def ajouter_note(self, note: Note) -> bool:
        """Ajoute ou met à jour une note"""
        query = """
        INSERT OR REPLACE INTO notes (etudiant_matricule, matiere_id, trimestre, note_cc, note_exam)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self.conn:
                self.conn.execute(query, (
                    note.etudiant_matricule,
                    note.matiere_id,
                    note.trimestre,
                    note.note_cc,
                    note.note_exam
                ))
            return True
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de l'ajout de la note: {str(e)}")

    def get_notes_etudiant(self, matricule: str) -> Dict[int, Dict[int, Note]]:
        """Récupère toutes les notes d'un étudiant, organisées par matière et trimestre"""
        query = "SELECT * FROM notes WHERE etudiant_matricule = ? ORDER BY matiere_id, trimestre"
        try:
            cursor = self.conn.execute(query, (matricule,))
            notes = {}
            for row in cursor.fetchall():
                note = Note(*row)
                if note.matiere_id not in notes:
                    notes[note.matiere_id] = {}
                notes[note.matiere_id][note.trimestre] = note
            return notes
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la récupération des notes: {str(e)}")

    def calculer_moyenne_generale(self, matricule: str) -> Tuple[float, int]:
        """Calcule la moyenne générale et le nombre de crédits obtenus"""
        try:
            notes_par_matiere = self.get_notes_etudiant(matricule)
            if not notes_par_matiere:
                return 0.0, 0

            total_points = 0
            total_coef = 0
            credits = 0
            
            for matiere_id, notes_trimestres in notes_par_matiere.items():
                # Récupérer le coefficient de la matière
                cursor = self.conn.execute("SELECT coefficient FROM matieres WHERE id = ?", (matiere_id,))
                coef = cursor.fetchone()[0]
                
                # Calculer la moyenne annuelle de la matière
                moyennes_trimestres = {}
                for trim, note in notes_trimestres.items():
                    if note.moyenne is not None:
                        moyennes_trimestres[trim] = note.moyenne
                
                if len(moyennes_trimestres) == 3:  # Si on a les notes des 3 trimestres
                    moyenne_matiere = ResultatEtudiant.calculer_moyenne_annuelle(moyennes_trimestres)
                    total_points += moyenne_matiere * coef
                    total_coef += coef
                    if moyenne_matiere >= 10:
                        credits += coef
            
            if total_coef == 0:
                return 0.0, 0
                
            return round(total_points / total_coef, 2), credits
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors du calcul de la moyenne: {str(e)}")

    def get_classement(self, niveau: str, filiere: str) -> List[ResultatEtudiant]:
        """Récupère le classement des étudiants par niveau et filière"""
        try:
            # Récupérer tous les étudiants du niveau et de la filière
            etudiants = self.get_etudiants_by_niveau_filiere(niveau, filiere)
            resultats = []
            
            for etudiant in etudiants:
                moyenne, credits = self.calculer_moyenne_generale(etudiant.matricule)
                notes = {str(note.matiere_id): note for note in self.get_notes_etudiant(etudiant.matricule)}
                
                resultats.append(ResultatEtudiant(
                    etudiant=etudiant,
                    notes=notes,
                    moyenne_generale=moyenne,
                    rang=0,  # Sera calculé après le tri
                    mention=ResultatEtudiant.calculer_mention(moyenne),
                    credits=credits
                ))
            
            # Trier par moyenne décroissante
            resultats.sort(key=lambda x: x.moyenne_generale, reverse=True)
            
            # Attribuer les rangs
            for i, resultat in enumerate(resultats, 1):
                resultat.rang = i
            
            return resultats
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la récupération du classement: {str(e)}")

    def get_etudiants_by_niveau_filiere(self, niveau: str, filiere: str) -> List[Etudiant]:
        """Récupère tous les étudiants d'un niveau et d'une filière donnés"""
        query = "SELECT * FROM etudiants WHERE niveau = ? AND filiere = ? ORDER BY nom, prenom"
        try:
            cursor = self.conn.execute(query, (niveau, filiere))
            return [Etudiant(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la récupération des étudiants: {str(e)}")

    def valider_date(self, date_str):
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date > datetime.now():
                return False
            return True
        except ValueError:
            return False

    def ajouter_etudiant(self, etudiant):
        if not self.valider_date(etudiant.date_naissance):
            raise DatabaseError("La date de naissance n'est pas valide")

        query = """
        INSERT INTO etudiants VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.conn:
                self.conn.execute(query, (
                    etudiant.matricule,
                    etudiant.nom.strip(),
                    etudiant.prenom.strip(),
                    etudiant.date_naissance,
                    etudiant.sexe,
                    etudiant.filiere,
                    etudiant.niveau
                ))
            return True
        except sqlite3.IntegrityError as e:
            if "CHECK constraint failed" in str(e):
                raise DatabaseError("Les données ne respectent pas les contraintes de validation")
            raise DatabaseError("Un étudiant avec ce matricule existe déjà")
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de l'ajout de l'étudiant: {str(e)}")

    def supprimer_etudiant(self, matricule):
        if not matricule:
            raise DatabaseError("Le matricule ne peut pas être vide")

        query = "DELETE FROM etudiants WHERE matricule = ?"
        try:
            with self.conn:
                cursor = self.conn.execute(query, (matricule,))
                if cursor.rowcount == 0:
                    return False
                return True
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la suppression de l'étudiant: {str(e)}")

    def modifier_etudiant(self, etudiant):
        """Modifie un étudiant dans etudiants.txt selon son matricule"""
        if not etudiant or not etudiant.matricule:
            return False
        if not os.path.exists('etudiants.txt'):
            return False
        lignes = []
        trouve = False
        with open('etudiants.txt', 'r', encoding='utf-8') as f:
            for ligne in f:
                donnees = ligne.strip().split('|')
                if len(donnees) == 7 and donnees[0] == etudiant.matricule:
                    # Remplacer la ligne par les nouvelles données
                    lignes.append('|'.join([
                        etudiant.matricule,
                        etudiant.nom,
                        etudiant.prenom,
                        etudiant.date_naissance,
                        etudiant.sexe,
                        etudiant.filiere,
                        etudiant.niveau
                    ]))
                    trouve = True
                else:
                    lignes.append(ligne.strip())
        if not trouve:
            return False
        with open('etudiants.txt', 'w', encoding='utf-8') as f:
            for l in lignes:
                f.write(l + '\n')
        return True

    def rechercher_etudiant(self, matricule):
        if not matricule:
            raise DatabaseError("Le matricule ne peut pas être vide")

        query = "SELECT * FROM etudiants WHERE matricule = ?"
        try:
            cursor = self.conn.execute(query, (matricule,))
            row = cursor.fetchone()
            if row:
                return Etudiant(*row)
            return None
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la recherche de l'étudiant: {str(e)}")

    def get_all_etudiants(self):
        try:
            cursor = self.conn.execute("""
                SELECT * FROM etudiants 
                ORDER BY nom, prenom
            """)
            return [Etudiant(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la récupération des étudiants: {str(e)}")

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(f"Erreur lors de la fermeture de la connexion: {str(e)}")

    def __del__(self):
        self.close()