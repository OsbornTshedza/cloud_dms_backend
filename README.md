# 📦 Cloud DMS Backend

This is the backend service for the **Cloud-based Document Management System (DMS)** built using Flask, AWS S3, and RDS MySQL.

---

## 🛠️ Tech Stack

- **Python 3 / Flask**
- **AWS S3** – File storage
- **RDS (MySQL)** – Metadata storage
- **Boto3** – AWS SDK
- **pymysql** – MySQL connector
- **Flask-CORS** – Cross-origin requests support

---

## 📁 Folder Structure

```
cloud-dms-backend/
├── app.py                 # Main Flask API
├── .env                  # Environment variables (ignored in git)
├── venv/                 # Virtual environment (ignored)
├── __pycache__/          # Python cache (ignored)
├── aws/                  # AWS CLI installer/resources (ignored)
└── requirements.txt      # Python dependencies (optional)
```

---

## ⚙️ Environment Setup

1. **Clone the repo:**

   ```bash
   git clone git@github.com:OsbornTshedza/cloud_dms_backend.git
   cd cloud_dms_backend
   ```

2. **Create virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up `.env` file:**

   ```env
   DB_HOST=your-db-host
   DB_USER=admin
   DB_PASSWORD=your-password
   DB_NAME=cloud_dms
   ```

---

## 🔌 API Routes

| Method | Route           | Description                            |
|--------|------------------|----------------------------------------|
| GET    | `/`              | Health check                           |
| GET    | `/test-db`       | Tests DB connection                    |
| GET    | `/files`         | Lists S3 files with presigned URLs     |
| GET    | `/documents`     | Returns indexed metadata               |
| POST   | `/upload`        | Uploads file to S3 and indexes in RDS  |

---

## 💬 Coming Soon (Phase 2 & 3)

- ✅ API Gateway + Lambda Integration  
- ✅ Advanced search & tagging (AI/ML)  
- ✅ CI/CD pipeline (GitHub Actions + Terraform)

---

## 🚀 Deployment Note (Optional)

This backend is hosted on an AWS EC2 instance (Ubuntu). If deploying to the cloud, make sure:

- ✅ The EC2 instance has an attached IAM role with permissions for **S3** and **RDS**
- ✅ The instance has **AWS CLI installed** (`aws --version`)
- ✅ The `.env` file is properly configured on the host, or use AWS Systems Manager Parameter Store for secrets management
- ✅ Port **5000** is open for external access (for Flask testing) or use **Nginx + Gunicorn** in production

---

## 👤 Author

**Osborn Tshedza**  
Cloud / DevOps Engineering Student  

## 🔗 Connect with Me & Explore More

- 📝 [Read the Blog on Medium](https://medium.com/@tshedzanethathe/building-a-cloud-native-document-management-system-on-aws-my-first-real-world-project-8a3370d3a802)
- 💼 [Connect on LinkedIn](https://www.linkedin.com/in/osborn-tshedza-nethathe-503679122/)

