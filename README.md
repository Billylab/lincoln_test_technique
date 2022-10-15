# lincoln_test_technique


- Création d'un service account avec les droits nécessaires pour lire et écrire dans un Google Cloud Storage / BigQuery


Fichier pubmed.json : 
- Ajustement manuel car on suppose qu'une telle erreur provient d'une manipulation humaine et non automatique
- Si automatique, cela ne doit pas se produire : , à la fin
- Ajustement : j'ai enlevé la virgule à la fin

Bucket dans GCS :
- GCS : 0_landing : hypothèse : chargement en mode FULL tous les jours : tous le reste de la pipeline en mode OVERWRITE / TRUCATE
- BQ : 1_raw :  copie de la landing vers la raw des fichiers valides + données de data quality
- BQ : 2_trusted : nettoyage et enrichissement de la couche raw
- BQ : 3_refined : pour les use case

