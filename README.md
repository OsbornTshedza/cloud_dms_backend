# 📦 FutureEd Cloud DMS – Backend (Phase 2)

This is the backend engine for the **FutureEd Hub, Cloud Document Management System**, built using Flask and deployed as a container to **AWS Lambda** via **ECR**, behind a RESTful **API Gateway**.

It powers secure document uploads, metadata indexing via RDS, and exposes API endpoints consumed by the frontend. Built with FinOps, observability, and DevOps culture in mind.

---

## 🔧 Tech Stack & AWS Services Used

- **Flask** + `awsgi2` (for Lambda routing)
- **AWS Lambda** (containerized backend)
- **API Gateway (REST API)** (public endpoint)
- **Amazon S3** (private doc storage)
- **Amazon RDS (MySQL)** (indexed metadata)
- **Amazon ECR** (container registry)
- **GitHub Actions** (CI/CD pipelines)
- **Slack + SNS + CloudWatch** (alerts + logs)

---

## 📂 Folder Structure

cloud-dms-backend/

├── .github/workflows/        # CI/CD pipeline (deploy.yml)

├── lambda_function.py        # Flask + awsgi Lambda handler

├── requirements.txt          # Python dependencies

├── Dockerfile                # Lambda container definition

├── .gitignore, .dockerignore

└── README.md

---

## ⚙️ Setup Instructions (Local Testing)

> Note: Backend is designed for containerized deployment via Lambda, not local Flask dev.
> 

### 📥 1. Clone the Repo

```bash
git clone <https://github.com/your-username/cloud_dms_backend.git>
cd cloud_dms_backend

```

### 📦 2. Build Docker Container (optional)

docker build -t cloud-dms-backend .

### ⚙️ 3. Environment Variables (for Lambda)

Add to Lambda > Configuration > Environment Variables:

- `RDS_HOST`
- `RDS_USER`
- `RDS_PASSWORD`
- `RDS_DB_NAME`
- `S3_BUCKET_NAME`

---

## 🔐 GitHub Secrets Used (CI/CD)

| Secret Key | Used For |
| --- | --- |
| `AWS_ACCESS_KEY_ID` | GitHub Actions IAM user |
| `AWS_SECRET_ACCESS_KEY` | IAM user credentials |
| `AWS_REGION` | AWS region |
| `ECR_REPOSITORY` | For backend container push |
| `LAMBDA_FUNCTION_NAME` | To update Lambda via Actions |

---

## 🚀 Deployment Process (CI/CD Flow)

> Automated via GitHub Actions (.github/workflows/deploy.yml)
> 

### 🔄 Pipeline Summary:

1. Authenticate to AWS
2. Build & tag Docker image
3. Push image to ECR
4. Update Lambda function
5. Notify via Slack on success/failure

---

## 🧪 API Routes

| Route | Method | Description |
| --- | --- | --- |
| `/files` | `GET` | Lists files from S3 with presigned URLs |
| `/upload` | `POST` | Uploads a new file and stores metadata |
| `/documents` | `GET` | Fetches document metadata from RDS |
| `/test-db` | `GET` | Tests DB connectivity |
| `/` | `GET` | Basic health check |

---

## 🧭 Monitoring & Alerts

- **CloudWatch Logs**: all Lambda logs
- **Metric Filters**: scans for `"ERROR"` or `"Task timed out"`
- **CloudWatch Alarms**: triggers SNS topic
- **SNS Topic**: notifies via email 
- **Slack Notifications**: real-time updates for CICD deployment success/failure

---

## 🔒 Security Summary

- **IAM Roles**: scoped per function (S3, RDS, Lambda)
- **S3 Bucket Policy**: trust-based access via `aws:SourceArn`
- **Lambda inside VPC**: for secure RDS access
- **RDS Security Group**: inbound only from Lambda SG
- **No secrets in code**: all handled via GitHub Secrets + Lambda env vars

---

## ✅ Phase 2 Takeaways

- Reduced idle costs by replacing EC2 with containerized Lambda
- Improved developer workflow with GitHub Actions CI/CD
- Enabled observability with CloudWatch + Slack alerts
- Designed a scalable, modular backend foundation
- Built with Well-Architected + Cloud Adoption Frameworks in mind

---

## 🔮 What’s Next (Phase 3)

- 🔍 OpenSearch + AI-powered document indexing
- 🧠 SageMaker / Bedrock for document classification
- 🧱 API Gateway JWT authorizers
- 🛡️ WAF, CloudTrail, S3 access logs for compliance

---

## **👤 Author**

### **Osborn Tshedza**

Cloud / DevOps Engineer In Training.

## 🔗 Connect with Me & Lets Collaborate

- 📝 [Read the Blog on Medium]
- 💼 [Connect on LinkedIn](https://www.linkedin.com/in/osborn-tshedza-nethathe-503679122/)

📜 License
MIT License – see LICENSE file.
