# Agent RAG sur documents

Chatbot RAG (retrieval-augmented generation) : il répond à des questions en se basant **uniquement** sur un corpus de documents indexés, et cite systématiquement ses sources. Backend FastAPI + génération via l'API Claude (Anthropic), retrieval local avec ChromaDB.

Projet de démonstration pour un profil freelance orienté automatisation IA / agents LLM.

## Démo incluse

Le dépôt contient un corpus fictif de documentation produit (« NovaTrack », un outil de gestion de projet imaginaire) : guide produit, FAQ, politique de remboursement. Ça permet de tester l'agent immédiatement sans avoir besoin de vos propres documents.

## Architecture

```
Question utilisateur
      │
      ▼
Embeddings locaux (sentence-transformers, all-MiniLM-L6-v2)
      │
      ▼
Recherche vectorielle (ChromaDB, stockage local persistant)
      │
      ▼
Chunks pertinents + question ──► Claude (API Anthropic, réponse en streaming)
      │
      ▼
Réponse citée, streamée vers le navigateur (SSE)
```

Point clé : la génération (Claude) et les embeddings (sentence-transformers, local) sont découplés. Une seule clé API est nécessaire (Anthropic) ; la recherche vectorielle ne coûte rien et fonctionne hors-ligne.

## Stack

- **Backend** : FastAPI + Uvicorn
- **LLM** : API Anthropic (Claude), réponses en streaming (SSE)
- **Embeddings** : `sentence-transformers` (modèle local, gratuit, pas de clé API nécessaire)
- **Vector store** : ChromaDB (persistant, local, aucun service externe)
- **Frontend** : HTML/CSS/JS vanilla (pas de framework)

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copiez `.env.example` en `.env` et renseignez votre clé API Anthropic :

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-5
```

Récupérez une clé sur [console.anthropic.com](https://console.anthropic.com/).

### Choisir le modèle

Le modèle par défaut est `claude-opus-5` (le plus capable). Pour une démo à moindre coût, changez simplement `CLAUDE_MODEL` dans `.env` :

| Modèle | Usage recommandé |
|---|---|
| `claude-opus-5` | Qualité maximale, par défaut |
| `claude-sonnet-5` | Bon compromis qualité/coût pour la plupart des cas |
| `claude-haiku-4-5` | Le moins cher, pour des démos à fort volume de requêtes |

## Utilisation

**1. Indexer les documents** (à refaire à chaque fois que le corpus change) :

```bash
python -m app.ingest
```

**2. Lancer le serveur** :

```bash
uvicorn app.main:app --reload
```

Ouvrez [http://localhost:8000](http://localhost:8000).

## Utiliser vos propres documents

1. Remplacez le contenu de `data/documents/` par vos fichiers `.md` ou `.txt` (un fichier par document source ; le nom du fichier sert d'identifiant de source dans les citations).
2. Relancez `python -m app.ingest`.
3. Redémarrez le serveur si besoin.

Pour des PDF ou d'autres formats, il faut adapter `app/ingest.py` (`load_documents`) pour extraire le texte avant de le passer à `chunk_text`.

## Tests

```bash
pytest
```

Les tests couvrent la logique de découpage en chunks (`app/chunking.py`) — la partie la plus facile à casser silencieusement lors d'une modification.

## Limites de cette démo

- Corpus statique : pas d'upload de documents depuis l'interface (ajouté volontairement hors scope pour limiter les coûts et les risques d'abus sur une démo publique).
- Pas de gestion multi-utilisateur ni d'historique de conversation persistant.
- Pas de cache de prompt (`prompt caching`) — pertinent seulement à partir d'un volume de requêtes significatif.

## Aller plus loin

- Ajouter l'upload de documents par l'utilisateur (avec limites de taille/type et isolation par session).
- Ajouter un historique de conversation multi-tours.
