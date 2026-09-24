#!/usr/bin/env python3
"""Runbook Generator — generate an ops runbook skeleton from a service name.

Usage:
  python3 runbook_generator.py payments-api
  python3 runbook_generator.py payments-api --owner platform --output docs/runbooks/payments-api.md
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path


def generate_runbook(service_name: str, owner: str = "TBD", output: str = None) -> str:
    """Generate runbook markdown content."""
    now = datetime.now().strftime("%Y-%m-%d")
    
    runbook = f"""# Runbook: {service_name}

| Field | Value |
|-------|-------|
| **Service** | {service_name} |
| **Owner** | {owner} |
| **Last Updated** | {now} |
| **On-Call Channel** | #{service_name}-oncall |

---

## 1. Service Overview

### What does this service do?
<!-- Brief description of the service's purpose and responsibilities -->

### Key Dependencies
| Dependency | Type | Impact if Down |
|------------|------|----------------|
| <!-- e.g., PostgreSQL --> | Database | <!-- e.g., Read/Write degraded --> |
| <!-- e.g., Redis --> | Cache | <!-- e.g., Increased latency --> |
| <!-- e.g., Payment Gateway --> | External API | <!-- e.g., Payments fail --> |

### Architecture
<!-- Link to architecture diagram or paste inline -->

---

## 2. Health Checks

### Standard Health Check
```bash
# HTTP health endpoint
curl -s https://{service_name}.example.com/health | jq .

# Expected: {{"status": "healthy"}}
```

### Deep Health Check
```bash
# Check database connectivity
curl -s https://{service_name}.example.com/health/deep | jq .

# Expected: {{"status": "healthy", "database": "connected", "cache": "connected"}}
```

---

## 3. Start / Stop / Restart

### Start Service
```bash
# <!-- Fill in actual start command -->
# e.g., kubectl scale deployment {service_name} --replicas=3 -n production
```

### Stop Service
```bash
# <!-- Fill in actual stop command -->
# e.g., kubectl scale deployment {service_name} --replicas=0 -n production
```

### Restart Service
```bash
# <!-- Fill in actual restart command -->
# e.g., kubectl rollout restart deployment {service_name} -n production
```

---

## 4. Common Issues & Remediation

### Issue: High Latency (>500ms P99)
**Symptoms:** Alert fires, users report slowness
**Diagnosis:**
```bash
# Check current latency
curl -s https://{service_name}.example.com/metrics | grep request_duration

# Check pod resource usage
kubectl top pods -l app={service_name}
```
**Remediation:**
1. <!-- Step 1 -->
2. <!-- Step 2 -->
3. <!-- Step 3 -->

### Issue: Memory Usage Growing
**Symptoms:** OOMKilled pods, memory alerts
**Diagnosis:**
```bash
# Check memory usage trend
kubectl top pods -l app={service_name} --sort-by=memory

# Take heap snapshot (if applicable)
# <!-- Fill in heap dump command -->
```
**Remediation:**
1. <!-- Step 1 -->
2. <!-- Step 2 -->

### Issue: Database Connection Pool Exhausted
**Symptoms:** Connection errors, timeout alerts
**Diagnosis:**
```bash
# Check active connections
# <!-- Fill in database connection check command -->
```
**Remediation:**
1. <!-- Step 1 -->
2. <!-- Step 2 -->

---

## 5. Scaling

### Horizontal Scaling
```bash
# Scale up
kubectl scale deployment {service_name} --replicas=<N> -n production

# Verify
kubectl get pods -l app={service_name} -n production
```

### Vertical Scaling
```bash
# <!-- Fill in vertical scaling command if applicable -->
```

---

## 6. Rollback Procedure

### Application Rollback
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/{service_name} -n production

# Check rollout status
kubectl rollout status deployment/{service_name} -n production
```

### Database Rollback
```bash
<!-- Fill in database rollback steps if applicable -->
```

---

## 7. Incident Response

### Severity Levels
| Level | Description | Response Time |
|-------|-------------|---------------|
| **SEV1** | Service down, data loss risk | Immediate |
| **SEV2** | Degraded performance, partial outage | < 30 min |
| **SEV3** | Minor issue, no user impact | < 4 hours |

### Escalation Path
1. **On-Call Engineer:** <!-- Name/Handle -->
2. **Tech Lead:** <!-- Name/Handle -->
3. **Engineering Manager:** <!-- Name/Handle -->

### Communication Template
```
[INCIDENT] {service_name} - [SEV?]
Impact: <!-- Description -->
Status: Investigating / Identified / Mitigating / Resolved
Updates: <!-- Link to incident channel -->
```

---

## 8. Monitoring & Alerts

### Key Metrics
| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|--------------------|
| Request Latency P99 | > 500ms | > 2000ms |
| Error Rate | > 1% | > 5% |
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 80% | > 95% |

### Alert Channels
- **PagerDuty:** <!-- Service key -->
- **Slack:** #{service_name}-alerts
- **Grafana Dashboard:** <!-- Link -->

---

## 9. Maintenance Windows

### Scheduled Maintenance
<!-- Fill in any recurring maintenance tasks -->

### Pre-Maintenance Checklist
- [ ] Notify on-call team
- [ ] Notify stakeholders
- [ ] Verify rollback procedure
- [ ] Prepare monitoring dashboard

---

## 10. Related Runbooks
<!-- Link to related service runbooks -->

---

*This runbook was generated by runbook-generator. Fill in the `<!-- -->` placeholders with service-specific information.*
"""
    return runbook


def main():
    parser = argparse.ArgumentParser(description="Generate a runbook skeleton for a service")
    parser.add_argument("service_name", help="Name of the service")
    parser.add_argument("--owner", default="TBD", help="Service owner/team")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    content = generate_runbook(args.service_name, args.owner)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Runbook written to: {output_path}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
