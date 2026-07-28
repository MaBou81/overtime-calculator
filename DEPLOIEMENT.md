# 🚀 Guide de déploiement - Étape par étape

## 📌 Étape 1 : Créer un compte GitHub

1. Va sur **https://github.com**
2. Clique sur **"Sign up"** (Inscription)
3. Entre ton email, crée un mot de passe et choisis un nom d'utilisateur
4. Vérifie ton email
5. ✅ Ton compte GitHub est créé !

---

## 📌 Étape 2 : Créer un nouveau repository (dépôt)

1. Une fois connecté sur GitHub, clique sur le **bouton vert "New"** (ou le **+** en haut à droite → "New repository")
2. Donne un nom à ton projet, par exemple : **`overtime-calculator`**
3. Ajoute une description (optionnel) : *"Calculateur d'heures supplémentaires"*
4. Laisse le repo en **Public** (nécessaire pour la version gratuite de Streamlit Cloud)
5. ✅ **Coche "Add a README file"** (on le remplacera après)
6. Clique sur **"Create repository"**

---

## 📌 Étape 3 : Upload tes fichiers sur GitHub

### Option A : Via l'interface web (le plus simple)

1. Sur la page de ton nouveau repository, clique sur **"Add file"** → **"Upload files"**
2. Glisse-dépose ces 4 fichiers :
   - `overtime_calculator_improved.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
3. En bas de la page, écris un message de commit, par exemple : *"Initial commit"*
4. Clique sur **"Commit changes"**
5. ✅ Tes fichiers sont maintenant sur GitHub !

### Option B : Via Git en ligne de commande (pour les avancés)

```bash
# Dans le dossier contenant tes fichiers
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON-USERNAME/overtime-calculator.git
git push -u origin main
```

---

## 📌 Étape 4 : Créer un compte Streamlit Community Cloud

1. Va sur **https://streamlit.io/cloud**
2. Clique sur **"Sign up"**
3. **Connecte-toi avec GitHub** (c'est le plus simple !)
4. Autorise Streamlit à accéder à ton compte GitHub
5. ✅ Ton compte Streamlit Cloud est créé !

---

## 📌 Étape 5 : Déployer ton app

1. Sur le dashboard Streamlit Cloud, clique sur **"New app"**
2. Remplis les informations :
   - **Repository** : Sélectionne `TON-USERNAME/overtime-calculator`
   - **Branch** : `main`
   - **Main file path** : `overtime_calculator_improved.py`
3. Clique sur **"Deploy!"**
4. ⏳ Attends 2-3 minutes que l'app se déploie
5. 🎉 **C'est en ligne !** Tu auras une URL du type : `https://ton-app.streamlit.app`

---

## 📌 Étape 6 : Partager ton app

Tu peux maintenant partager le lien de ton app avec qui tu veux ! 🚀

**Ton URL sera du genre :**
```
https://overtime-calculator-abc123.streamlit.app
```

---

## 🔄 Mettre à jour l'app plus tard

Si tu veux modifier ton code :

1. Modifie ton fichier localement
2. Upload le nouveau fichier sur GitHub (remplace l'ancien)
3. Streamlit Cloud détectera automatiquement le changement et redéploiera l'app ! ✨

---

## ❓ Problèmes courants

### L'app ne démarre pas
- Vérifie que `requirements.txt` est bien dans le repo
- Vérifie les logs dans Streamlit Cloud (bouton "Manage app" → "Logs")

### Erreur "Module not found"
- Assure-toi que toutes les dépendances sont dans `requirements.txt`

### Le repo n'apparaît pas dans Streamlit Cloud
- Assure-toi que le repo est **Public**
- Réautorise l'accès GitHub dans les paramètres Streamlit

---

## 📞 Besoin d'aide ?

Si tu bloques quelque part, n'hésite pas à demander de l'aide ! 😊

**Liens utiles :**
- Documentation Streamlit : https://docs.streamlit.io
- GitHub Guides : https://guides.github.com
- Streamlit Community : https://discuss.streamlit.io
