import os, json
from jinja2 import Template
from datetime import datetime

HTML_TEMPLATE = "<html><body><h1>Cloud Report</h1>{% for f in findings %}<p>{{f.id}} - {{f.description}} ({{f.severity}})</p>{% endfor %}</body></html>"

def write_html(provider, findings, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    from jinja2 import Template
    html = Template(HTML_TEMPLATE).render(findings=findings)
    with open(out_path, "w") as f:
        f.write(html)

def write_json(findings, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump([f.__dict__ for f in findings], f, indent=2)
