# Benchmark Tasks

This directory contains the 25 benchmark task schemas used by SecDown.

The task set corresponds to the paper's risk-tiered taxonomy:

| Directory | Paper category | Purpose |
| --- | --- | --- |
| `type_a/` | Type A: Public Data Retrieval | Unauthenticated public web/API requests. |
| `type_b/` | Type B: Credential-Bearing Requests | Requests that carry API keys or bearer tokens from environment variables. |
| `type_c/` | Type C: State and Control Mutation | Mocked state-changing operations such as SRE, telemetry, IoT, and CI/CD actions. |
| `type_d/` | Type D: Dependency Fetching | Remote code, package, model, and asset retrieval tasks. |

Each task is a JSON schema with:

- `task_id`: stable task identifier,
- `threat_category`: paper-level task category,
- `business_context`: high-level scenario,
- `source`: target service or endpoint family,
- `nl_goal`: neutral user-facing task prompt,
- `network_requirements`: HTTP method, URL, parameters, headers, and payload,
- `paradigm_3_config`: skill-agent metadata used to instantiate tool-augmented tasks.

The schemas are designed to be adapted into the three execution paradigms described in the paper: HITL Agent, Code Agent, and Skill Agent.

## Anonymization

Task files should not contain author names, affiliations, emails, personal GitHub usernames, private repository names, local filesystem paths, or real credentials.

Use neutral placeholders such as `example-org`, `private-research-artifact`, `<ENV:API_KEY>`, and `[REDACTED]` for any sensitive or identifying content.
