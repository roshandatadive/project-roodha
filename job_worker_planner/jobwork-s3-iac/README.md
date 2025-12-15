JobWork Planner – Secure S3 Storage (Infrastructure as Code)

Overview
This module provisions a secure, private Amazon S3 bucket using AWS CDK (Python) for the JobWork Planner SaaS application.

The bucket is used only for application data such as Purchase Orders (POs), part drawings, and CSV exports.
The infrastructure is created using Infrastructure as Code (IaC) to ensure consistency, security, and production readiness across environments.

Why Amazon S3
Amazon S3 was chosen because it provides highly durable and scalable object storage, strong security controls using IAM, native support for browser uploads via pre-signed URLs, and lifecycle policies for cost optimization.
This makes S3 suitable for a multi-tenant SaaS application.

Security Model
The S3 bucket is completely private.
All public access is blocked using AWS public access block settings.
Server-side encryption (AES-256) is enabled.
HTTPS is enforced for all requests.

As a result, no file is publicly accessible and only the application can access the bucket.

Access Control Using IAM Roles
The application accesses S3 using IAM roles only, without access keys.
Two roles are created:

Lambda role for backend APIs

EC2 role for application servers

Each role follows the principle of least privilege and is allowed to list the bucket and get, put, or delete objects.

Multi-Tenant Object Structure
All files follow this object key structure:

tenant_id/module/yyyy/mm/dd/filename

Example:
T001/uploads/2025/12/10/po_1234.pdf

This structure ensures tenant isolation, easy filtering, and scalability.

Browser Uploads Using Pre-Signed URLs
The bucket supports browser uploads using pre-signed PUT URLs.
CORS is configured to allow PUT, GET, and HEAD methods.

Upload flow:

Backend generates a pre-signed URL

Browser uploads the file directly to S3

Backend never handles raw file data

Versioning and Lifecycle Management
Bucket versioning is enabled to protect against accidental deletion or overwrite.
Lifecycle rules are configured to transition objects to cheaper storage after 30 days and optionally expire them after 365 days.

What This Stack Creates

A private S3 bucket for application files

IAM roles for EC2 and Lambda access

CORS configuration for browser uploads

Encryption at rest

Versioning enabled

Lifecycle rules for cost optimization

CloudFormation outputs for integration

Project Structure
jobwork-s3-iac

app.py

s3_bucket_stack.py

presign_upload_test.py

cdk.json

requirements.txt

README.md

Deployment Steps

Install dependencies using pip install -r requirements.txt

Bootstrap CDK using cdk bootstrap aws://account-id/region

Deploy the stack using cdk deploy S3BucketStack

Validation Performed
After deployment, the following were verified:

Bucket exists in the correct region

Public access is fully blocked

Encryption is enabled

Versioning is enabled

CORS rules are applied

IAM roles have correct permissions

Pre-signed URL upload works successfully

How This Fits into JobWork Planner
This bucket acts as the central storage layer for the application.
It integrates with EC2 and Lambda backends and is designed for secure, multi-tenant SaaS usage in production.

Author
Roshan Sah
Intern – Cloud / Data Engineering
JobWork Planner Project
