import resend
from orchestrator.state import ProcurementState
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


def build_email_html(state: ProcurementState) -> str:
    request_id = state.get("request_id", "")
    item = state.get("item", "")
    quantity = state.get("quantity", 0)
    budget = state.get("budget", 0)
    decision = state.get("decision", "")
    supplier = state.get("selected_supplier") or {}
    forecast = state.get("price_forecast") or {}
    audit_log = state.get("audit_log", [])
    negotiation = state.get("negotiation_strategy", "")

    decision_color = {
        "buy":      "#00c853",
        "wait":     "#ff6d00",
        "escalate": "#ff0000"
    }.get(decision, "#707070")

    audit_rows = ""
    for line in audit_log[-15:]:
        dot_color = "#ff0000"
        if "OK" in line or "generated" in line.lower() or "approved" in line.lower():
            dot_color = "#00c853"
        elif "WAIT" in line or "falling" in line or "NOTE" in line:
            dot_color = "#ff6d00"

        time_part = ""
        text_part = line
        if line.startswith("["):
            try:
                end = line.index("]")
                raw_time = line[1:end]
                dt = datetime.fromisoformat(raw_time)
                time_part = dt.strftime("%H:%M:%S")
                text_part = line[end+2:]
            except:
                pass

        audit_rows += f"""
        <tr>
            <td style="padding:8px 16px;border-bottom:1px solid #1a1a1a;vertical-align:top;">
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <div style="width:6px;height:6px;border-radius:50%;background:{dot_color};
                                margin-top:5px;flex-shrink:0;"></div>
                    <div style="font-family:monospace;font-size:11px;color:#444;
                                min-width:60px;margin-top:1px;">{time_part}</div>
                    <div style="font-family:'Courier New',monospace;font-size:11px;
                                color:#888;line-height:1.5;">{text_part}</div>
                </div>
            </td>
        </tr>"""

    supplier_html = ""
    if supplier:
        risk = supplier.get("risk_score", 0)
        risk_color = "#00c853" if risk < 0.4 else "#ff6d00" if risk < 0.7 else "#ff0000"
        risk_label = "LOW RISK" if risk < 0.4 else "MED RISK" if risk < 0.7 else "HIGH RISK"
        supplier_html = f"""
        <div style="background:#0a0a0a;border-left:3px solid #C00000;
                    padding:16px 20px;margin:20px 0;">
            <div style="font-family:'Courier New',monospace;font-size:10px;color:#C00000;
                        letter-spacing:0.2em;text-transform:uppercase;margin-bottom:10px;">
                Selected Supplier</div>
            <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;
                        color:#ffffff;margin-bottom:4px;">{supplier.get('name', '—')}</div>
            <div style="font-family:'Courier New',monospace;font-size:11px;
                        color:#FF0000;margin-bottom:16px;">{supplier.get('url', '')}</div>
            <div style="display:flex;gap:32px;flex-wrap:wrap;">
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.15em;margin-bottom:4px;">PRICE / UNIT</div>
                    <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
                                color:#ffffff;">&#8377;{supplier.get('price', 0):,.0f}</div>
                </div>
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.15em;margin-bottom:4px;">RISK SCORE</div>
                    <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
                                color:{risk_color};">{risk:.3f}
                        <span style="font-size:10px;font-family:'Courier New',monospace;
                                     letter-spacing:0.1em;"> {risk_label}</span>
                    </div>
                </div>
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.15em;margin-bottom:4px;">TOTAL COST</div>
                    <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
                                color:#ffffff;">&#8377;{supplier.get('price', 0) * quantity:,.0f}</div>
                </div>
            </div>
        </div>"""

    forecast_html = ""
    if forecast:
        trend = forecast.get("trend", "stable")
        trend_color = "#ff0000" if trend == "rising" else "#00c853" if trend == "falling" else "#707070"
        forecast_html = f"""
        <div style="background:#0a0a0a;border-left:3px solid #707070;
                    padding:16px 20px;margin:20px 0;">
            <div style="font-family:'Courier New',monospace;font-size:10px;color:#707070;
                        letter-spacing:0.2em;text-transform:uppercase;margin-bottom:12px;">
                Price Intelligence</div>
            <div style="display:flex;gap:28px;flex-wrap:wrap;margin-bottom:10px;">
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.12em;margin-bottom:3px;">TREND</div>
                    <div style="font-family:Georgia,serif;font-size:16px;font-weight:700;
                                color:{trend_color};">{trend.upper()}</div>
                </div>
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.12em;margin-bottom:3px;">30 DAYS</div>
                    <div style="font-family:Georgia,serif;font-size:16px;font-weight:700;
                                color:#ffffff;">&#8377;{forecast.get('forecast_30_days', 0):,.0f}</div>
                </div>
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.12em;margin-bottom:3px;">60 DAYS</div>
                    <div style="font-family:Georgia,serif;font-size:16px;font-weight:700;
                                color:#ffffff;">&#8377;{forecast.get('forecast_60_days', 0):,.0f}</div>
                </div>
                <div>
                    <div style="font-family:'Courier New',monospace;font-size:9px;
                                color:#444;letter-spacing:0.12em;margin-bottom:3px;">90 DAYS</div>
                    <div style="font-family:Georgia,serif;font-size:16px;font-weight:700;
                                color:#ffffff;">&#8377;{forecast.get('forecast_90_days', 0):,.0f}</div>
                </div>
            </div>
            <div style="font-family:'Courier New',monospace;font-size:11px;
                        color:#707070;border-top:1px solid #1a1a1a;padding-top:8px;">
                {forecast.get('recommendation', '')}</div>
        </div>"""

    neg_html = ""
    if negotiation:
        neg_html = f"""
        <div style="background:#0a0a0a;border-left:3px solid #333;
                    padding:16px 20px;margin:20px 0;">
            <div style="font-family:'Courier New',monospace;font-size:10px;color:#444;
                        letter-spacing:0.2em;text-transform:uppercase;margin-bottom:10px;">
                Negotiation Strategy</div>
            <div style="font-family:'Courier New',monospace;font-size:11px;
                        color:#707070;line-height:1.8;white-space:pre-wrap;">{negotiation[:600]}...</div>
        </div>"""

    approve_url = f"https://procureiq-production-8df0.up.railway.app/approve/{request_id}"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#000000;">
<div style="max-width:620px;margin:0 auto;background:#000000;padding:0;">

    <div style="height:3px;background:linear-gradient(90deg,#C00000,#FF0000);"></div>

    <div style="padding:32px 32px 24px;border-bottom:1px solid #1a1a1a;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#C00000,#FF0000);
                        clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);"></div>
            <div>
                <div style="font-family:Georgia,serif;font-size:20px;font-weight:700;
                            color:#ffffff;letter-spacing:0.05em;">PROCUREIQ</div>
                <div style="font-family:'Courier New',monospace;font-size:9px;color:#FF0000;
                            letter-spacing:0.25em;text-transform:uppercase;margin-top:1px;">
                    Autonomous Procurement Intelligence</div>
            </div>
        </div>
    </div>

    <div style="padding:24px 32px;background:#0a0a0a;border-bottom:1px solid #1a1a1a;">
        <div style="font-family:'Courier New',monospace;font-size:10px;color:#C00000;
                    letter-spacing:0.25em;text-transform:uppercase;margin-bottom:8px;">
            &#11042; Human Approval Required</div>
        <div style="font-family:Georgia,serif;font-size:24px;font-weight:700;
                    color:#ffffff;margin-bottom:6px;">
            {item} &mdash; {quantity:,} units</div>
        <div style="font-family:'Courier New',monospace;font-size:11px;color:#707070;">
            Budget: &#8377;{budget:,.0f} &nbsp;&middot;&nbsp;
            ID: {request_id[:8].upper()} &nbsp;&middot;&nbsp;
            {datetime.now().strftime("%d %b %Y %H:%M")}</div>
    </div>

    <div style="padding:20px 32px;border-bottom:1px solid #1a1a1a;">
        <div style="display:inline-block;border:1px solid {decision_color};padding:8px 20px;">
            <span style="font-family:'Courier New',monospace;font-size:12px;font-weight:700;
                         color:{decision_color};letter-spacing:0.2em;text-transform:uppercase;">
                AI DECISION: {decision.upper()}</span>
        </div>
    </div>

    <div style="padding:0 32px;">
        {supplier_html}
        {forecast_html}
        {neg_html}
    </div>

    <div style="margin:0 32px 24px;border:1px solid #1a1a1a;">
        <div style="padding:10px 16px;border-bottom:1px solid #1a1a1a;background:#0a0a0a;">
            <span style="font-family:'Courier New',monospace;font-size:9px;color:#C00000;
                         letter-spacing:0.2em;text-transform:uppercase;">
                Audit Trail &mdash; Last 15 Steps</span>
        </div>
        <table style="width:100%;border-collapse:collapse;background:#000;">
            {audit_rows}
        </table>
    </div>

    <div style="padding:32px;text-align:center;border-top:1px solid #1a1a1a;">
        <a href="{approve_url}"
           style="display:inline-block;background:linear-gradient(135deg,#C00000,#FF0000);
                  color:#ffffff;text-decoration:none;
                  font-family:'Courier New',monospace;font-size:12px;font-weight:700;
                  letter-spacing:0.2em;text-transform:uppercase;padding:14px 40px;">
            APPROVE &amp; GENERATE DOCUMENTS &rarr;
        </a>
        <div style="margin-top:12px;font-family:'Courier New',monospace;font-size:10px;color:#444;">
            Or paste in browser:<br>
            <span style="color:#FF0000;">{approve_url}</span>
        </div>
    </div>

    <div style="height:3px;background:linear-gradient(90deg,#FF0000,#C00000);"></div>
    <div style="padding:16px 32px;text-align:center;">
        <div style="font-family:'Courier New',monospace;font-size:9px;color:#333;
                    letter-spacing:0.1em;">
            PROCUREIQ &middot; AUTONOMOUS PROCUREMENT INTELLIGENCE &middot;
            {datetime.now().strftime("%d %B %Y").upper()}
        </div>
    </div>

</div>
</body>
</html>"""

    return html


def send_approval_email(state: ProcurementState) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    to_email = os.getenv("GMAIL_ADDRESS")

    if not api_key or not to_email:
        print("Email not configured — skipping notification")
        return False

    try:
        resend.api_key = api_key
        item = state.get("item", "Unknown")
        request_id = state.get("request_id", "")
        html_content = build_email_html(state)

        print(f"Sending email to {to_email}...")
        response = resend.Emails.send({
            "from": "ProcureIQ <onboarding@resend.dev>",
            "to": [to_email],
            "subject": f"[ProcureIQ] Approval Required — {item} | {request_id[:8].upper()}",
            "html": html_content
        })

        print(f"Email sent successfully for request {request_id[:8].upper()}: {response}")
        return True

    except Exception as e:
        print(f"Email failed: {e}")
        return False