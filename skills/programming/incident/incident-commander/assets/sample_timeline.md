{
  "timeline": {
    "total_events": 21,
    "time_range": {
      "start": "2024-03-15T14:30:00+00:00",
      "end": "2024-03-15T15:40:00+00:00",
      "duration_minutes": 70
    },
    "phases": [
      {
        "name": "detection",
        "start_time": "2024-03-15T14:30:00+00:00",
        "end_time": "2024-03-15T14:30:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Initial detection of the incident through monitoring or observation"
      },
      {
        "name": "escalation",
        "start_time": "2024-03-15T14:32:00+00:00",
        "end_time": "2024-03-15T14:32:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Escalation to additional resources or higher severity response"
      },
      {
        "name": "triage",
        "start_time": "2024-03-15T14:35:00+00:00",
        "end_time": "2024-03-15T14:35:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Assessment and initial investigation of the incident"
      },
      {
        "name": "escalation",
        "start_time": "2024-03-15T14:38:00+00:00",
        "end_time": "2024-03-15T14:47:00+00:00",
        "duration_minutes": 9.0,
        "event_count": 5,
        "description": "Escalation to additional resources or higher severity response"
      },
      {
        "name": "triage",
        "start_time": "2024-03-15T14:50:00+00:00",
        "end_time": "2024-03-15T14:50:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Assessment and initial investigation of the incident"
      },
      {
        "name": "escalation",
        "start_time": "2024-03-15T14:52:00+00:00",
        "end_time": "2024-03-15T15:02:00+00:00",
        "duration_minutes": 10.0,
        "event_count": 4,
        "description": "Escalation to additional resources or higher severity response"
      },
      {
        "name": "triage",
        "start_time": "2024-03-15T15:05:00+00:00",
        "end_time": "2024-03-15T15:12:00+00:00",
        "duration_minutes": 7.0,
        "event_count": 2,
        "description": "Assessment and initial investigation of the incident"
      },
      {
        "name": "detection",
        "start_time": "2024-03-15T15:15:00+00:00",
        "end_time": "2024-03-15T15:15:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Initial detection of the incident through monitoring or observation"
      },
      {
        "name": "resolution",
        "start_time": "2024-03-15T15:18:00+00:00",
        "end_time": "2024-03-15T15:18:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Confirmation that the incident has been resolved"
      },
      {
        "name": "detection",
        "start_time": "2024-03-15T15:25:00+00:00",
        "end_time": "2024-03-15T15:25:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Initial detection of the incident through monitoring or observation"
      },
      {
        "name": "resolution",
        "start_time": "2024-03-15T15:30:00+00:00",
        "end_time": "2024-03-15T15:35:00+00:00",
        "duration_minutes": 5.0,
        "event_count": 2,
        "description": "Confirmation that the incident has been resolved"
      },
      {
        "name": "triage",
        "start_time": "2024-03-15T15:40:00+00:00",
        "end_time": "2024-03-15T15:40:00+00:00",
        "duration_minutes": 0.0,
        "event_count": 1,
        "description": "Assessment and initial investigation of the incident"
      }
    ],
    "events": [
      {
        "timestamp": "2024-03-15T14:30:00+00:00",
        "source": "datadog",
        "type": "alert",
        "message": "High error rate detected on payment-api: 45% error rate (threshold: 5%)",
        "severity": 5,
        "actor": "monitoring-system",
        "metadata": {
          "metadata": {
            "alert_id": "ALT-001",
            "metric_value": "45%",
            "threshold": "5%"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:32:00+00:00",
        "source": "pagerduty",
        "type": "escalation",
        "message": "Paged on-call engineer Sarah Chen for payment-api alerts",
        "severity": 4,
        "actor": "pagerduty-system",
        "metadata": {
          "metadata": {
            "incident_id": "PD-12345",
            "responder": "sarah.chen@company.com"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:35:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Sarah Chen acknowledged the alert and is investigating payment-api issues",
        "severity": 3,
        "actor": "sarah.chen",
        "metadata": {
          "metadata": {
            "channel": "#incidents",
            "message_id": "1234567890.123456"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:38:00+00:00",
        "source": "application_logs",
        "type": "log",
        "message": "Database connection pool exhausted: 200/200 connections active, unable to acquire new connections",
        "severity": 5,
        "actor": "payment-api",
        "metadata": {
          "metadata": {
            "log_level": "ERROR",
            "component": "database_pool",
            "connection_count": 200,
            "max_connections": 200
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:40:00+00:00",
        "source": "slack",
        "type": "escalation",
        "message": "Sarah Chen: Escalating to incident commander - database connection pool exhausted, need database team",
        "severity": 4,
        "actor": "sarah.chen",
        "metadata": {
          "metadata": {
            "channel": "#incidents",
            "escalation_reason": "database_expertise_needed"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:42:00+00:00",
        "source": "pagerduty",
        "type": "escalation",
        "message": "Incident commander Mike Rodriguez assigned to incident PD-12345",
        "severity": 4,
        "actor": "pagerduty-system",
        "metadata": {
          "metadata": {
            "incident_commander": "mike.rodriguez@company.com",
            "role": "incident_commander"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:45:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Mike Rodriguez: War room established in #war-room-payment-api. Engaging database team.",
        "severity": 4,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "channel": "#incidents",
            "war_room": "#war-room-payment-api"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:47:00+00:00",
        "source": "pagerduty",
        "type": "escalation",
        "message": "Database team engineers paged: Tom Wilson, Lisa Park",
        "severity": 3,
        "actor": "pagerduty-system",
        "metadata": {
          "metadata": {
            "team": "database-team",
            "responders": [
              "tom.wilson@company.com",
              "lisa.park@company.com"
            ]
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:50:00+00:00",
        "source": "statuspage",
        "type": "communication",
        "message": "Status page updated: Investigating payment processing issues",
        "severity": 3,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "status": "investigating",
            "affected_systems": [
              "payment-api"
            ]
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:52:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Tom Wilson: Joining war room. Looking at database metrics now. Seeing unusual query patterns from recent deployment.",
        "severity": 3,
        "actor": "tom.wilson",
        "metadata": {
          "metadata": {
            "channel": "#war-room-payment-api",
            "investigation_focus": "database_metrics"
          }
        }
      },
      {
        "timestamp": "2024-03-15T14:55:00+00:00",
        "source": "database_monitoring",
        "type": "log",
        "message": "Identified slow query introduced in deployment v2.3.1: payment validation taking 15s per request",
        "severity": 5,
        "actor": "database-monitor",
        "metadata": {
          "metadata": {
            "deployment_version": "v2.3.1",
            "query_time": "15s",
            "normal_query_time": "0.1s"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:00:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Tom Wilson: Root cause identified - inefficient query in v2.3.1 deployment. Recommending immediate rollback.",
        "severity": 4,
        "actor": "tom.wilson",
        "metadata": {
          "metadata": {
            "channel": "#war-room-payment-api",
            "root_cause": "inefficient_query",
            "recommendation": "rollback"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:02:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Mike Rodriguez: Approved rollback to v2.2.9. Sarah initiating rollback procedure.",
        "severity": 4,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "channel": "#war-room-payment-api",
            "decision": "rollback_approved",
            "target_version": "v2.2.9"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:05:00+00:00",
        "source": "deployment_system",
        "type": "action",
        "message": "Rollback initiated: payment-api v2.3.1 → v2.2.9",
        "severity": 3,
        "actor": "sarah.chen",
        "metadata": {
          "metadata": {
            "from_version": "v2.3.1",
            "to_version": "v2.2.9",
            "deployment_type": "rollback"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:12:00+00:00",
        "source": "deployment_system",
        "type": "action",
        "message": "Rollback completed successfully: payment-api now running v2.2.9 across all regions",
        "severity": 3,
        "actor": "deployment-system",
        "metadata": {
          "metadata": {
            "deployment_status": "completed",
            "regions": [
              "us-west",
              "us-east",
              "eu-west"
            ]
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:15:00+00:00",
        "source": "datadog",
        "type": "log",
        "message": "Error rate decreasing: payment-api error rate dropped to 8% and continuing to decline",
        "severity": 3,
        "actor": "monitoring-system",
        "metadata": {
          "metadata": {
            "error_rate": "8%",
            "trend": "decreasing"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:18:00+00:00",
        "source": "database_monitoring",
        "type": "log",
        "message": "Connection pool utilization normalizing: 45/200 connections active",
        "severity": 2,
        "actor": "database-monitor",
        "metadata": {
          "metadata": {
            "connection_count": 45,
            "max_connections": 200,
            "utilization": "22.5%"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:25:00+00:00",
        "source": "datadog",
        "type": "log",
        "message": "Error rate returned to normal: payment-api error rate now 0.2% (within normal range)",
        "severity": 2,
        "actor": "monitoring-system",
        "metadata": {
          "metadata": {
            "error_rate": "0.2%",
            "status": "normal"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:30:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Mike Rodriguez: All metrics returned to normal. Declaring incident resolved. Thanks to all responders.",
        "severity": 2,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "channel": "#war-room-payment-api",
            "status": "resolved"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:35:00+00:00",
        "source": "statuspage",
        "type": "communication",
        "message": "Status page updated: Payment processing issues resolved. All systems operational.",
        "severity": 2,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "status": "resolved",
            "duration": "65 minutes"
          }
        }
      },
      {
        "timestamp": "2024-03-15T15:40:00+00:00",
        "source": "slack",
        "type": "communication",
        "message": "Mike Rodriguez: PIR scheduled for tomorrow 10am. Action item: fix the inefficient query in v2.3.2",
        "severity": 2,
        "actor": "mike.rodriguez",
        "metadata": {
          "metadata": {
            "channel": "#incidents",
            "pir_time": "2024-03-16T10:00:00Z",
            "action_item": "fix_query_v2.3.2"
          }
        }
      }
    ]
  },
  "metrics": {
    "duration_metrics": {
      "total_duration_minutes": 70.0,
      "detection_duration_minutes": 0.0,
      "time_to_mitigation_minutes": 0,
      "time_to_resolution_minutes": 48.0,
      "phase_durations": {
        "detection": 0.0,
        "escalation": 10.0,
        "triage": 0.0,
        "resolution": 5.0
      }
    },
    "activity_metrics": {
      "total_events": 21,
      "events_per_hour": 18.0,
      "communication_frequency": 7.7,
      "action_frequency": 1.7,
      "unique_sources": 7,
      "unique_actors": 8
    },
    "phase_metrics": {
      "total_phases": 12,
      "phase_sequence": [
        "detection",
        "escalation",
        "triage",
        "escalation",
        "triage",
        "escalation",
        "triage",
        "detection",
        "resolution",
        "detection",
        "resolution",
        "triage"
      ],
      "longest_phase": "escalation",
      "shortest_phase": "detection"
    },
    "source_distribution": {
      "datadog": 3,
      "pagerduty": 3,
      "slack": 8,
      "application_logs": 1,
      "statuspage": 2,
      "database_monitoring": 2,
      "deployment_system": 2
    }
  },
  "gap_analysis": {
    "gaps": [],
    "warnings": [
      {
        "type": "missing_phase",
        "phase": "mitigation",
        "message": "Expected phase 'mitigation' not detected in timeline"
      }
    ],
    "gap_summary": {
      "total_gaps": 0,
      "critical_gaps": 0,
      "warning_gaps": 0,
      "missing_phases": 1
    }
  },
  "narrative": {
    "summary": "Incident Timeline Summary:\nThe incident began at 2024-03-15 14:30:00 UTC and concluded at 2024-03-15 15:40:00 UTC, lasting approximately 70 minutes.\n\nThe incident progressed through 12 distinct phases: detection, escalation, triage, escalation, triage, escalation, triage, detection, resolution, detection, resolution, triage.\n\nKey milestones:\n- Detection: 14:30 (0 min)\n- Escalation: 14:32 (0 min)\n- Triage: 14:35 (0 min)\n- Escalation: 14:38 (9 min)\n- Triage: 14:50 (0 min)\n- Escalation: 14:52 (10 min)\n- Triage: 15:05 (7 min)\n- Detection: 15:15 (0 min)\n- Resolution: 15:18 (0 min)\n- Detection: 15:25 (0 min)\n- Resolution: 15:30 (5 min)\n- Triage: 15:40 (0 min)",
    "phase_narratives": [
      {
        "phase": "detection",
        "start_time": "2024-03-15T14:30:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "The incident was first detected when High error rate detected on payment-api: 45% error rate (threshold: 5%). This phase lasted 0 minutes with 1 total events.",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "escalation",
        "start_time": "2024-03-15T14:32:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "During the escalation phase (0 minutes), key activities included: Paged on-call engineer Sarah Chen for payment-api alerts",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "triage",
        "start_time": "2024-03-15T14:35:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "Initial investigation began with Sarah Chen acknowledged the alert and is investigating payment-api issues. The team focused on Sarah Chen acknowledged the alert and is investigating payment-api issues",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "escalation",
        "start_time": "2024-03-15T14:38:00+00:00",
        "duration_minutes": 9.0,
        "narrative": "During the escalation phase (9 minutes), key activities included: Database connection pool exhausted: 200/200 connections active, unable to acquire new connections",
        "key_events": 4,
        "total_events": 5
      },
      {
        "phase": "triage",
        "start_time": "2024-03-15T14:50:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "Initial investigation began with Status page updated: Investigating payment processing issues. The team focused on Status page updated: Investigating payment processing issues",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "escalation",
        "start_time": "2024-03-15T14:52:00+00:00",
        "duration_minutes": 10.0,
        "narrative": "During the escalation phase (10 minutes), key activities included: Tom Wilson: Joining war room. Looking at database metrics now. Seeing unusual query patterns from recent deployment.",
        "key_events": 4,
        "total_events": 4
      },
      {
        "phase": "triage",
        "start_time": "2024-03-15T15:05:00+00:00",
        "duration_minutes": 7.0,
        "narrative": "Initial investigation began with Rollback initiated: payment-api v2.3.1 → v2.2.9. The team performed various diagnostic activities",
        "key_events": 2,
        "total_events": 2
      },
      {
        "phase": "detection",
        "start_time": "2024-03-15T15:15:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "The incident was first detected when Error rate decreasing: payment-api error rate dropped to 8% and continuing to decline. This phase lasted 0 minutes with 1 total events.",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "resolution",
        "start_time": "2024-03-15T15:18:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "During the resolution phase (0 minutes), key activities included: Connection pool utilization normalizing: 45/200 connections active",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "detection",
        "start_time": "2024-03-15T15:25:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "The incident was first detected when Error rate returned to normal: payment-api error rate now 0.2% (within normal range). This phase lasted 0 minutes with 1 total events.",
        "key_events": 1,
        "total_events": 1
      },
      {
        "phase": "resolution",
        "start_time": "2024-03-15T15:30:00+00:00",
        "duration_minutes": 5.0,
        "narrative": "During the resolution phase (5 minutes), key activities included: Mike Rodriguez: All metrics returned to normal. Declaring incident resolved. Thanks to all responders.",
        "key_events": 2,
        "total_events": 2
      },
      {
        "phase": "triage",
        "start_time": "2024-03-15T15:40:00+00:00",
        "duration_minutes": 0.0,
        "narrative": "Initial investigation began with Mike Rodriguez: PIR scheduled for tomorrow 10am. Action item: fix the inefficient query in v2.3.2. The team performed various diagnostic activities",
        "key_events": 1,
        "total_events": 1
      }
    ],
    "timeline_type": "standard_escalation",
    "complexity_score": 7.633333333333333
  },
  "summary": {
    "incident_overview": {
      "start_time": "2024-03-15T14:30:00+00:00",
      "end_time": "2024-03-15T15:40:00+00:00",
      "total_duration_minutes": 70.0,
      "total_events": 21,
      "phases_detected": 12
    },
    "phase_analysis": {
      "detection": {
        "duration_minutes": 0.0,
        "event_count": 1,
        "start_time": "2024-03-15T15:25:00+00:00",
        "end_time": "2024-03-15T15:25:00+00:00"
      },
      "escalation": {
        "duration_minutes": 10.0,
        "event_count": 4,
        "start_time": "2024-03-15T14:52:00+00:00",
        "end_time": "2024-03-15T15:02:00+00:00"
      },
      "triage": {
        "duration_minutes": 0.0,
        "event_count": 1,
        "start_time": "2024-03-15T15:40:00+00:00",
        "end_time": "2024-03-15T15:40:00+00:00"
      },
      "resolution": {
        "duration_minutes": 5.0,
        "event_count": 2,
        "start_time": "2024-03-15T15:30:00+00:00",
        "end_time": "2024-03-15T15:35:00+00:00"
      }
    },
    "key_participants": {
      "monitoring-system": 3,
      "pagerduty-system": 3,
      "sarah.chen": 3,
      "payment-api": 1,
      "mike.rodriguez": 6,
      "tom.wilson": 2,
      "database-monitor": 2,
      "deployment-system": 1
    },
    "event_sources": {
      "datadog": 1,
      "pagerduty": 1,
      "slack": 1,
      "application_logs": 1,
      "statuspage": 1,
      "database_monitoring": 1,
      "deployment_system": 1
    },
    "complexity_indicators": {
      "unique_sources": 7,
      "unique_actors": 8,
      "high_severity_events": 9,
      "phase_transitions": 11
    }
  },
  "reconstruction_timestamp": "2026-09-22T03:01:10.922600+00:00"
}
