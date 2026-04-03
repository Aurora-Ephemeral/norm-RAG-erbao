import pytest
from app.util import IntentRouter

@pytest.fixture
def router():
    return IntentRouter()

class TestIntentRouter(object):

    def test_surface_category(self, router):
        query = "盐雾测试怎么做"
        result = router.predict(query)
        assert result["category"].index("表面防护") == 1


    def test_other_router(self, router):
        query = "你是谁"
        result = router.predict(query)
        assert result["category"] == "other"