# 方言差异与 ORM 模式速查

> 本文件由 SKILL.md 正文外移而来（progressive disclosure）：正文只留导航与工作流，
> 长篇幅的参考型知识按需读取。

## 多数据库支持

### 方言差异

| 特性 | PostgreSQL | MySQL | SQLite | SQL Server |
|------|-----------|-------|--------|------------|
| UPSERT | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT DO UPDATE` | `MERGE` |
| 布尔 | 原生 `BOOLEAN` | `TINYINT(1)` | `INTEGER` | `BIT` |
| 自增 | `SERIAL` / `GENERATED` | `AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | `IDENTITY` |
| JSON | `JSONB`（可索引） | `JSON` | 文本（扩展） | `NVARCHAR(MAX)` |
| 数组 | 原生 `ARRAY` | 不支持 | 不支持 | 不支持 |
| CTE（递归） | 完整支持 | 8.0+ | 3.8.3+ | 完整支持 |
| 窗口函数 | 完整支持 | 8.0+ | 3.25.0+ | 完整支持 |
| 全文检索 | `tsvector` + GIN | `FULLTEXT` 索引 | FTS5 扩展 | 全文目录 |
| LIMIT/OFFSET | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |

### 兼容性要点

- **始终用参数化查询** — 所有方言下防 SQL 注入
- **共享代码避免方言专属函数** — 用适配层封装
- **在目标引擎上测迁移** — `information_schema` 各引擎不同
- **用 ISO 日期格式** — `'YYYY-MM-DD'` 到处可用
- **给标识符加引号** — 双引号（SQL 标准）或反引号（MySQL）

## ORM 模式

### Prisma

**Schema 定义**

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

**迁移**：`npx prisma migrate dev --name add_user_email`

**查询 API**：`prisma.user.findMany({ where: { email: { contains: '@' } }, include: { posts: true } })`

**原生 SQL 逃生通道**：`prisma.$queryRaw\`SELECT * FROM users WHERE id = ${userId}\``

### Drizzle

**Schema 优先定义**

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});
```

**查询构造器**：`db.select().from(users).where(eq(users.email, email))`

**迁移**：`npx drizzle-kit generate:pg` 后接 `npx drizzle-kit push:pg`

### TypeORM

**实体装饰器**

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

**Repository 模式**：`userRepo.find({ where: { email }, relations: ['posts'] })`

**迁移**：`npx typeorm migration:generate -n AddUserEmail`

### SQLAlchemy

**声明式模型**

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    posts = relationship('Post', back_populates='author')
```

**Session 管理**：始终用 `with Session() as session:` 上下文管理器

**Alembic 迁移**：`alembic revision --autogenerate -m "add user email"`

> 各 ORM 并排对比与迁移工作流见 references/orm_patterns.md。
