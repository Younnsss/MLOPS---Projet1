Exercice 1 :

user@w-yboutkri:~/projects/MLOPS---Projet1$ docker compose up -d
                                                                                                                        0.0s 
 ✔ Container mlops---projet1-postgres-1 Created                                                                                                                                0.0s 
 ✔ Container mlops---projet1-mlflow-1   Created                                                                                                                                0.0s 
 ✔ Container mlops---projet1-prefect-1  Created                                                                                                                                0.0s 
 ✔ Container mlops---projet1-feast-1    Created                                                                                                                                0.0s 
 ✔ Container mlops---projet1-api-1      Created                                                                                                                                0.0s 
 ✔ Container streamflow-prometheus      Created                                                                                                                                0.0s 
 ✔ Container streamflow-grafana         Created                                                                                         0.0s 

user@w-yboutkri:~/projects/MLOPS---Projet1$ docker compose ps
NAME                         IMAGE                           COMMAND                  SERVICE      CREATED              STATUS          PORTS
mlops---projet1-api-1        mlops---projet1-api             "uvicorn app:app --h…"   api          About a minute ago   Up 59 seconds   0.0.0.0:8000->8000/tcp
mlops---projet1-feast-1      mlops---projet1-feast           "bash -lc 'tail -f /…"   feast        About a minute ago   Up 59 seconds   
mlops---projet1-mlflow-1     ghcr.io/mlflow/mlflow:v2.16.0   "mlflow server --bac…"   mlflow       About a minute ago   Up 59 seconds   0.0.0.0:5000->5000/tcp
mlops---projet1-postgres-1   postgres:16                     "docker-entrypoint.s…"   postgres     About a minute ago   Up 59 seconds   0.0.0.0:5432->5432/tcp
mlops---projet1-prefect-1    mlops---projet1-prefect         "/usr/bin/tini -g --…"   prefect      About a minute ago   Up 59 seconds   
streamflow-grafana           grafana/grafana:11.2.0          "/run.sh"                grafana      About a minute ago   Up 58 seconds   0.0.0.0:3000->3000/tcp
streamflow-prometheus        prom/prometheus:v2.55.1         "/bin/prometheus --c…"   prometheus   About a minute ago   Up 58 seconds   0.0.0.0:9090->9090/tcp


![alt text](image-1.png)


Exercice 2 :

(venv) user@w-yboutkri:~/projects/MLOPS---Projet1$ pytest -q
..                                                                                                                                                                           [100%]
2 passed in 0.02s

Une fonction pure est isolée (sans dépendances spécifiques comme Prefect/MLflow, et sans opérations d'entrée/sortie), permettant de tester la logique décisionnelle de manière rapide, déterministe et indépendante de toute infrastructure externe.