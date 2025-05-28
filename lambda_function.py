from flask import Flask, redirect, url_for, session, request, jsonify
import pymysql
import boto3
import os
from flask_cors import CORS
from dotenv import load_dotenv
import awsgi2
from botocore.config import Config
import base64

# ---------------- Flask App Setup ----------------
app = Flask(__name__)
CORS(app)
load_dotenv()

# ---------------- Config ----------------
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")

# ---------------- Clients ----------------
s3_config = Config(connect_timeout=5, read_timeout=10)
s3 = boto3.client("s3", region_name=S3_REGION, config=s3_config, endpoint_url="https://s3.us-east-1.amazonaws.com")

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ---------------- Health & Core Routes ----------------

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Cloud DMS Backend API"})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "2.0.0"})

@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()
        connection.close()
        return jsonify({"message": "Database connection successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/documents")
def get_documents():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM documents")
            documents = cursor.fetchall()
        connection.close()
        return jsonify(documents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_name = file.filename
    subject = request.form.get("subject", "General")
    description = request.form.get("description", "")

    print(f"🟡 Uploading: {file_name} | Subject: {subject}")

    try:
        s3.upload_fileobj(file, S3_BUCKET, file_name)
        print("✅ Uploaded to S3")
    except Exception as s3err:
        print(f"❌ S3 upload failed: {str(s3err)}")
        return jsonify({"error": "S3 upload failed", "details": str(s3err)}), 500

    try:
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO documents (filename, subject, file_url, description)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (file_name, subject, file_url, description))
            connection.commit()
        connection.close()

        print("✅ Metadata saved to RDS")
        return jsonify({"message": "File uploaded successfully", "file_url": file_url}), 200
    except Exception as db_err:
        print(f"❌ RDS insert failed: {str(db_err)}")
        return jsonify({"error": "DB insert failed", "details": str(db_err)}), 500

@app.route("/files", methods=["GET"])
def get_files():
    print("📦 /files route hit — attempting to list S3 contents...")
    try:
        print(f"S3 Client Region: {S3_REGION}") # Log the region (using the global variable)
        print(f"S3 Client Config: {s3._client_config}") # Log the client config (using the global client)

        print("⏳ Calling s3.list_objects_v2...") # Log before the call
        response = s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=100)
        print("✅ s3.list_objects_v2 call completed.") # Log after the call

        files = response.get("Contents", [])
        if not files:
            print("⚠️ No files found in bucket")
            return jsonify({"files": []})

        file_urls = []
        for file in files:
            file_name = file["Key"]
            print(f"🔗 Generating presigned URL for: {file_name}")
            try:
                presigned_url = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": file_name},
                    ExpiresIn=3600
                )
                file_urls.append({"name": file_name, "url": presigned_url})
            except Exception as url_err:
                print(f"⚠️ Failed to generate URL for {file_name}: {url_err}")

        print("✅ Presigned URLs generation complete")
        return jsonify({"files": file_urls})

    except Exception as e:
        print(f"❌ /files route failed: {str(e)}")
        return jsonify({"error": "Failed to retrieve files", "details": str(e)}), 500

@app.route("/indexed-documents", methods=["GET"])
def indexed_documents():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, subject, upload_date, file_url, description
                FROM documents
                ORDER BY upload_date DESC
                LIMIT 50
            """)
            results = cursor.fetchall()
        connection.close()

        for doc in results:
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": doc["filename"]},
                ExpiresIn=3600
            )
            doc["file_url"] = presigned_url

        return jsonify({"documents": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/documents/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT filename FROM documents WHERE id = %s", (doc_id,))
            result = cursor.fetchone()

        if not result:
            print(f"⚠️ Document ID {doc_id} not found in DB.")
            return jsonify({"error": "Document not found"}), 404

        filename = result["filename"]
        print(f"🗑️ Deleting document ID: {doc_id} | File: {filename}")

        try:
            s3.delete_object(Bucket=S3_BUCKET, Key=filename)
            print(f"✅ S3 object deleted: {filename}")
        except Exception as s3_err:
            print(f"⚠️ S3 deletion failed: {s3_err}")

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            connection.commit()
        connection.close()

        return jsonify({"message": f"Document '{filename}' deleted successfully"}), 200

    except Exception as e:
        print(f"❌ Delete error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ---------------- Lambda Entry Point ----------------
def lambda_handler(event, context):
    print("🔍 Lambda handler invoked!")
    print("Event:", event)

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": ""
        }

    if 'http' in event.get('requestContext', {}):
        event['httpMethod'] = event['requestContext']['http']['method']
        event['path'] = event['requestContext']['http']['path']

        if 'queryStringParameters' not in event:
            query_params = event.get('rawQueryString', '')
            parsed_query = {}
            if query_params:
                for item in query_params.split('&'):
                    if '=' in item:
                        key, value = item.split('=', 1)
                        parsed_query[key] = value
            event['queryStringParameters'] = parsed_query

    return awsgi2.response(app, event, context, base64_content_types={"image/png", "application/pdf"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
