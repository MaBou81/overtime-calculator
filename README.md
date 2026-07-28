# ⏰ Overtime / On-call Intervention Calculator

Application Streamlit pour calculer les heures supplémentaires et les interventions d'astreinte selon les règles belges.

## 📊 Fonctionnalités

- ✅ Calcul automatique des taux d'heures supplémentaires (130%, 150%, 200%)
- ✅ Prise en compte des jours fériés belges
- ✅ Distinction entre interventions urgentes et planifiées
- ✅ Export Excel avec résultats détaillés
- ✅ Calcul indicatif des surcharges financières
- ✅ Validation des données et gestion d'erreurs

## 💰 Taux d'heures supplémentaires

### Interventions planifiées
- **130%** : Nuits en semaine (20:00-06:00)
- **150%** : Vendredi à partir de 20:00 et samedi jusqu'à 20:00
- **200%** : Dimanches, jours fériés, samedi à partir de 20:00, lundi jusqu'à 06:00

### Interventions urgentes
- **200%** : En dehors des heures de bureau (avant 7:30 ou après 18:00), week-ends, jours fériés

## 🚀 Installation locale

### Prérequis
- Python 3.8 ou supérieur
- pip

### Installation
```bash
# Cloner le repository
git clone https://github.com/VOTRE-USERNAME/overtime-calculator.git
cd overtime-calculator

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run overtime_calculator_improved.py
```

L'application sera accessible sur `http://localhost:8501`

## 📋 Format du fichier Excel

Votre fichier Excel doit contenir les colonnes suivantes :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| WOT | Numéro de ticket | WOT001 |
| WOT_Received_Date | Date de réception | 2024-01-15 |
| WOT_Received_Time | Heure de réception | 08:30 |
| Location | Lieu | Building A |
| Description | Description | Server issue |
| Start_Date | Date de début | 2024-01-15 |
| Start_Time | Heure de début | 21:00 |
| End_Date | Date de fin | 2024-01-15 |
| End_Time | Heure de fin | 23:30 |
| Intervention_Type | Type (urgent/planned) | urgent |

## 📦 Déploiement sur Streamlit Cloud

1. Poussez votre code sur GitHub
2. Allez sur https://streamlit.io/cloud
3. Connectez-vous avec votre compte GitHub
4. Cliquez sur "New app"
5. Sélectionnez votre repository et le fichier `overtime_calculator_improved.py`
6. Cliquez sur "Deploy"

🎉 Votre app sera en ligne en quelques minutes !

## 🛠️ Technologies utilisées

- **Streamlit** : Framework web pour Python
- **Pandas** : Manipulation de données
- **OpenPyXL** : Lecture/écriture de fichiers Excel
- **Holidays** : Gestion des jours fériés belges

## 📝 Licence

Ce projet est libre d'utilisation pour un usage personnel ou professionnel.

## 🤝 Contribution

Les suggestions et améliorations sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

---

Développé avec ❤️ pour simplifier la gestion des heures supplémentaires
