import pytest
import ai_service

@pytest.fixture(autouse=True)
def local_by_default(monkeypatch):
    monkeypatch.setenv("SMART_HANDOFF_MODE", "local")

from escalation import decide
from ai_service import analyse
from app import app

def test_policy():
    assert decide(1) is None
    assert decide(3)
    assert decide(2,negative=True)
    assert decide(1,unsupported=True)
    assert decide(3,declined=True) is None
    assert decide(3,resolved=True) is None

def test_intent():
    assert analyse('Where is my refund?')['intent']=='refund'
    assert analyse('Still waiting','refund')['intent']=='refund'

def test_handoff():
    with app.test_client() as c:
        def act(a,**kw): return c.post('/api/action',json={'action':a,**kw})
        assert act('message',message='Track my parcel').json['state']['status']=='chat'
        assert act('message',message='Where is my refund?').json['state']['status']=='offer'
        assert act('accept').json['state']['status']=='review'
        assert act('confirm',summary='Edited summary').json['state']['status']=='queued'
        assert act('confirm').status_code==409
        assert act('cancel').json['state']['status']=='chat'
        assert act('manual').json['state']['status']=='review'
        assert act('decline').json['state']['status']=='chat'


from ai_service import analyse


def test_order_intent():
    result = analyse("Where is my order?")
    assert result["intent"] == "delivery"


def test_context_follow_up():
    result = analyse(
        "Help me find it",
        previous="refund"
    )
    assert result["intent"] == "refund"


def test_explicit_intent_change():
    result = analyse(
        "Where is my parcel?",
        previous="refund"
    )
    assert result["intent"] == "delivery"


def test_frustration_signal():
    result = analyse(
        "I am disappointed with my refund"
    )
    assert result["negative"] is True


def enable_mock(monkeypatch):
    monkeypatch.setenv('SMART_HANDOFF_MODE', 'hybrid')
    monkeypatch.setenv('GEMINI_API_KEY', 'fake-test-key')


def test_hybrid_success(monkeypatch):
    enable_mock(monkeypatch)
    monkeypatch.setattr(ai_service, '_gemini', lambda *a: {'intent':'delivery','negative':False,'manual':False})
    with app.test_client() as c:
        s=c.post('/api/action',json={'action':'message','message':'Has it left the warehouse?'}).json['state']
        assert s['intent']=='delivery' and s['source'].startswith('Gemini')


def test_hybrid_failure(monkeypatch):
    enable_mock(monkeypatch)
    def fail(*a): raise TimeoutError()
    monkeypatch.setattr(ai_service, '_gemini', fail)
    result=ai_service.analyse_hybrid('Where is my refund?')
    assert result['intent']=='refund' and result['fallback']=='TimeoutError'


def test_invalid_model_output(monkeypatch):
    enable_mock(monkeypatch)
    monkeypatch.setattr(ai_service, '_gemini', lambda *a: {'intent':'invalid','negative':'false','manual':False})
    assert ai_service.analyse_hybrid('Track my parcel')['source']=='Local rules (fallback)'


def test_model_cannot_block_manual_request(monkeypatch):
    enable_mock(monkeypatch)
    monkeypatch.setattr(ai_service, '_gemini', lambda *a: {'intent':'other','negative':False,'manual':False})
    with app.test_client() as c:
        s=c.post('/api/action',json={'action':'message','message':'I want a human agent'}).json['state']
        assert s['status']=='review' and not s.get('ticket')



from ai_service import analyse, analyse_hybrid


def test_fallback_implicit_manual_request():
    result = analyse("Can I speak to someone instead?")
    assert result["manual"] is True


def test_fallback_implicit_return():
    result = analyse("I no longer want to keep this item.")
    assert result["intent"] == "return"


def test_fallback_warehouse_query():
    result = analyse("Has it left the warehouse yet?")
    assert result["intent"] == "delivery"


def test_fallback_context_and_frustration():
    result = analyse(
        "This is the third time I have asked. Nothing has changed.",
        previous="refund"
    )
    assert result["intent"] == "refund"
    assert result["negative"] is True


def test_manual_request_refusal():
    result = analyse("I don't want a human.")
    assert result["manual"] is False


def test_temporary_error_retry(monkeypatch):
    import ai_service
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda **kw: None)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("SMART_HANDOFF_MODE", raising=False)
    monkeypatch.setattr(ai_service.time, "sleep", lambda _: None)

    calls = []

    class TemporaryError(Exception):
        code = 503

    def mock_gemini(*args):
        calls.append(1)

        if len(calls) == 1:
            raise TemporaryError("Simulated service error")

        return {
            "intent": "delivery",
            "negative": False,
            "manual": False
        }

    monkeypatch.setattr(ai_service, "_gemini", mock_gemini)

    result = analyse_hybrid("Where is my order?")

    assert len(calls) == 2
    assert result["intent"] == "delivery"
    assert result["source"].startswith("Gemini")
    assert result["fallback"] is None


def test_persistent_error_fallback(monkeypatch):
    import ai_service
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda **kw: None)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("SMART_HANDOFF_MODE", raising=False)
    monkeypatch.setattr(ai_service.time, "sleep", lambda _: None)

    calls = []

    class TemporaryError(Exception):
        code = 503

    def mock_gemini(*args):
        calls.append(1)
        raise TemporaryError("Simulated persistent failure")

    monkeypatch.setattr(ai_service, "_gemini", mock_gemini)

    result = analyse_hybrid("Can I speak to someone instead?")

    assert len(calls) == 2
    assert result["manual"] is True
    assert result["source"] == "Local rules (fallback)"


def test_invalid_argument_no_retry(monkeypatch):
    import ai_service
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda **kw: None)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("SMART_HANDOFF_MODE", raising=False)

    calls = []

    class InvalidArgument(Exception):
        code = 400

    def mock_gemini(*args):
        calls.append(1)
        raise InvalidArgument("Simulated invalid request")

    monkeypatch.setattr(ai_service, "_gemini", mock_gemini)

    result = analyse_hybrid("Where is my order?")

    assert len(calls) == 1
    assert result["source"] == "Local rules (fallback)"
    assert result["intent"] == "delivery"
