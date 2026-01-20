# 🎓 Architecture Docker - Explication Complète

## 📐 Vue d'ensemble de l'Architecture

Votre projet suit une architecture **3-tiers** :

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 8080)                 │
│              Node.js - Interface Utilisateur            │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP Requests
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (Port 5000)                    │
│              Flask - API REST (CRUD)                    │
└─────────────────┬───────────────────────────────────────┘
                  │ Read/Write
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  DATABASE (Container)                   │
│          SQLite + Backup Service                        │
│          Volume: ./sqlite_data                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🐳 Détail des Dockerfiles

### 1️⃣ Dockerfile.backend (Service API Flask)

```dockerfile
FROM python:3.11-slim          # Image de base Python (allégée)
WORKDIR /app                   # Répertoire de travail dans le container
RUN mkdir -p /database         # Créer le dossier pour la DB
COPY backend/requirements.txt  # Copier le fichier de dépendances
RUN pip install ...            # Installer Flask, Flask-CORS
EXPOSE 5000                    # Exposer le port 5000
CMD ["python", "app.py"]       # Commande par défaut au démarrage
```

**Pourquoi ça ?**
- `python:3.11-slim` : Image légère avec Python
- `WORKDIR /app` : Tous les fichiers seront dans `/app` dans le container
- Le volume `./backend:/app` dans docker-compose remplace ce qui est copié lors du build
- Les dépendances sont installées dans l'image (Flask, Flask-CORS)

**Important** : Le Dockerfile copie les fichiers **une seule fois lors du build**. Le volume dans docker-compose permet de modifier le code sans rebuilder.

---

### 2️⃣ Dockerfile.frontend (Service Web)

```dockerfile
FROM node:18-alpine            # Image Node.js très légère (Alpine Linux)
WORKDIR /app                   # Répertoire de travail
RUN npm install node-fetch@2   # Installer la dépendance
COPY frontend/ .               # Copier les fichiers frontend
EXPOSE 3000                    # Le serveur Node écoute sur le port 3000
CMD ["node", "server.js"]      # Démarrer le serveur
```

**Pourquoi ça ?**
- `node:18-alpine` : Très petite image (< 50MB)
- Le serveur Node sert simplement les fichiers HTML statiques
- Le volume `./frontend:/app` permet de modifier les fichiers sans rebuilder

---

### 3️⃣ Dockerfile.sqlite (Service de Gestion de la DB)

```dockerfile
FROM python:3.11-slim          # Image Python
RUN mkdir -p /database /backup # Créer 2 dossiers
CMD sh -c "while true; do ..." # Boucle infinie pour les backups
```

**C'est quoi ce script ?**
```bash
while true; do                          # Boucle infinie
    if [ -f /database/app.db ]; then    # Si le fichier DB existe
        cp /database/app.db /backup/... # Copier vers backup
    fi
    sleep 10                            # Attendre 10 secondes
done
```

**Pourquoi ça ?**
- Ce container ne fait QUE des backups automatiques
- Il vérifie toutes les 10 secondes si `app.db` existe et le sauvegarde
- Le container reste actif grâce à cette boucle infinie

---

## 🎯 Docker Compose - L'Orchestrateur

Docker Compose est comme un **chef d'orchestre** qui coordonne tous les containers.

### Structure générale :

```yaml
version: '3.9'           # Version du format docker-compose

services:                # Les différents services (containers)
  service1: ...
  service2: ...

networks:                # Réseau virtuel entre containers
  app_network: ...

volumes:                 # Stockage persistant
  sqlite_data: ...
```

---

## 🔍 Analyse Service par Service

### 1. Service `database`

```yaml
database:
  container_name: sqlite_db              # Nom explicite du container
  build:
    context: .                           # Chemin relatif depuis le dossier courant
    dockerfile: docker/Dockerfile.sqlite # Quel Dockerfile utiliser
  volumes:
    - ./sqlite_data:/database            # Volume partagé (hôte → container)
    - ./sqlite_data/backups:/backup      # Dossier backups sur l'hôte
  networks:
    - app_network                        # Connecté au réseau virtuel
```

**Volumes expliqués :**
```
./sqlite_data:/database
│             │
│             └─ Chemin DANS le container
└─ Chemin sur votre machine (hôte)

→ Tout ce qui est écrit dans /database du container
  est écrit dans ./sqlite_data sur votre machine !
```

**Pourquoi 2 volumes ?**
- `/database` : Base de données partagée avec le backend
- `/backup` : Sauvegardes (accessibles depuis l'hôte)

---

### 2. Service `backend`

```yaml
backend:
  container_name: flask_app
  build:
    context: .
    dockerfile: docker/Dockerfile.backend
  ports:
    - "5000:5000"              # Hôte:Container (expose le port)
  volumes:
    - ./backend:/app           # Code source (développement)
    - ./sqlite_data:/database  # MÊME volume que database !
  depends_on:
    - database                 # Attendre que database démarre
  networks:
    - app_network
  command: ["python", "app.py"] # Override le CMD du Dockerfile
```

**Points clés :**

1. **`ports: "5000:5000"`** :
   ```
   Format: "HÔTE:CONTAINER"
   → http://localhost:5000 (votre machine)
     → redirige vers port 5000 du container
   ```

2. **Volume `./backend:/app`** :
   - Modifications du code reflétées immédiatement
   - Pas besoin de rebuilder après chaque changement

3. **Volume `./sqlite_data:/database`** :
   - **Partage le MÊME dossier** que le service database
   - Le backend lit/écrit dans le même fichier `app.db`

4. **`depends_on: database`** :
   - Docker attend que `database` soit démarré avant `backend`
   - Ordre de démarrage garanti

---

### 3. Service `frontend`

```yaml
frontend:
  container_name: frontend_app
  build:
    context: .
    dockerfile: docker/Dockerfile.frontend
  ports:
    - "8080:3000"             # Port 8080 sur hôte → 3000 dans container
  volumes:
    - ./frontend:/app         # Code frontend monté
  depends_on:
    - backend                 # Attendre le backend
  networks:
    - app_network
```

**Points clés :**

1. **`ports: "8080:3000"`** :
   - Le serveur Node écoute sur le port **3000** dans le container
   - Accessible via le port **8080** depuis votre machine
   - URL : http://localhost:8080

2. **`depends_on: backend`** :
   - S'assure que le backend est prêt avant de démarrer le frontend

---

## 🌐 Réseau (Networking)

```yaml
networks:
  app_network:
    driver: bridge
```

**Comment ça marche ?**

Tous les containers sont sur le **même réseau virtuel** :

```
┌─────────────────────────────────────────┐
│         app_network (bridge)            │
│                                         │
│  ┌──────────┐      ┌──────────┐       │
│  │ frontend │◄────►│ backend  │       │
│  └──────────┘      └────┬─────┘       │
│                         │              │
│                    ┌────▼─────┐       │
│                    │ database │       │
│                    └──────────┘       │
└─────────────────────────────────────────┘
```

**Avantages :**
- Les containers peuvent communiquer entre eux par **nom de service**
- Exemple : `http://backend:5000` depuis le frontend
- **Isolation** : Les containers ne sont pas accessibles depuis l'extérieur sauf via les ports exposés

**Noms de service = DNS interne :**
- `backend` → résout vers l'IP du container backend
- `database` → résout vers l'IP du container database
- `frontend` → résout vers l'IP du container frontend

---

## 💾 Gestion des Volumes

### Volume Partagé : La Clé de Votre Architecture

```yaml
# Dans database
volumes:
  - ./sqlite_data:/database

# Dans backend
volumes:
  - ./sqlite_data:/database
```

**Schéma de Partage :**

```
Votre Machine (Hôte)
└── ./sqlite_data/
    └── app.db                    ← Un seul fichier physique

        ├── Container database
        │   └── /database/app.db  ← Point d'accès 1
        │
        └── Container backend
            └── /database/app.db  ← Point d'accès 2

→ Les deux containers voient le MÊME fichier !
→ Modifications depuis l'un OU l'autre → visibles partout
```

**Exemple concret :**

1. **Backend écrit** dans `/database/app.db` → Modifie `./sqlite_data/app.db` sur votre machine
2. **Container database** peut lire `./sqlite_data/app.db` via `/database/app.db`
3. **Vous sur votre machine** pouvez aussi accéder à `./sqlite_data/app.db`

**C'est ça la magie des volumes !** 🔮

---

## 🔄 Flux de Données Complet

### Scénario : Créer un utilisateur via le frontend

```
1. Utilisateur remplit le formulaire sur http://localhost:8080
   │
   ▼
2. JavaScript dans index.html fait un fetch
   → fetch('http://localhost:5000/api/users', { method: 'POST', ... })
   │
   ▼
3. Requête HTTP arrive au container backend (port 5000)
   │
   ▼
4. Flask (app.py) reçoit la requête sur /api/users (POST)
   │
   ▼
5. app.py appelle db.create_user(username, password)
   │
   ▼
6. db.py ouvre une connexion à /database/app.db
   │
   ▼
7. SQLite écrit dans le fichier partagé
   → ./sqlite_data/app.db est modifié
   │
   ▼
8. Container database détecte le changement (dans 10 secondes max)
   → Copie app.db vers /backup/app.db.backup
   │
   ▼
9. Flask renvoie une réponse JSON au frontend
   │
   ▼
10. Frontend affiche le nouvel utilisateur dans la liste
```

---

## 🎯 Pourquoi Cette Architecture ?

### Avantages :

1. **Isolation** : Chaque service est dans son propre container
   - Si le frontend crash, le backend continue
   - Chaque service a ses propres dépendances

2. **Scalabilité** : Facile d'ajouter des instances
   ```yaml
   # On pourrait faire :
   backend:
     deploy:
       replicas: 3  # 3 instances du backend
   ```

3. **Développement** : Volumes permettent de modifier le code sans rebuilder
   - Changez `backend/app.py` → changements immédiats dans le container

4. **Production-ready** : Même configuration locale et production
   - Modifiez juste les ports/variables d'environnement

5. **Persistance** : Les données survivent aux redémarrages
   - `./sqlite_data` reste sur votre machine même si vous supprimez les containers

---

## 🔧 Commandes Utiles

### Build et démarrage
```bash
make all        # Build et démarre tous les services
make clean      # Arrête les containers
make fclean     # Arrête + supprime les images
make re         # Rebuild complet
```

### Commandes Docker Compose équivalentes
```bash
docker-compose -p ex2 up -d --build    # Démarrer
docker-compose -p ex2 down             # Arrêter
docker-compose -p ex2 logs -f backend  # Voir les logs
docker-compose -p ex2 ps               # État des services
```

---

## 🎓 Concepts Clés à Retenir

1. **Dockerfile** = Recette pour créer une image
   - Instructions pour construire l'environnement
   - Exécuté une fois lors du `build`

2. **Docker Compose** = Orchestrateur de containers
   - Définit les services, réseaux, volumes
   - Gère les dépendances et l'ordre de démarrage

3. **Volume** = Pont entre hôte et container
   - Permet la persistance des données
   - Permet le partage entre containers

4. **Réseau** = Communication entre containers
   - Les containers se parlent par nom de service
   - Isolation par défaut

5. **Port Mapping** = Exposition vers l'extérieur
   - `"8080:3000"` = port 8080 de la machine → port 3000 du container

---

## 🎉 Résumé en Une Ligne

**Docker Compose orchestre 3 containers isolés qui communiquent via un réseau virtuel et partagent des données via des volumes montés depuis l'hôte.**

Voilà ! C'est toute l'architecture de votre projet ! 🚀
