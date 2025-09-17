Docker & AWS Targets

Docker (mandatory)
	•	Dockerfile (non-root user, multi-stage build).
	•	docker-compose.yml: api, db, optional pgadmin; healthchecks.
	•	Makefile: up, down, migrate, seed, test.

AWS (two blessed paths)
	•	ECS Fargate + ALB for always-warm, low-latency containers. Logs to CloudWatch.  ￼
	•	API Gateway + Lambda (via Mangum) + RDS Proxy for spiky loads; Aurora PostgreSQL Serverless v2 for DB.  ￼

Data & Secrets
	•	Aurora PostgreSQL Serverless v2 (auto-scaling) + RDS Proxy (connection pooling).
	•	Secrets Manager for DB creds and signing salts.  ￼

Edge
	•	Rate limiting/WAF at API Gateway or ALB; private subnets for DB.

