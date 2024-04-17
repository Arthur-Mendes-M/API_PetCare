import os
from flask import jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

bucket_petcare = 'PetCare_Files'
bucket_employees = 'Employees'
bucket_products = 'Products'

# supabase.storage.create_bucket(bucket_employees, options={"public": True})
# supabase.storage.create_bucket(bucket_products, options={"public": True})

def supabase_operation(operation):
    try:
        return jsonify(operation.execute().data)
    except Exception as e:        
        return jsonify({ "error": str(e.details)})