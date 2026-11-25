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
