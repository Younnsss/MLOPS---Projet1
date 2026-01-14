Exercice 1 :

user@w-yboutkri:~/projects/MLOPS---Projet1$ docker compose up -d
0.0s
✔ Container mlops---projet1-postgres-1 Created 0.0s
✔ Container mlops---projet1-mlflow-1 Created 0.0s
✔ Container mlops---projet1-prefect-1 Created 0.0s
✔ Container mlops---projet1-feast-1 Created 0.0s
✔ Container mlops---projet1-api-1 Created 0.0s
✔ Container streamflow-prometheus Created 0.0s
✔ Container streamflow-grafana Created 0.0s

user@w-yboutkri:~/projects/MLOPS---Projet1$ docker compose ps
NAME IMAGE COMMAND SERVICE CREATED STATUS PORTS
mlops---projet1-api-1 mlops---projet1-api "uvicorn app:app --h…" api About a minute ago Up 59 seconds 0.0.0.0:8000->8000/tcp
mlops---projet1-feast-1 mlops---projet1-feast "bash -lc 'tail -f /…" feast About a minute ago Up 59 seconds  
mlops---projet1-mlflow-1 ghcr.io/mlflow/mlflow:v2.16.0 "mlflow server --bac…" mlflow About a minute ago Up 59 seconds 0.0.0.0:5000->5000/tcp
mlops---projet1-postgres-1 postgres:16 "docker-entrypoint.s…" postgres About a minute ago Up 59 seconds 0.0.0.0:5432->5432/tcp
mlops---projet1-prefect-1 mlops---projet1-prefect "/usr/bin/tini -g --…" prefect About a minute ago Up 59 seconds  
streamflow-grafana grafana/grafana:11.2.0 "/run.sh" grafana About a minute ago Up 58 seconds 0.0.0.0:3000->3000/tcp
streamflow-prometheus prom/prometheus:v2.55.1 "/bin/prometheus --c…" prometheus About a minute ago Up 58 seconds 0.0.0.0:9090->9090/tcp

![alt text](image-1.png)

Exercice 2 :

(venv) user@w-yboutkri:~/projects/MLOPS---Projet1$ pytest -q
.. [100%]
2 passed in 0.02s

Une fonction pure est isolée (sans dépendances spécifiques comme Prefect/MLflow, et sans opérations d'entrée/sortie), permettant de tester la logique décisionnelle de manière rapide, déterministe et indépendante de toute infrastructure externe.

Exercice 3 :

![alt text](image-2.png)

![alt text](image-3.png)

On impose un delta pour éviter de promouvoir un modèle pour un gain trop faible, souvent à cause du hasard du split ou au bruit statistique.

Exercice 4 :

![alt text](image-4.png)

![alt text](image-5.png)

Exercice 5 :

younes@younes-XMG-CORE-REN-E21:~/Bureau/work/MLOPS---Projet1$ curl -s -X POST "http://localhost:8000/predict" \
 -H "Content-Type: application/json" \
 -d '{"user_id":"7590-VHVEG"}' | jq
{
"user_id": "7590-VHVEG",
"prediction": 1,
"features": {
"user_id": "7590-VHVEG",
"net_service": "DSL",
"plan_stream_movies": false,
"monthly_fee": 29.850000381469727,
"plan_stream_tv": false,
"paperless_billing": true,
"months_active": 1,
"skips_7d": 4,
"watch_hours_30d": 24.48365020751953,
"unique_devices_30d": 3,
"rebuffer_events_7d": 1,
"avg_session_mins_7d": 29.14104461669922,
"failed_payments_90d": 1,
"ticket_avg_resolution_hrs_90d": 16.0,
"support_tickets_90d": 0
}
}

l’API charge le modèle MLflow au démarrage et le garde en mémoire.
Il faut redémarrer le service pour recharger la nouvelle version Production après une promotion dans le registry.

Exercice 6 :
![alt text](image-38.png)

On démarre Docker Compose dans la CI pour valider l’intégration multi-services (DB/Feast/MLflow/API) et vérifier que l’API démarre correctement et répond au healthcheck, ce que des tests unitaires seuls ne couvrent pas.

## Synthèse – Monitoring, réentraînement et CI/CD

Dans ce projet, le drift des données est mesuré à l’aide d’Evidently en comparant une période de référence à une période courante. Le principal indicateur utilisé est le drift_share, qui représente la proportion de features présentant un drift statistiquement significatif. Un seuil de déclenchement est fixé à 0.02 afin d’automatiser la décision de réentraînement. Dans un contexte réel, ce seuil serait généralement plus élevé afin d’éviter des réentraînements trop fréquents dus au bruit ou à des variations normales des données.

Lorsque le drift dépasse le seuil, le flow train_and_compare_flow est déclenché. Ce flow construit un dataset cohérent à une date as_of, entraîne un modèle candidat, et évalue ses performances sur un jeu de validation via la métrique val_auc. En parallèle, le modèle actuellement en Production est évalué sur exactement le même split de données. La décision de promotion repose sur une règle simple et testée unitairement : le modèle candidat est promu uniquement si son val_auc dépasse celui du modèle en Production d’au moins un delta. Ce delta permet d’éviter des promotions dues à des gains marginaux ou aléatoires.

Les responsabilités sont clairement séparées entre les outils :

Prefect orchestre les workflows métier (monitoring, entraînement, comparaison, promotion) et gère la logique MLOps dynamique.

GitHub Actions assure la CI : exécution des tests unitaires rapides et vérification que la stack Docker démarre correctement via un healthcheck. Aucun entraînement complet n’y est exécuté.

## Limites et améliorations

La CI ne doit pas entraîner le modèle complet, car l’entraînement est coûteux, lent et non déterministe, ce qui rendrait les pipelines instables et difficiles à maintenir.
Plusieurs tests manquent encore, notamment des tests d’intégration fonctionnels sur les flows Prefect, des tests de non-régression sur les métriques, et des tests de robustesse sur les données en entrée.
Enfin, en production réelle, une approbation humaine est souvent nécessaire avant toute promotion : gouvernance ML, contraintes réglementaires, validation métier et analyse d’impact sont essentielles pour éviter des déploiements automatiques risqués.
