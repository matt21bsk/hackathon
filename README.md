# ETL Apache Airflow

Ce repository permet de déployer un **ETL via Apache Airflow** pour alimenter une base de données au format OMOP depuis une base de données source.

Il est basé sur le repository [Environnement-Hackathon-EDS](https://github.com/GIRCI-SOHO-Hackathon-EDS/Environnement-Hackathon-EDS) qui permet de déployer :
- Une base de données source contenant des fausses données ;
- Une base de données clible au format OMOP.

## Configration de l'environnement virtuel pour Apache Airflow
1. Créer un environnement python virtuel avec `venv`
```bash
python3 -m venv env
```

2. Sourcer l'environnement virtuel
```bash
source ./env/bin/activate
```

3. Installer les dépendences
```bash
pip install -r requierments.txt
```

## Déploiement d'Apache Airflow

1. Créer un fichier `.env` sur la base du fichier `.env.example` et adaptez le si nécessaire :
```bash
cp .env.example .env
```

2. Déployer Airflow en lançant la commande suivante :
```bash
./start.sh
```

Airflow est accessible via http://localhost:8080 (le port peut varier en fonction du paramètre `AIRFLOW__WEBSERVER__PORT` défini dans le fichier `.env`).

**Attention, le déploiement proposé ici n'est pas sécurisé, à ne pas utiliser en production.** Au premier lancement, le mot de passe administrateur permettant de se connecté à Apache Airflow est affiché dans le terminal. Il peut être modifié via le fichier `airflow/simple_auth_manager_passwords.json.generated`.

## Confguration d'Apache Airflow

Les connections aux bases de données source et cible peuvent être configuré via l'UI d'Apache Airflow :
- Connectez vous avec le compte administrateur à Apache Airflow
- Dans `Admin` > `Connection` vous pouvez ajouter des connection en sélectionnant **Ajouter une connection**. Par défaut :
    * Connection vers la base de données source (tel que définit dans `source.env`) :
        + ID de connection : `hackathon_source`
        + Type de connection : `Postgres`
        + Hôte : `localhost`
        + Identifiant : `postgres` (cf. `POSTGRES_USER`)
        + Mot de passe : `awesomePasswdS0urce` (cf. `POSTGRES_PASSWORD`)
        + Port : `5432` (cf. port mapping)
        + Schéma : `postgres` (cf. `POSTGRES_DB`)
    * Connection vers la base de données clible (tel que définit dans `target.env`) :
        + ID de connection : `hackathon_target`
        + Type de connection : `Postgres`
        + Hôte : `localhost`
        + Identifiant : `postgres` (cf. `POSTGRES_USER`)
        + Mot de passe : `awesomePasswdC1ble` (cf. `POSTGRES_PASSWORD`)
        + Port : `5433` (cf. port mapping)
        + Schéma : `postgres` (cf. `POSTGRES_DB`)

Les information de connection sont définis dans les fichier `source.env`, `target.env` et `docker-compose.yml` (port mapping) dans le repository permettant de déployer l'environnement de base de données.

## Configuration VSCode
Pour que VSCode puisse résoubre correctement les chemin du dossier `plugins`, ajouter dans le fichier `settings.json` :
```json
{
    [...]
    "python.envFile": "${workspaceFolder}/.env",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/plugins",
        "${workspaceFolder}"
    ]
}
```

Pour accéder à ce fichier :
- Dans le menu de VSCode : `View` > `Command Palette`
- Sélection `Open User Settings (JSON)`

