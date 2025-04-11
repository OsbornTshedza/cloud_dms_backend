from flask import Flask, request, jsonify
import pymysql
import boto3
import os
from flask_cors import CORS  # Import CORS
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# Database connection settings
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# AWS S3 Config
S3_BUCKET = "cloud-dms-bucket1"  # Replace with your actual bucket name
S3_REGION = "us-east-1"  # Change this to your bucket's actual region

# Initialize S3 client
s3 = boto3.client("s3", region_name=S3_REGION)  # Uses IAM role automatically

# ---------------------- Database Functions ----------------------

def get_db_connection():
    """Establish a new database connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------------- API Routes ----------------------

@app.route("/")
def home():
    return "Cloud DMS is running on EC2"

@app.route("/test-db")
def test_db():
    """Test database connection."""
    try:
        connection = get_db_connection()
        connection.close()
        return jsonify({"message": "Database connection successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/documents")
def get_documents():
    """Fetch documents from MySQL database."""
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
    """Upload a file to S3 and index it in RDS."""
    print("Received request to /upload")  # Debug log

    if "file" not in request.files:
        print("No file part in request")  # Debug log
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_name = file.filename
    print(f"Uploading {file_name} to S3")  # Debug log

    # Optional fields from frontend form (can be blank for now)
    subject = request.form.get("subject", "General")
    description = request.form.get("description", "")

    try:
        # Upload to S3
        s3.upload_fileobj(file, S3_BUCKET, file_name)
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        print(f"File uploaded successfully: {file_url}")  # Debug log

        # Insert metadata into RDS
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO documents (filename, subject, file_url, description)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (file_name, subject, file_url, description))
            connection.commit()
        connection.close()

        return jsonify({
            "message": "File uploaded successfully",
            "file_url": file_url
        }), 200

    except Exception as e:
        print(f"Upload or DB insert failed: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500


@app.route("/files", methods=["GET"])
def get_files():
    """Fetch list of files from S3 and generate presigned URLs."""
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        files = response.get("Contents", [])

        file_urls = []
        for file in files:
            file_name = file["Key"]
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": file_name},
                ExpiresIn=3600  # URL valid for 1 hour
            )
            file_urls.append({"name": file_name, "url": presigned_url})

        return jsonify({"files": file_urls})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/indexed-documents", methods=["GET"])
def indexed_documents():
    """Fetch metadata-indexed documents from the database with presigned S3 URLs."""
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

        # Attach presigned URL for each document
        for doc in results:
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": doc["filename"]},
                ExpiresIn=3600  # 1 hour
            )
            doc["file_url"] = presigned_url

        return jsonify({"documents": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- Run Flask ----------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Allows external access

