import unittest
from unittest.mock import AsyncMock

from github_stats import Queries, Stats


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


class StatsTest(unittest.IsolatedAsyncioTestCase):
    async def test_total_contributions_sums_all_years(self) -> None:
        session = AsyncMock()
        stats = Stats("octocat", "test-token", session)
        stats.queries.query = AsyncMock(
            side_effect=[
                {
                    "data": {
                        "viewer": {
                            "contributionsCollection": {
                                "contributionYears": [2023, 2024]
                            }
                        }
                    }
                },
                {
                    "data": {
                        "viewer": {
                            "year2023": {
                                "contributionCalendar": {"totalContributions": 12}
                            },
                            "year2024": {
                                "contributionCalendar": {"totalContributions": 34}
                            },
                        }
                    }
                },
            ]
        )

        self.assertEqual(await stats.total_contributions, 46)
        self.assertEqual(
            stats.queries.query.await_args_list[1].args[0],
            Queries.all_contribs([2023, 2024]),
        )


if __name__ == "__main__":
    unittest.main()
