---
name: tester-backend
description: Backend testing patterns, test templates, and coverage requirements for FastAPI + GraphQL applications.
type: reference
---

# Backend Testing Patterns

## Rule: GraphQL Mutations MUST Be Tested, Not Just Queries

**Status**: Active (FB29-sourced)
**Severity**: MEDIUM (untested mutation paths hide security/validation bugs)
**Applies to**: vsm_backend_tester, vsm_auditor

GraphQL test suites frequently only test introspection, queries, and the `me`
query. Mutations (create, update, delete) are left untested, allowing validation
and ownership bugs to survive to production.

**Required test templates**:

### Template 1: Create Mutation (auth + validation + success)
```python
async def test_graphql_create_article(client, writer_auth_header):
    response = await client.post(
        "/graphql",
        json={
            "query": """
            mutation CreateArticle($input: ArticleCreateInput!) {
                create_article(input: $input) { id title status }
            }
            """,
            "variables": {
                "input": {"title": "Test Article", "content": "Body text"}
            }
        },
        headers=writer_auth_header,
    )
    assert response.status_code == 200
    data = response.json()["data"]["create_article"]
    assert data["title"] == "Test Article"
    assert data["status"] == "draft"
```

### Template 2: Update Mutation (ownership enforcement)
```python
async def test_graphql_update_article_ownership(client, db, writer_user, editor_user):
    # Create article as writer
    article = Article(title="Original", author_id=writer_user.id)
    db.add(article); await db.commit()

    # Editor tries to update — should fail
    editor_token = create_access_token({"sub": str(editor_user.id), "role": "editor"})
    response = await client.post(
        "/graphql",
        json={
            "query": """
            mutation UpdateArticle($id: ID!, $input: ArticleUpdateInput!) {
                update_article(id: $id, input: $input) { id title }
            }
            """,
            "variables": {"id": str(article.id), "input": {"title": "Hacked"}}
        },
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    assert "error" in response.json() or response.json()["data"]["update_article"] is None
```

### Template 3: Delete Mutation (RBAC + ownership)
```python
async def test_graphql_delete_article_admin_can_any(client, admin_auth_header, db):
    article = Article(title="To Delete", author_id=some_writer_id)
    db.add(article); await db.commit()

    response = await client.post(
        "/graphql",
        json={
            "query": "mutation DeleteArticle($id: ID!) { delete_article(id: $id) }",
            "variables": {"id": str(article.id)}
        },
        headers=admin_auth_header,
    )
    assert response.status_code == 200
    assert response.json()["data"]["delete_article"] is True
```

### Template 4: Register Mutation (password validation)
```python
async def test_graphql_register_password_too_short(client):
    response = await client.post(
        "/graphql",
        json={
            "query": """
            mutation Register($email: String!, $password: String!, $name: String!) {
                register(email: $email, password: $password, name: $name) { id email }
            }
            """,
            "variables": {"email": "test@example.com", "password": "123", "name": "Test"}
        },
    )
    assert "error" in response.json()
    assert "8" in str(response.json()["errors"])  # Error mentions min length
```

**Prevention rules**:
1. Backend test suite MUST include at least ONE test per GraphQL mutation.
2. Tests MUST verify both success paths AND failure paths (auth, validation, ownership).
3. If a GraphQL mutation has a REST equivalent, test the GraphQL path independently.
4. Auditor MUST flag any mutation without a corresponding test as MEDIUM.

**Source**: FB29 had only 3 GraphQL tests: introspection, published articles query,
and `me` query. Zero mutation tests. GraphQL password bypass (HIGH-1) and ownership
gap (HIGH-2) were only caught by security audit, not tests.

---

## Rule: GraphQL Mutation Coverage Floor — No Stub Mutations (FB34-A2)

**Status**: Active (FB34-sourced)
**Severity**: BLOCKER (untested mutation stubs escape the Phase 4 gate)
**Applies to**: `vsm_backend_tester`, `vsm_auditor`

FB34 demonstrated that 33/33 backend tests passed while six GraphQL mutations returned `INTERNAL_ERROR`. The existing test suite did not exercise the mutation implementations, so stubs were invisible to the Phase 4 hard gate.

**Required rule**:
1. The backend test suite MUST contain at least **one test per `@strawberry.mutation`** in the schema.
2. Each mutation test MUST assert that the resolver does **NOT** return a hard-coded `INTERNAL_ERROR`, `NotImplemented`, or `None` for the success path.
3. If a mutation resolver body contains only `pass`, `raise`, or a hard-coded error payload, the test MUST fail.
4. The auditor MUST verify mutation coverage by cross-referencing `app/graphql.py` `@strawberry.mutation` decorators against test names in the test files.

**Enforcement**:
- If mutation coverage is < 100% (any mutation untested), score Phase 4 as ISSUE.
- If stub mutations pass the suite, score Phase 4 as BLOCKER — the gate is not functioning.

**Source**: FB34 backend tests 33/33 passed with 6 `INTERNAL_ERROR` stub mutations (`implementation-audit.md` lines 30, 75–82).
