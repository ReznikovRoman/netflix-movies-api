import pytest
import requests

from movies.common.constants import DefaultRoles

from ..base import BaseClientTest, CacheTestMixin, CacheWithParamsTestMixin, PaginationTestMixin

pytestmark = [pytest.mark.asyncio]


class TestFilmList(
    CacheWithParamsTestMixin,
    CacheTestMixin,
    PaginationTestMixin,
    BaseClientTest,
):
    """Tests for retrieving a list of movies."""

    endpoint = "/api/v1/films/"

    pagination_factory_name = "films_es"

    cache_field_name = "title"
    cache_es_index_name = "movies"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"

    cache_es_query = {"query": {"match_all": {}}}
    cache_es_params = {"sort": "imdb_rating:desc"}
    cache_es_list_fixture_name = "films_es"
    cache_dto_list_fixture_name = "films_dto"
    cache_with_params_request = {"sort": "-imdb_rating"}

    async def test_film_list_ok(self, films_es, films_dto):
        """Retrieving list of films works correctly."""
        fields_to_check = ("uuid", "title")

        got = await self.client.get("/api/v1/films")

        assert len(got) == len(films_dto)
        for field_to_check in fields_to_check:
            actual = set([film_data[field_to_check] for film_data in got])
            expected = set([(str(getattr(film, field_to_check))) for film in films_dto])
            assert actual == expected

    async def test_film_list_with_params(self, elastic, films_es, film_dto):
        """The list of films is returned correctly even with additional query parameters in the request."""
        genre = film_dto.genre[0]

        got = await self.client.get(f"/api/v1/films/?filter[genre]={genre.name}")

        assert len(got) == 1
        assert got[0]["uuid"] == str(film_dto.uuid)
        assert got[0]["title"] == film_dto.title

    async def test_films_for_subscribers(self, settings, elastic, subscription_film_es, film_es, subscriber_token):
        """If an authorized user has a subscription, all films are returned (both subscription-only and 'free')."""
        headers = {"Authorization": f"Bearer {subscriber_token}"}
        got = requests.get(f"{settings.CLIENT_BASE_URL}/api/v1/films", headers=headers).json()

        assert len(got) == 2

    async def test_films_for_viewer(self, settings, elastic, subscription_film_es, film_es, viewer_token):
        """If an authorized user doesn't have a subscription, only free/public films are returned."""
        headers = {"Authorization": f"Bearer {viewer_token}"}
        got = requests.get(f"{settings.CLIENT_BASE_URL}/api/v1/films", headers=headers).json()

        assert len(got) == 1

    @pytest.fixture
    async def viewer_token(self, settings, auth0_token) -> str:
        base_url = settings.AUTH_BASE_URL
        data = {"email": "viewer@gmail.com", "password": "test"}
        with requests.Session() as client:
            client.post(f"{base_url}/api/v1/auth/register", data=data)
            credentials = client.post(f"{base_url}/api/v1/auth/login", data=data)
            access_token = credentials.json()["data"]["access_token"]
            return access_token

    @pytest.fixture
    async def subscriber_token(self, settings, auth0_token) -> str:
        base_url = settings.AUTH_BASE_URL
        data = {"email": "test@gmail.com", "password": "test"}
        headers = {"Authorization": f"Bearer {auth0_token}"}

        # register user
        with requests.Session() as client:
            user_response = client.post(f"{base_url}/api/v1/auth/register", data=data)
            if user_response.status_code != 201:  # if user already exists, just get an access token
                # authorizing for retrieving a JWT
                credentials = client.post(f"{base_url}/api/v1/auth/login", data=data)
                access_token = credentials.json()["data"]["access_token"]
                return access_token

        # get user id
        user_id = user_response.json()["data"]["id"]

        with requests.Session() as client:
            # get id of role with subscription
            roles_response = client.get(f"{settings.AUTH_BASE_URL}/api/v1/roles", headers=headers)
            roles = roles_response.json()["data"]
            role_id = self._find_subscription_role_id(roles)

            # assign given role to user
            client.post(f"{base_url}/api/v1/users/{user_id}/roles/{role_id}", headers=headers)

            # authorizing for retrieving a JWT
            credentials = client.post(f"{base_url}/api/v1/auth/login", data=data)
            access_token = credentials.json()["data"]["access_token"]
            return access_token

    @pytest.fixture
    async def auth0_token(self, settings) -> str:
        payload = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": settings.AUTH0_API_AUDIENCE,
            "grant_type": settings.AUTH0_GRANT_TYPE,
        }
        headers = {"content-type": "application/json"}

        with requests.Session() as client:
            got = client.post(settings.AUTH0_AUTHORIZATION_URL, json=payload, headers=headers)

        access_token = got.json()["access_token"]
        self._access_token = access_token
        return access_token

    @staticmethod
    def _find_subscription_role_id(roles: list[dict]) -> str:
        for role in roles:
            if role["name"] == DefaultRoles.SUBSCRIBERS.value:
                return role["id"]
