from pymongo import MongoClient
import sys

try:
    client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=5000)
    db = client['ecommerce_analytics']
    count = db['sales_metrics'].count_documents({})
    if count > 0:
        print(f"Succès : {count} documents trouvés dans MongoDB.")
        sys.exit(0)
    else:
        print("Erreur : Aucun document trouvé.")
        sys.exit(1)
except Exception as e:
    print(f"Erreur de connexion : {e}")
    sys.exit(1)