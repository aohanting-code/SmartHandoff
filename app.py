from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import json, secrets
from ai_service import analyse
from escalation import decide
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DATA = json.loads((Path(__file__).parent/'data/mock_orders.json').read_text())
# In-memory prototype state; no real customer records or external services.
STATES = {}
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
        signals=analyse(msg,s['intent']); intent=signals['intent']; s['history'].append('Customer: '+msg)
        if signals['manual']:
            s['status']='review'; s['reason']='You requested human support.'
        else:
            if intent!=s['intent']: s.update(intent=intent,count=0,declined=False)
            s['count']+=1; s['negative']=signals['negative']; s['unsupported']=intent in ('refund','other')
            reply=DATA.get(intent,'I cannot find relevant information in the demo records.')
            s['history'].append('Assistant: '+reply)
            s['reason']=decide(s['count'],s['negative'],s['unsupported'],declined=s['declined'])
            if s['reason']: s['status']='offer'
    elif a=='manual' and s['status'] in ('chat','offer'):
        s['status']='review'; s['reason']='You requested human support.'
    elif a=='accept' and s['status']=='offer': s['status']='review'
    elif a=='decline' and s['status'] in ('offer','review'):
        s.update(status='chat',declined=True,reason=None); reply='Continuing with AI support. Human support remains available.'
    elif a=='resolved' and s['status'] in ('chat','offer'):
        s.update(status='chat',count=0,declined=False,reason=None); reply='Thanks for confirming the issue is resolved.'
    elif a=='confirm' and s['status']=='review':
        summary=str(d.get('summary',''))[:4000]; s.update(status='queued',ticket='DEMO-'+secrets.token_hex(3).upper(),summary=summary); reply='Simulated queue request created. No real agent has been contacted.'
    elif a=='cancel' and s['status']=='queued':
        s.update(status='chat',declined=True,reason=None,ticket=None); reply='Simulated request cancelled.'
    else: return jsonify(error='Action unavailable in current state.'),409
    if s['status']=='review': summary='\n'.join(s['history'])[-4000:]
    return jsonify(reply=reply,summary=summary,state={k:v for k,v in s.items() if k not in ('history','summary')})
if __name__=='__main__': app.run()
