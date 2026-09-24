# Code Pattern Cheat Sheet

## Python FastAPI CRUD

### When to use
- Implementing a new resource module (users, orders, products, etc.)
- Standard RESTful API + data model + service layer

### File structure
```
src/{target}/
├── models.py    # Pydantic models (Create/Update/Base)
├── service.py   # business logic (CRUD operations)
└── api.py       # FastAPI routes (REST endpoints)
```

### Field inference rules
| scope keyword | Inferred fields |
|-------------|---------|
| auth/login | username, password_hash, email |
| user | username, email, name |
| order | user_id, total, status, items |
| product | name, price, description, stock |
| comment | content, user_id, post_id |

---

## TypeScript Express CRUD

### When to use
- Node.js/Express REST API
- TypeScript project

### File structure
```
src/{target}/
├── {target}.router.ts    # route definitions
├── {target}.service.ts   # service layer
├── {target}.model.ts     # type definitions
└── {target}.dto.ts       # data transfer objects
```

---

## Go Gin CRUD

### When to use
- Go + Gin framework
- High-performance API service

### File structure
```
internal/{target}/
├── model.go      # data structures
├── handler.go    # HTTP handlers
├── service.go    # business logic
└── repository.go # data access
```

---

## Bug Fix pattern

### When to use
- Fixing runtime errors (crash, panic, exception)
- Need to annotate the root cause and fix notes

### File conventions
1. Add a comment block at the fix point explaining:
   - Root cause
   - Before (the pre-fix state)
   - After (the post-fix state)
2. Add a guard clause to prevent recurrence
3. Add logging for the exception scenario

---

## Test stub generation rules

### Coverage scenarios
1. **Happy path** — the normal flow
2. **Edge case** — boundary conditions
3. **Error handling** — error handling

### Naming conventions
- Test class: `Test{ClassName}`
- Test method: `test_{method_name}_{scenario}`

### Assertion conventions
- Use `assert` rather than `assertTrue`
- Specify the expected value explicitly
- Error messages include context
