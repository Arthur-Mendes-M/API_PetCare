import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

bucket = 'PetCare_Files'
bucket_employees = 'Employees'
bucket_products = 'Products'

# supabase.storage.create_bucket('employeesphoto', options={"public": True})

def supabase_operation(operation):
    try:
        return operation.execute().data
    except Exception as e:
        return {"error": str(e)}