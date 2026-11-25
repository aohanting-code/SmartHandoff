from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import json, secrets, re
from ai_service import analyse_hybrid
from escalation import decide
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DATA = json.loads((Path(__file__).parent/'data/mock_orders.json').read_text())
# In-memory prototype state; fictional records; optional external model analysis.
STATES = {}
def capability_gap(message, intent):
    text = message.lower()

    if intent in ('refund', 'other'):
        return True

    if intent == 'return':
        return bool(re.search(
            r'\b(return label|shipping label|'
            r'prepaid label|arrange collection|'
            r'book a collection)\b',
            text
        ))

    if intent == 'delivery':
        return bool(re.search(
            r'\b(change|update|correct) '
            r'(?:my |the )?(?:delivery |shipping )?address\b|'
            r'\b(cancel my order|cancel the order|'
            r'reschedule delivery)\b',
            text
        ))

    return False
def state():
    if 'sid' not in session: session['sid'] = secrets.token_hex(16)
    return STATES.setdefault(session['sid'], {'intent':'other','count':0,'declined':False,'history':[],'status':'chat','reason':None})
@app.get('/')
def home(): return render_template('index.html')
@app.post('/api/action')
def action():
    s=state(); d=request.get_json() or {}; a=d.get('action'); reply=''; summary=None
    if a=='reset':
        STATES.pop(session['sid'],None); s=state(); reply='Hello! How can I help with your demo order?'
    elif a=='message' and s['status']=='chat':
        msg=str(d.get('message','')).strip()[:500]
        if not msg: return jsonify(error='Enter a message.'),400
        signals=analyse_hybrid(msg,s['intent'],s['history']); s.update(source=signals['source'],fallback=signals['fallback']); intent=signals['intent']; s['history'].append('Customer: '+msg)
        if signals['manual']:
            s['status']='review'; s['reason']='You requested human support.'
        else:
            if intent!=s['intent']: s.update(intent=intent,count=0,declined=False)
            s['count']+=1; s['negative']=signals['negative']; s['unsupported'] = capability_gap(msg, intent)
            reply = DATA.get(
                intent,
                'I cannot find relevant information in the demo records.')

            if s['unsupported'] and intent in ('return', 'delivery'):
                reply = (
                    'I can provide general information, but I cannot '
                    'complete this action in the current prototype. '
                    'Human support may be able to help.'
                )
            s['history'].append('Assistant: '+reply)
            s['reason']=decide(s['count'],s['negative'],s['unsupported'],declined=s['declined'])
            if s['reason']: s['status']='offer'
    elif a=='manual' and s['status'] in ('chat','offer'):
        s['status']='review'; s['reason']='You requested human support.'
    elif a=='accept' and s['status']=='offer': s['status']='review'
    elif a=='decline' and s['status'] in ('offer','review'):
        s.update(status='chat',declined=True,reason=None); reply='Continuing with AI support. Human support remains available.'
    elif a == 'resolved' and s['status'] in ('chat', 'offer'):
        if s['count'] == 0 and s['intent'] == 'other':
            return jsonify(error='No active issue to resolve.'), 409
        s.update(
            status='chat',
            intent='other',
            count=0,
            declined=False,
            negative=False,
            unsupported=False,
            reason=None,
            ticket=None,
            summary=None,
            history=[],
            source=None,
            fallback=None
        )
        reply = 'Thanks for confirming the issue is resolved. How else can I help?'
    elif a=='confirm' and s['status']=='review':
        summary=str(d.get('summary',''))[:4000]; s.update(status='queued',ticket='DEMO-'+secrets.token_hex(3).upper(),summary=summary); reply='Simulated queue request created. No real agent has been contacted.'
    elif a=='cancel' and s['status']=='queued':
        s.update(status='chat',declined=True,reason=None,ticket=None); reply='Simulated request cancelled.'
    else: return jsonify(error='Action unavailable in current state.'),409
    if s['status']=='review': summary='\n'.join(s['history'])[-4000:]
    return jsonify(reply=reply,summary=summary,state={k:v for k,v in s.items() if k not in ('history','summary')})
if __name__=='__main__': app.run()
