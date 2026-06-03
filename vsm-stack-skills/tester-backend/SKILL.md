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
