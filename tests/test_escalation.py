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
