from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict
from decimal import Decimal

class EtudiantError(Exception):
    """Classe d'exception personnalisée pour les erreurs de validation d'étudiant"""
    pass

@dataclass
class Matiere:
    id: int
    nom: str
    coefficient: int
    niveau: str
    filiere: str

    def __post_init__(self):
        if self.coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à 0")

@dataclass
class Note:
    id: Optional[int]
    etudiant_matricule: str
    matiere_id: int
    note_cc: Optional[float]  # Contrôle continu
    note_exam: Optional[float]  # Examen final
    trimestre: int  # 1, 2 ou 3
    
    def __post_init__(self):
        if self.note_cc is not None and (self.note_cc < 0 or self.note_cc > 20):
            raise ValueError("La note de CC doit être comprise entre 0 et 20")
        if self.note_exam is not None and (self.note_exam < 0 or self.note_exam > 20):
            raise ValueError("La note d'examen doit être comprise entre 0 et 20")
        if self.trimestre not in [1, 2, 3]:
            raise ValueError("Le trimestre doit être 1, 2 ou 3")
    
    @property
    def moyenne(self) -> Optional[float]:
        """Calcule la moyenne (40% CC + 60% Exam)"""
        if self.note_cc is None or self.note_exam is None:
            return None
        return round(0.4 * self.note_cc + 0.6 * self.note_exam, 2)

@dataclass
class ResultatEtudiant:
    etudiant: 'Etudiant'
    notes: Dict[str, Dict[int, Note]]  # Dictionnaire matière -> {trimestre -> note}
    moyenne_generale: float
    rang: int
    mention: str
    credits: int
    
    @staticmethod
    def calculer_mention(moyenne: float) -> str:
        if moyenne >= 16:
            return "Très Bien"
        elif moyenne >= 14:
            return "Bien"
        elif moyenne >= 12:
            return "Assez Bien"
        elif moyenne >= 10:
            return "Passable"
        else:
            return "Insuffisant"
            
    @staticmethod
    def calculer_moyenne_annuelle(notes_trimestres: Dict[int, float]) -> float:
        """Calcule la moyenne annuelle selon la formule tunisienne"""
        if not all(trim in notes_trimestres for trim in [1, 2, 3]):
            return 0.0
            
        # (Trim1 × 1 + Trim2 × 1 + Trim3 × 2) / 4
        return round((notes_trimestres[1] + notes_trimestres[2] + (2 * notes_trimestres[3])) / 4, 2)

@dataclass
class Etudiant:
    matricule: str
    nom: str
    prenom: str
    date_naissance: str
    sexe: str
    filiere: str
    niveau: str

    NIVEAUX = [
        "1ère année", "2ème année", "3ème année", "Bac"
    ]
    FILIERES = {
        "1ère année": ["Tronc Commun"],
        "2ème année": [
            "Lettres",
            "Economie-Gestion",
            "Science",
            "Informatique"
        ],
        "3ème année": [
            "Lettres",
            "Economie-Gestion",
            "Science",
            "Informatique",
            "Mathématique",
            "Technique"
        ],
        "Bac": [
            "Lettres",
            "Economie-Gestion",
            "Science",
            "Informatique",
            "Mathématique",
            "Technique"
        ]
    }
    
    def __post_init__(self):
        self.valider()
    
    def valider(self):
        """Valide les données de l'étudiant"""
        if not self.matricule or not isinstance(self.matricule, str):
            raise EtudiantError("Le matricule est invalide")
            
        if not self.nom or not isinstance(self.nom, str):
            raise EtudiantError("Le nom est invalide")
            
        if not self.prenom or not isinstance(self.prenom, str):
            raise EtudiantError("Le prénom est invalide")
            
        if not self.date_naissance:
            raise EtudiantError("La date de naissance est invalide")
            
        try:
            date = datetime.strptime(self.date_naissance, "%Y-%m-%d")
            if date.date() > datetime.now().date():
                raise EtudiantError("La date de naissance ne peut pas être dans le futur")
        except ValueError:
            raise EtudiantError("Format de date invalide (utilisez YYYY-MM-DD)")
            
        if self.sexe not in ['F', 'H']:
            raise EtudiantError("Le sexe doit être 'F' ou 'H'")
            
        # Vérification de la filière en fonction du niveau
        if self.niveau not in self.FILIERES:
            raise EtudiantError(f"Le niveau doit être l'un des suivants : {', '.join(self.NIVEAUX)}")
            
        filieres_valides = self.FILIERES[self.niveau]
        if self.filiere not in filieres_valides:
            raise EtudiantError(f"Pour le niveau {self.niveau}, la filière doit être l'une des suivantes : {', '.join(filieres_valides)}")
    
    @property
    def age(self) -> Optional[int]:
        """Calcule l'âge de l'étudiant"""
        try:
            naissance = datetime.strptime(self.date_naissance, "%Y-%m-%d")
            aujourd_hui = datetime.now()
            age = aujourd_hui.year - naissance.year
            
            # Ajustement si l'anniversaire n'est pas encore passé cette année
            if aujourd_hui.month < naissance.month or \
               (aujourd_hui.month == naissance.month and aujourd_hui.day < naissance.day):
                age -= 1
                
            return age
        except ValueError:
            return None
    
    def to_dict(self) -> dict:
        """Convertit l'étudiant en dictionnaire"""
        return {
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'sexe': self.sexe,
            'filiere': self.filiere,
            'niveau': self.niveau,
            'age': self.age
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Etudiant':
        """Crée un étudiant à partir d'un dictionnaire"""
        return cls(
            matricule=data.get('matricule', ''),
            nom=data.get('nom', ''),
            prenom=data.get('prenom', ''),
            date_naissance=data.get('date_naissance', ''),
            sexe=data.get('sexe', ''),
            filiere=data.get('filiere', ''),
            niveau=data.get('niveau', '')
        )