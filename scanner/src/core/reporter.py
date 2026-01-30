import os, json
from jinja2 import Template
from datetime import datetime

HTML_TEMPLATE = """<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .finding { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .finding.high { border-left: 5px solid #d32f2f; }
        .finding.medium { border-left: 5px solid #f57c00; }
        .finding.low { border-left: 5px solid #388e3c; }
        .severity { font-weight: bold; padding: 5px 10px; border-radius: 3px; }
        .severity.high { background-color: #ffebee; color: #d32f2f; }
        .severity.medium { background-color: #fff3e0; color: #f57c00; }
        .severity.low { background-color: #e8f5e9; color: #388e3c; }
        .cvss { background-color: #fce4ec; padding: 10px; border-radius: 3px; margin: 10px 0; font-weight: bold; }
        .cvss.critical { background-color: #b71c1c; color: white; }
        .cvss.high { background-color: #d32f2f; color: white; }
        .cvss.medium { background-color: #f57c00; color: white; }
        .cvss.low { background-color: #388e3c; color: white; }
        .meta { color: #666; font-size: 0.9em; margin-top: 10px; }
        .mitre { background-color: #e3f2fd; padding: 10px; border-radius: 3px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Azure Cloud Security Scan Report</h1>
    {% if findings %}
        {% for f in findings %}
        <div class="finding {{ f.severity.lower() }}">
            <h3>{{ f.id }}</h3>
            <p><strong>{{ f.description }}</strong></p>
            <p class="severity {{ f.severity.lower() }}">Severity: {{ f.severity }}</p>
            {% set cvss_class = 'critical' if f.cvss_score >= 9.0 else ('high' if f.cvss_score >= 7.0 else ('medium' if f.cvss_score >= 4.0 else 'low')) %}
            <div class="cvss {{ cvss_class }}">CVSS 3.1: {{ f.cvss_score }}</div>
            <div class="meta">
                <p><strong>Service:</strong> {{ f.service }}</p>
                <p><strong>Resource:</strong> {{ f.resource }}</p>
                <p><strong>Rule:</strong> {{ f.rule }}</p>
            </div>
            <div class="mitre">
                <strong>MITRE ATT&CK:</strong> {{ f.mitre }}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p><em>No findings detected. Your resources appear to be secure!</em></p>
    {% endif %}
</body>
</html>"""

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
