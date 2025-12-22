# Contexte

À la fin des TP précédents, nous avons mis en place un pipeline de données opérationnel capable d’ingérer des fichiers CSV mensuels dans une base PostgreSQL, de valider les données via Great Expectations, puis de figer leur état à l’aide de snapshots temporels. Ces derniers couvrent actuellement deux dates clés (2024-01-31 et 2024-02-29) et portent sur plusieurs tables métiers : utilisateurs, abonnements, usages agrégés, paiements et support client. Ce TP3 a pour objectif de connecter ces données historisées à un Feature Store (Feast) afin de préparer l’entraînement d’un futur modèle de churn. Nous allons définir des features réutilisables à partir des snapshots, les extraire en mode offline pour constituer un dataset d’entraînement, et en mode online pour des usages en temps réel. Enfin, nous exposerons ces features via un endpoint API simple pour illustrer leur intégration dans une architecture de production.

# Mise en place de Feast

docker compose up -d --build

Le conteneur Feast permet d’exécuter Feast dans un environnement isolé, incluant Python et ses dépendances nécessaires. 
La configuration du Feature Store est située dans le répertoire `/repo` à l’intérieur du conteneur, ce dossier étant monté en volume depuis `./services/feast_repo/repo` sur l’hôte. 
Pour utiliser Feast, il suffira d’exécuter des commandes via `docker compose exec feast`.

# Définition du Feature Store

Dans Feast, une Entity représente l’objet métier pour lequel les features sont définies et récupérées.
Dans notre cas, user_id est un choix idéal comme clé de jointure, car il s’agit déjà d’une clé stable et commune à l’ensemble de nos tables (users, subscriptions, snapshots, etc.), garantissant ainsi des jointures cohérentes entre les différentes sources de données.

La table usage_agg_30d_snapshots contient des features comme watch_hours_30d, avg_session_mins_7d, unique_devices_30 , skips_7d.

La colonne as_of sert de référence temporelle (timestamp_field) pour permettre à Feast de faire des jointures point-in-time correctes.

feast apply : Lit la configuration du Feature Store (entities, sources, feature views) et crée ou met à jour le registre Feast (registry.db).
Ce registre sert de "source de vérité" pour tous les objets Feast définis. Il est ensuite utilisé pour effectuer les récupérations offline/online et pour matérialiser les données vers l’online store.

# Récupération offline & online

docker compose exec prefect python build_training_dataset.py

5 premières lignes :

user@w-yboutkri:~/projects/systeme1$ head -5 data/processed/training_df.csv
user_id,event_timestamp,months_active,monthly_fee,paperless_billing,watch_hours_30d,avg_session_mins_7d,failed_payments_90d,churn_label
7590-VHVEG,2024-01-31,1,29.85,True,24.4836507667874,29.141044640845102,1,True
5575-GNVDE,2024-01-31,34,56.95,False,30.0362276875424,29.141044640845102,0,False
3668-QPYBK,2024-01-31,2,53.85,True,26.7068107231889,29.141044640845102,1,False
7795-CFOCW,2024-01-31,45,42.300000000000004,False,21.8920408062136,29.141044640845102,1,True

Feast assure la cohérence temporelle grâce au paramètre `timestamp_field="as_of"` dans les `PostgreSQLSource`, qui associe chaque feature à une date précise correspondant au snapshot.  
Dans `entity_df`, on fournit `user_id` et `event_timestamp`, ce qui permet à Feast de récupérer les valeurs valides à cette date spécifique via une jointure temporelle point-in-time, garantissant ainsi qu’aucune information "future" n’est utilisée pour une date donnée.

Online features for user: 7590-VHVEG
{'user_id': ['7590-VHVEG'], 'months_active': [1], 'monthly_fee': [29.850000381469727], 'paperless_billing': [True]}

Online features for user: 1234
{'user_id': ['1234'], 'monthly_fee': [None], 'paperless_billing': [None], 'months_active': [None]}
Si on interroge un `user_id` sans features matérialisées, Feast renvoie des valeurs `None`.

user@w-yboutkri:~/projects/systeme1$ curl http://localhost:8000/health

{"status":"ok sa roule"}

user@w-yboutkri:~/projects/systeme1$ curl http://localhost:8000/features/7590-VHVEG

{"user_id":"7590-VHVEG","features":{"monthly_fee":29.850000381469727,"months_active":1,"paperless_billing":true}}


# Réflexion

Cet endpoint minimise le risque de *training-serving skew*, car il délivre en production des features calculées à partir des mêmes définitions (FeatureViews Feast) que celles utilisées pour générer le dataset d'entraînement via `get_historical_features`.  
Cela évite de reproduire manuellement le calcul des features dans l’API, limitant ainsi les risques d’incohérences.  
De plus, toute modification des features est centralisée dans Feast, ce qui garantit une mise à jour uniforme, aussi bien pour l'entraînement des modèles (offline) que pour leur utilisation en production (online).