Exercice 1: 

A :

user@w-yboutkri:~/projects/systeme1$ ls
api  data  db  docker-compose.yml  reports  services

B : 

user@w-yboutkri:~/projects/systeme1$ ls data/seeds/month_000
labels.csv  payments_agg_90d.csv  subscriptions.csv  support_agg_90d.csv  usage_agg_30d.csv  users.csv


Exercice 2 :

A : 

Fichier db/init/001_schema.sql créé.


B : 

Le fichier .env stocke les variables d’environnements. Docker Compose les injecte automatiquement dans les conteneurs pour séparer la configuration du code.

C : 

La commande \dt montre les tables créées automatiquement grâce au script 001_schema.sql.

user@w-yboutkri:~/projects/systeme1$ docker compose exec postgres psql -U streamflow -d streamflow
psql (16.11 (Debian 16.11-1.pgdg13+1))
Type "help" for help.

streamflow=# \dt
               List of relations
 Schema |       Name       | Type  |   Owner    
--------+------------------+-------+------------
 public | labels           | table | streamflow
 public | payments_agg_90d | table | streamflow
 public | subscriptions    | table | streamflow
 public | support_agg_90d  | table | streamflow
 public | usage_agg_30d    | table | streamflow
 public | users            | table | streamflow
(6 rows)


Exercice 3 : 

A : 

Le conteneur prefect héberge le serveur Prefect + un worker qui exécute le flow d’ingestion.

B :

upsert_csv : lit un CSV, crée une table temporaire, y insère les données puis exécute un INSERT ... ON CONFLICT DO UPDATE pour effectuer un upsert.
Si la clé primaire existe déjà, les colonnes non-PK sont mises à jour, sinon une nouvelle ligne est créée.

C : 

user@w-yboutkri:~/projects/systeme1$ docker compose exec postgres psql -U streamflow -d streamflow
psql (16.11 (Debian 16.11-1.pgdg13+1))
Type "help" for help.

streamflow=# SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM subscriptions;
 count 
-------
  7043
(1 row)

 count 
-------
  7043
(1 row)

streamflow=# 

Après ingestion de month_000, les table contiennent 7043 lignes, soit 7043 clients.

Exercice 4 : 

A :

La fonction validate_with_ge applique des règles Great Expectations sur les tables chargées.
-> Si une expectation échoue, elle lève une exception et fait échouer le flow Prefect.

Pour usage_agg_30d, nous forçons les colonnes watch_hours_30d, avg_session_mins_7d, unique_devices_30d, skips_7d et rebuffer_events_7d à être ≥ 0, car ce sont des compteurs ou durées qui ne peuvent pas être négatifs.

Exercice 5 : 

A : 

La fonction snapshot_month(as_of) crée les tables de snapshots et copie l’état des tables live vers des tables *_snapshots en ajoutant une colonne as_of. 
-> Cela permet de figer l’état des données à la fin de chaque mois et de conserver l’historique temporel.

B : 
 

streamflow=# SELECT COUNT(*) FROM subscriptions_profile_snapshots WHERE as_of = '2024-01-31';
 count 
-------
  7043
(1 row)

streamflow=# SELECT COUNT(*) FROM subscriptions_profile_snapshots WHERE as_of = '2024-02-29';
 count 
-------
  7043
(1 row)

streamflow=# 


C : 

Pourquoi on ne travaille pas directement sur les tables live ?

Les tables live sont en constante évolution. Entraîner un modèle sur ces données rend impossible la reproduction d’une expérience et peut entraîner du data leakage, où le modèle "anticipe" en exploitant des informations futures.


Pourquoi les snapshots sont importants ?

Les snapshots capturent l’état des features à une date as_of, ce qui garantit la reproductibilité des entraînements, le respect de la chronologie des données et empêche le modèle d’exploiter des informations qui n’étaient pas accessibles à l’époque.


Réflexion perso :

Le plus compliqué a été de gérer correctement l’upsert et les clauses ON CONFLICT. J’ai également rencontré des erreurs du type "relation does not exist", que j’ai résolues en vérifiant l’ordre d’exécution des DDL et des INSERT, ainsi que les noms des tables.


Schéma ASCII : 

        +----------------------+
        |         CSVs         |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |  ingest_month_flow() |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |   upsert_csv()       |
        |   (tables live)      |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | validate_with_ge()   |
        |  (contrôle qualité)  |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |  snapshot_month()    |
        | (création snapshots) |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |   PostgreSQL final   |
        | (Tables live + snaps)|
        +----------------------+


