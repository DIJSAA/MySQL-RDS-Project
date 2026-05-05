# AWS MySQL RDS Project

I deployed a MySQL RDS instance in a private VPC subnet on AWS, configured an EC2 bastion host with least-privilege security groups to connect to it, and used Amazon Q to generate a Python script that programmatically queries the database.

---

## Architecture

```
Internet
    │
    ▼
[EC2 Bastion Host]  ← public subnet, port 22 open to my IP only
    │
    │ port 3306 (MySQL)
    ▼
[MySQL RDS Instance]  ← private subnet, no public access
```

**Key security decision:** The RDS instance has no public IP and its security group only accepts connections from the EC2 security group — not from the open internet. This is the bastion host pattern used in production environments to protect databases from direct exposure.

---

## Services Used

- **Amazon VPC** — custom VPC with public/private subnet architecture across 2 AZs
- **Amazon RDS** — managed MySQL 8.4 instance on db.t4g.micro (free tier)
- **Amazon EC2** — Amazon Linux 2023 bastion host (t2.micro)
- **Security Groups** — least-privilege inbound rules between services
- **Amazon Q** — AI-assisted Python script generation
- **Python + mysql-connector-python** — programmatic database access

---

## What It Does

1. A custom VPC (`mysql-project-vpc`, CIDR `10.0.0.0/16`) provides network isolation with 2 public and 2 private subnets
2. The RDS instance lives in the private subnets — unreachable from the internet
3. An EC2 bastion host in a public subnet acts as the only entry point
4. SSH into the EC2 instance, then connect to RDS over port 3306 from within the VPC
5. A Python script (generated with Amazon Q) connects to the database and runs queries programmatically

---

## Security Group Configuration

| Security Group | Inbound Rule | Source |
|---|---|---|
| `ec2-sg` | SSH / TCP / Port 22 | My IP only |
| `rds-sg` | MySQL / TCP / Port 3306 | `ec2-sg` only |

Port 3306 is never open to `0.0.0.0/0`.

---

## Usage

### Option A — Manual MySQL Client

```bash
# SSH into EC2
ssh -i "your-keypair.pem" ec2-user@<EC2-PUBLIC-IP>

# Install MySQL client
sudo dnf install mariadb105 -y

# Connect to RDS
mysql -h <RDS-ENDPOINT> -P 3306 -u <username> -p --ssl=0
```

```sql
SHOW DATABASES;
CREATE DATABASE testdb;
USE testdb;
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));
INSERT INTO users (name) VALUES ('AWS Project');
SELECT * FROM users;
```

### Option B — Python Script

```bash
# Install dependencies
sudo dnf install python3-pip -y
pip3 install mysql-connector-python

# Set credentials as environment variables (never hardcode)
export RDS_PASSWORD='your-password'
export RDS_DATABASE='testdb'

# Run
python3 rds_connect.py
```

Expected output:
```
Successfully connected to MySQL RDS instance
Server version: 8.4.x

=== Available Databases ===
- testdb
```

> **Note:** Run the Python script from the EC2 instance, not CloudShell. CloudShell operates outside the VPC and cannot reach the RDS endpoint.

---

## Skills Demonstrated

| Skill | How It Shows Up |
|---|---|
| VPC + Subnets | Public/private subnet architecture across 2 AZs |
| Security Groups | Least-privilege access between services |
| RDS | Managed database provisioning in a private subnet |
| EC2 | Bastion host pattern for secure database access |
| IAM | Key pair authentication for EC2 |
| Python | Programmatic database access via mysql-connector-python |
| Amazon Q | AI-assisted code generation |

---

## What I'd Add Next

- **AWS Secrets Manager** — rotate and retrieve RDS credentials programmatically instead of using environment variables
- **RDS Multi-AZ** — enable automatic failover for high availability
- **IAM database authentication** — eliminate passwords entirely, authenticate via IAM roles
- **VPC Flow Logs** — capture network traffic for auditing and troubleshooting
- **Parameter Store** — store RDS endpoint and config as SSM parameters for cleaner scripting
