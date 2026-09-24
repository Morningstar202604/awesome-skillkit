# Dialect Differences and ORM Patterns Quick Reference

> This file was moved out of the SKILL.md body (progressive disclosure): the body keeps only navigation and workflow,
> and the long-form reference knowledge is read on demand.

## Multi-database support

### Dialect differences

| Feature | PostgreSQL | MySQL | SQLite | SQL Server |
|------|-----------|-------|--------|------------|
| UPSERT | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT DO UPDATE` | `MERGE` |
| Boolean | Native `BOOLEAN` | `TINYINT(1)` | `INTEGER` | `BIT` |
| Auto-increment | `SERIAL` / `GENERATED` | `AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | `IDENTITY` |
| JSON | `JSONB` (indexable) | `JSON` | text (extension) | `NVARCHAR(MAX)` |
| Array | Native `ARRAY` | Unsupported | Unsupported | Unsupported |
| Recursive CTE | Full support | 8.0+ | 3.8.3+ | Full support |
| Window functions | Full support | 8.0+ | 3.25.0+ | Full support |
| Full-text search | `tsvector` + GIN | `FULLTEXT` index | FTS5 extension | Full-text catalog |
| LIMIT/OFFSET | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |

### Compatibility notes

- **Always use parameterized queries** — prevents SQL injection under all dialects
- **Avoid dialect-specific functions in shared code** — wrap them in an adapter layer
- **Test migrations on the target engine** — `information_schema` differs across engines
- **Use ISO date formats** — `'YYYY-MM-DD'` works everywhere
- **Quote identifiers** — double quotes (SQL standard) or backticks (MySQL)

## ORM patterns

### Prisma

**Schema definition**

```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  author   User   @relation(fields: [authorId], references: [id])
  authorId Int
}
```

**Migration**: `npx prisma migrate dev --name add_user_email`

**Query API**: `prisma.user.findMany({ where: { email: { contains: '@' } }, include: { posts: true } })`

**Raw SQL escape hatch**: `prisma.$queryRaw\`SELECT * FROM users WHERE id = ${userId}\``

### Drizzle

**Schema-first definition**

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});
```

**Query builder**: `db.select().from(users).where(eq(users.email, email))`

**Migration**: `npx drizzle-kit generate:pg` followed by `npx drizzle-kit push:pg`

### TypeORM

**Entity decorators**

```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @OneToMany(() => Post, post => post.author)
  posts: Post[];
}
```

**Repository pattern**: `userRepo.find({ where: { email }, relations: ['posts'] })`

**Migration**: `npx typeorm migration:generate -n AddUserEmail`

### SQLAlchemy

**Declarative model**

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    posts = relationship('Post', back_populates='author')
```

**Session management**: always use the `with Session() as session:` context manager

**Alembic migration**: `alembic revision --autogenerate -m "add user email"`

> For a side-by-side comparison of the ORMs and migration workflows, see references/orm_patterns.md.
