# SmartHandoff
A local rule-based customer support prototype with mixed-initiative escalation. All records and handoffs are fictional; no LLM or real agent is connected.

## Run
Install Flask (`python -m pip install flask pytest`), then `python app.py`. Open http://127.0.0.1:5000. Run tests with `python -m pytest -q`.

## Inspect
Try delivery, refund, declining an offer, manual handoff, editing the summary, confirming and cancelling a simulated request. The inspector exposes decision signals. State is held in memory and is lost on restart. Keyword matching is limited and may misclassify paraphrases. The summary is a transcript excerpt, not an AI-generated summary. No external API is required.

## Authorship
Initial implementation generated with ChatGPT assistance. Student review, modifications and verification should be recorded in docs/development_log.md using actual evidence.
