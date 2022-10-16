# Lincoln test technique

## I) Python et Data Engineering

### 3 - Data Pipeline

#### Hypothèses de travail

- On suppose que la **pipeline de données va tourner tous les jours**, à une certaine heure de la journée, le matin par exemple.
- On suppose que les 4 fichiers de données vont être chargés en **mode FULL** chaque jour (et non en mode incrémental / delta).
- **Un ajustement a été effectué concernant le fichier pubmed.json.** En effet, dans l'énoncé, ce fichier contient une virgule "," à la fin. Une telle erreur ne peut provenir que d'une erreur manuelle et non automatique. Comme le chargement du fichier est supposé être automatique (1ere hypothèse), j'ai enlevé cette virgule. 

#### Outils techs utilisés et architecture

- Le code (**Python, Docker, GO, Shell**) est stocké sur un repository **Github**.
- Une fois qu'une nouvelle version du code est PUSH sur le repository, cela enclenche un trigger **Cloud Build** qui va :
    - BUILD l'image Docker
    - PUSH l'image Docker sur **Google Container Registry**
    - DEPLOY le **Cloud Run** correspondant.
- Un **appel HTTP** permet de lancer le Cloud Run et donc la pipeline data. 

#### Data Pipeline

- **GCS : 0_landing** : les différents fichiers sont déposés initialement dans un bucket Google Cloud Storage
- **BQ : 1_raw** : la data pipeline déplace les données dans une table de BigQuery, dans la zone RAW. Une étape de Data Quality est effectuée afin de ne garder que les fichiers et les lignes considérés comme valides. Des statistiques de Data Quality sont en même temps générés et écrites dans BigQuery.
- **BQ : 2_trusted** : la data pipeline croise et déplace les données dans une table de BigQuery, dans la zone Trusted
- **GCS** : finalement, la data pipeline produit en sortie un **unique fichier JSON**  correspondant à la table 2_trusted, et représentant un graphe de liaison entre les différents médicaements et leurs mentions respectives. Le fichier JSON est stocké dans Google Cloud Storage.

### 4 - Traitement ad-hoc

- Repository : https://github.com/Billylab/lincoln_test_technique_annexe
- La feature annexe est basée sur les mêmes outils que la data pipeline.
- La feature extrait depuis le json produit par la data pipeline, la liste des journaux qui mentionnent le plus de médicaments différents.

### Orchestration

- Les deux instances Cloud Run peuvent être facilement appelées et intégrées dans un orchestrateur de jobs : Airflow, Workflow, Azure Data Factory...
- En effet, sous réserve d'accès aux instances, un seul appel curl est nécessaire pour lancer les applications.

### 6 - Pour aller plus loin

- Pour traiter une plus grosse volumétrie de données (par exemple pour les fichiers pubmed et clinical trials qui contiennent un champ DATE), on pourrait par exemple paramétrer les appels CURL (impact dans le code Python, Shell, et GO), en ajoutant 2 paramètres "start_date" et "end_date" correspondant respectivement à la date de début et à la date de fin de la période de données qui est à ingérer.
- En amont, il faudrait charger les fichiers de manière incrémentale. Par exemple :
    - pubmed.2022-01-01.csv : contient les données pubmed du 2022-01-01
    - pubmed.2022-01-02.csv : contient les données pubmed du 2022-01-02
    - ...
- Ainsi, plusieurs Cloud Run pourront être instanciées pour faire de multiples appels Curl, pour ingérer différentes périodes de données et donc se répartir la charge de processing. 


## II) SQL

### Première requête
``` sql
# CAST le champ DATE en STRING car des comparaisons seront effectuées
WITH transactions_formatted AS
(
  SELECT
    PARSE_DATE('%d/%m/%Y',date) as date,
    order_id,
    client_id,
    prod_id,
    prod_price,
    prod_qty
    FROM `test01-lincoln-project.exercice_II_sql.transactions`
)

SELECT 
  date,
  SUM(prod_price*prod_qty) AS ventes
FROM `transactions_formatted`
WHERE date >= '2019-01-01' AND date <= '2019-12-31' 
GROUP BY date
ORDER BY date
```

### Seconde requête
``` sql
# CAST le champ DATE en STRING car des comparaisons seront effectuées
WITH transactions_formatted AS
(
  SELECT
    PARSE_DATE('%d/%m/%Y',date) as date_transaction,
    order_id,
    client_id,
    prod_id,
    prod_price,
    prod_qty
    FROM `test01-lincoln-project.exercice_II_sql.transactions`
),

# Filtre sur la période souhaitée
transactions_formatted_filtered AS
(
  SELECT 
    client_id,
    product_type,
    prod_price,
    prod_qty
  FROM transactions_formatted AS tf
  LEFT JOIN `test01-lincoln-project.exercice_II_sql.product-nomenclature` AS pn ON tf.prod_id=pn.product_id
  WHERE date_transaction >= "2020-01-01" AND date_transaction <= "2020-12-31"
),

# Pivot table
pivot_table AS (
  SELECT * FROM transactions_formatted_filtered
  PIVOT  
  (  
    SUM(prod_price*prod_qty)
    FOR product_type IN ("MEUBLE", "DECO")  
  ) AS PivotTable
)

SELECT 
  client_id,
  MEUBLE AS ventes_meubles,
  DECO AS ventes_deco
FROM pivot_table
 

```