# Guide produit — NovaTrack

NovaTrack est un outil de gestion de projet en ligne conçu pour les petites équipes (2 à 20 personnes). Il combine un tableau Kanban, un suivi du temps passé et des rapports d'avancement automatiques.

## Fonctionnalités principales

**Tableaux Kanban.** Chaque projet possède un tableau personnalisable avec des colonnes libres (par défaut : À faire, En cours, En révision, Terminé). Les cartes peuvent contenir des sous-tâches, des pièces jointes (jusqu'à 25 Mo par fichier) et des commentaires.

**Suivi du temps.** Un chronomètre intégré permet de suivre le temps passé sur chaque tâche. Les données sont exportables au format CSV ou directement synchronisées avec les outils de facturation compatibles (voir la section Intégrations).

**Rapports automatiques.** Chaque lundi matin, NovaTrack génère un résumé de la semaine précédente par e-mail : tâches terminées, retards, charge de travail par membre de l'équipe. Ce rapport est activé par défaut mais peut être désactivé dans les paramètres de notification.

**Automatisations.** Il est possible de créer des règles simples du type « quand une carte passe en colonne Terminé, notifier le chef de projet » ou « quand une carte reste plus de 5 jours sans activité, l'étiqueter En retard ».

## Intégrations disponibles

NovaTrack se connecte avec Slack, Google Calendar, GitHub et Stripe (pour la facturation). L'intégration GitHub permet de lier automatiquement une carte à une pull request : la carte passe en colonne En révision dès l'ouverture de la PR et en colonne Terminé dès le merge.

## Limites techniques

- Nombre de projets par espace de travail : illimité sur les forfaits Équipe et Entreprise, 3 maximum sur le forfait Solo.
- Taille maximale d'une pièce jointe : 25 Mo.
- Historique des activités conservé 12 mois glissants, sauf sur le forfait Entreprise où il est illimité.
- L'application mobile (iOS et Android) permet la consultation et la mise à jour des tâches, mais pas la création de nouveaux tableaux.
