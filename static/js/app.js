
const $ = id => document.getElementById(id);

let busy = false;
let currentState = { status: 'chat', count: 0 };

function bubble(text, cls = 'bot') {
    if (!text) return;

    const p = document.createElement('p');
    p.className = cls;
    p.textContent = text;

    $('chat').append(p);
    $('chat').scrollTop = $('chat').scrollHeight;

    return p;
}

function updateControls() {
    const s = currentState;

    $('message').disabled =
        busy || s.status !== 'chat';

    $('form').querySelector('button').disabled =
        busy || s.status !== 'chat';

    $('manual').disabled =
        busy || !['chat', 'offer'].includes(s.status);

    $('resolved').disabled =
        busy ||
        !['chat', 'offer'].includes(s.status) ||
        s.count === 0;

    $('reset').disabled = busy;

    $('controls')
        .querySelectorAll('button, textarea')
        .forEach(el => el.disabled = busy);
}

function control(label, action, extra = {}, secondary = false) {
    const b = document.createElement('button');

    b.textContent = label;

    if (secondary) b.className = 'secondary';

    b.onclick = () => send(
        action,
        typeof extra === 'function' ? extra() : extra
    );

    $('controls').append(b);
}

function render(d) {
    const s = d.state;
    currentState = s;

    $('controls').replaceChildren();
    $('inspector').replaceChildren();

    const fields = {
        'Analysis mode': s.source || 'Not yet analysed',
        'Fallback reason': s.fallback || 'None',
        'Intent': s.intent,
        'Open issue mentions': s.count,
        'Frustration signal': s.negative
            ? 'Detected' : 'Not detected',
        'Capability gap': s.unsupported
            ? 'Detected' : 'No gap flagged',
        'Decision reason': s.reason || 'None',
        'Execution status': s.status,
        'Ticket': s.ticket || 'None'
    };

    for (const [k, v] of Object.entries(fields)) {
        const dt = document.createElement('dt');
        const dd = document.createElement('dd');

        dt.textContent = k;
        dd.textContent = v;

        $('inspector').append(dt, dd);
    }

    if (s.status === 'offer') {
        bubble(
            s.reason + ' Would you like human support?'
        );

        control('Connect to human', 'accept');
        control('Continue with AI', 'decline', {}, true);
    }

    if (s.status === 'review') {
        const label = document.createElement('label');

        label.textContent =
            'Review or edit the information for the simulated handoff';

        label.htmlFor = 'summary';

        const t = document.createElement('textarea');

        t.id = 'summary';
        t.value = d.summary || '';

        $('controls').append(label, t);

        control(
            'Confirm simulated handoff',
            'confirm',
            () => ({ summary: t.value })
        );

        control('Cancel', 'decline', {}, true);
    }

    if (s.status === 'queued') {
        control(
            'Cancel simulated request',
            'cancel',
            {},
            true
        );
    }

    updateControls();
}

async function send(action, extra = {}) {
    if (busy) return;

    busy = true;
    updateControls();

    $('form').setAttribute('aria-busy', 'true');

    let userBubble = null;
    let loading = null;

    // Show the user's message immediately.
    if (action === 'message') {
        userBubble = bubble(extra.message, 'user');
    }

    loading = bubble(
        action === 'message'
            ? 'Analysing your message…'
            : 'Processing your request…',
        'bot loading'
    );

    try {
        const r = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action, ...extra })
        });

        const d = await r.json();

        if (!r.ok) {
            throw Error(d.error || 'Request unavailable');
        }

        loading?.remove();

        if (action === 'reset') {
            $('chat').replaceChildren();
            $('message').value = '';
        }

        bubble(d.reply);
        render(d);

    } catch (e) {
        loading?.remove();

        if (action === 'message') {
            userBubble?.remove();
            $('message').value = extra.message;
        }

        bubble(
            'Request could not be completed: ' +
            e.message +
            '. Please check the current state before retrying.',
            'bot error'
        );

    } finally {
        busy = false;

        $('form').removeAttribute('aria-busy');

        updateControls();

        if (currentState.status === 'chat') {
            $('message').focus();
        }
    }
}

$('form').onsubmit = e => {
    e.preventDefault();

    const message = $('message').value.trim();

    if (message && !busy) {
        $('message').value = '';
        send('message', { message });
    }
};

$('manual').onclick = () => send('manual');
$('resolved').onclick = () => send('resolved');
$('reset').onclick = () => send('reset');

send('reset');
