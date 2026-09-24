# Solution Templates

## implement.feature
1. Confirm the requirement: feature boundaries, user stories, success criteria
2. Design the data model: table schema / type definitions
3. Implement the core logic: split by module and implement one by one
4. Write tests: unit tests covering the core logic
5. Integration verification: end-to-end tests confirm the feature is complete

## implement.api
1. Define the API contract: routes, request/response format, error codes
2. Implement the data access layer: DAO/Repository
3. Implement the business logic layer: Service
4. Implement the controller layer: HTTP handler
5. Write API tests: swagger/openapi validation + unit tests

## fix.runtime
1. Reproduce: write a minimal repro script
2. Locate: analyze the stack trace, logs, and related code
3. Plan: draft a fix, assess the impact scope
4. Fix: implement the fix, following the minimal-change principle
5. Verify: regression tests + smoke tests on related modules
6. Prevent: add a regression test case

## fix.security
1. Assess: confirm the vulnerability type and impact scope
2. Fix: fix per OWASP recommendations
3. Scan: run a security scan to verify the fix
4. Dependencies: check and upgrade affected dependencies
5. Documentation: record the vulnerability and the fix

## refactor
1. Analyze: scan dependencies and impact scope
2. Protect: write tests for the current behavior
3. Plan: draft a small-step refactoring plan
4. Execute: refactor step by step per the plan
5. Verify: run the full test suite to confirm no regression

## test.coverage
1. Analyze: generate the current coverage report
2. Identify: find uncovered code paths
3. Supplement: prioritize tests for core logic
4. Verify: run tests to confirm coverage improved
5. Lock in: add the coverage requirement to CI

## optimize
1. Baseline: establish a performance baseline (response time/QPS/memory)
2. Profile: locate the bottleneck (CPU/IO/memory)
3. Plan: draft an optimization strategy
4. Implement: optimize step by step, verifying each step
5. Regression: confirm the optimization introduces no new problems

## design
1. Requirement clarification: confirm feature boundaries and constraints
2. Draft options: list 2-3 viable approaches
3. Selection rationale: compare the pros and cons of each
4. Architecture sketch: draw the component relationship diagram
5. Review: confirm the approach with stakeholders

## migrate
1. Compatibility analysis: identify breaking changes
2. Plan: draft the migration steps and rollback plan
3. Pilot: validate on a small scale
4. Full rollout: execute per the plan
5. Verify: full testing confirms normal operation

## destructive
1. Risk assessment: confirm the impact scope
2. Backup: back up relevant data/config
3. Confirm: clearly explain the risk to the user
4. Execute: perform the deletion
5. Verify: confirm the impact matches expectations
