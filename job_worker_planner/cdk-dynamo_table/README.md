# JobWork Planner – DynamoDB Infrastructure (IaC)

## Overview
This module provisions the **core DynamoDB tables** required for the JobWork Planner application using **AWS CDK (Python)**.

The goal of this task is to:
- Ensure consistent infrastructure across environments
- Support a **multi-tenant SaaS architecture**
- Manage AWS resources using **Infrastructure as Code (IaC)**

---

## Why DynamoDB?
DynamoDB is used because:
- The application is **multi-tenant by design**
- Access patterns are key-based (tenant → users)
- It provides automatic scaling and high availability
- PAY_PER_REQUEST mode removes capacity planning overhead

---

## Tables Created

### 1. Tenant Table (`tenant`)
Stores factory / company level information.

**Primary Key**
- `tenant_id` (STRING, UUID)

**Attributes**
- `name` – tenant name
- `code` – short readable identifier (e.g. `DD-DEMO`)
- `created_at` – creation timestamp

**Design Notes**
- Acts as the root entity for multi-tenancy
- Schema follows DynamoDB best practices (minimal key definition)

---

### 2. Users Table (`users`)
Stores users belonging to a tenant.

**Primary Key**
- Partition Key: `tenant_id` (STRING)
- Sort Key: `user_id` (STRING, UUID)

**Attributes**
- `cognito_sub` – maps user to AWS Cognito
- `name`
- `email`
- `role` – OWNER / SUPERVISOR / OPERATOR
- `created_at`
- `updated_at`

**Design Notes**
- All users of a tenant are grouped using `tenant_id`
- Enables efficient queries like fetching all users of a tenant
- Supports strong tenant isolation

---

## Infrastructure Design

- **IaC Tool:** AWS CDK (Python)
- **Billing Mode:** PAY_PER_REQUEST
- **Removal Policy:** DESTROY (development only)

⚠️ In production, the removal policy will be changed to `RETAIN` to avoid data loss.

---

## Project Structure

# JobWork Planner – DynamoDB Infrastructure (IaC)

## Overview
This module provisions the **core DynamoDB tables** required for the JobWork Planner application using **AWS CDK (Python)**.

The goal of this task is to:
- Ensure consistent infrastructure across environments
- Support a **multi-tenant SaaS architecture**
- Manage AWS resources using **Infrastructure as Code (IaC)**

---

## Why DynamoDB?
DynamoDB is used because:
- The application is **multi-tenant by design**
- Access patterns are key-based (tenant → users)
- It provides automatic scaling and high availability
- PAY_PER_REQUEST mode removes capacity planning overhead

---

## Tables Created

### 1. Tenant Table (`tenant`)
Stores factory / company level information.

**Primary Key**
- `tenant_id` (STRING, UUID)

**Attributes**
- `name` – tenant name
- `code` – short readable identifier (e.g. `DD-DEMO`)
- `created_at` – creation timestamp

**Design Notes**
- Acts as the root entity for multi-tenancy
- Schema follows DynamoDB best practices (minimal key definition)

---

### 2. Users Table (`users`)
Stores users belonging to a tenant.

**Primary Key**
- Partition Key: `tenant_id` (STRING)
- Sort Key: `user_id` (STRING, UUID)

**Attributes**
- `cognito_sub` – maps user to AWS Cognito
- `name`
- `email`
- `role` – OWNER / SUPERVISOR / OPERATOR
- `created_at`
- `updated_at`

**Design Notes**
- All users of a tenant are grouped using `tenant_id`
- Enables efficient queries like fetching all users of a tenant
- Supports strong tenant isolation

---

## Infrastructure Design

- **IaC Tool:** AWS CDK (Python)
- **Billing Mode:** PAY_PER_REQUEST
- **Removal Policy:** DESTROY (development only)

⚠️ In production, the removal policy will be changed to `RETAIN` to avoid data loss.

---

## Project Structure

cdk-demo/
├── app.py # CDK app entry point
├── dynamodb_stack.py # DynamoDB table definitions
├── cdk.json
├── requirements.txt
└── README.md
---

## Deployment

### Prerequisites
- AWS CLI configured
- AWS CDK installed
- Python 3.x

### Commands
```bash
cdk bootstrap
cdk synth
cdk deploy

Multi-Tenancy Strategy

Every record is scoped by tenant_id

Application logic ensures users access only their tenant’s data

Design supports future scaling without schema changes



Status

✅ Infrastructure created using IaC
✅ Tables deployed and verified using AWS CLI
✅ Design reviewed for scalability and security

Author

Roshan Sah
Intern – JobWork Planner
2025

