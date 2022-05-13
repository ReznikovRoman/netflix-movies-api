from ..base import BaseClientTest, CacheTestMixin


class TestPersonList(CacheTestMixin, BaseClientTest):
    """Тестирование получения списка персон."""

    endpoint = "/api/v1/persons/"

    cache_es_index_name = "person"
    cache_field_name = "full_name"
    cache_es_fixture_name = "person_es"
    cache_dto_fixture_name = "person_dto"

    async def test_person_list_ok(self, persons_es, persons_dto):
        """Получение списка персон работает корректно."""
        fields_to_check = ("uuid", "full_name")

        got = await self.client.get("/api/v1/persons")

        assert len(got) == len(persons_dto)
        for field_to_check in fields_to_check:
            actual = set([person_data[field_to_check] for person_data in got])
            expected = set([(str(getattr(person, field_to_check))) for person in persons_dto])
            assert actual == expected
