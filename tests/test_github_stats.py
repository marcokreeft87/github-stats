import unittest
from unittest.mock import AsyncMock

from github_stats import Queries


class QueriesTest(unittest.IsolatedAsyncioTestCase):
    async def test_graphql_query_uses_access_token(self) -> None:
        response = AsyncMock()
        response.json.return_value = {"data": {"viewer": {}}}
        session = AsyncMock()
        session.post.return_value = response

        queries = Queries("octocat", "test-token", session)

        result = await queries.query("query { viewer { login } }")

        self.assertEqual(result, {"data": {"viewer": {}}})
        session.post.assert_awaited_once_with(
            "https://api.github.com/graphql",
            headers={"Authorization": "bearer test-token"},
            json={"query": "query { viewer { login } }"},
        )


if __name__ == "__main__":
    unittest.main()
