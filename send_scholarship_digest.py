"""
Scholarship Hub — Monday Digest Email
Runs every Monday at 7 AM CT via GitHub Actions.
Uses Claude AI to suggest new scholarships for Hanna to review.
Sends a digest email to hannamickedu@gmail.com.
"""

import json
import os
import smtplib
import anthropic
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta


def get_current_scholarships():
    try:
        with open("scholarships.json") as f:
            data = json.load(f)
        return [s["name"] for s in data.get("scholarships", [])]
    except Exception:
        return []


def fetch_scholarship_suggestions():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    client = anthropic.Anthropic(api_key=api_key)
    current = get_current_scholarships()
    today = datetime.now().strftime("%B %d, %Y")

    prompt = (
        "Today is " + today + ". You are helping a Kansas school counselor find scholarships for high school students.\n\n"
        "Suggest 6-8 real scholarships that are currently open and accepting applications. "
        "Focus on scholarships for Kansas students OR nationally available ones.\n\n"
        "These scholarships are ALREADY on the site, so do NOT suggest them:\n"
        + "\n".join("- " + name for name in current) + "\n\n"
        "For each scholarship provide:\n"
        "- Name\n"
        "- Award amount\n"
        "- Brief description (1-2 sentences)\n"
        "- Deadline\n"
        "- Website URL\n"
        "- Why it is good for Kansas students\n\n"
        "Format as a simple numbered list. Be honest — only include scholarships you are confident are real."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return "Could not fetch suggestions: " + str(e)


def send_email(suggestions):
    suggestions = suggestions.encode("ascii", "ignore").decode("ascii")
    gmail_user = "hannamickedu@gmail.com"
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        print("No Gmail app password found")
        return

    today = datetime.now().strftime("%B %d, %Y")

    html = """
    <html><body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; color: #1A202C;">
    <div style="background: #0F2044; padding: 24px; border-radius: 8px 8px 0 0;">
      <div style="color: #D4A017; font-size: 11px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">Kansas Scholarship Hub</div>
      <h1 style="color: white; font-size: 24px; margin: 0;">Weekly Scholarship Digest</h1>
      <p style="color: rgba(255,255,255,0.7); margin: 8px 0 0;">""" + today + """</p>
    </div>
    <div style="background: white; padding: 24px; border: 1px solid #E2E8F0; border-top: none;">
      <p style="color: #4A5568; font-size: 14px; margin-bottom: 20px;">
        Here are this week's scholarship suggestions to review. These are <strong>AI-generated suggestions</strong> — 
        please verify each link before adding to the site.
      </p>
      <div style="background: #F5F7FA; border-radius: 8px; padding: 20px; white-space: pre-wrap; font-size: 14px; line-height: 1.7; color: #2D3748;">""" + suggestions + """</div>
      <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #E2E8F0;">
        <p style="font-size: 13px; color: #4A5568; margin-bottom: 12px;"><strong>To add a scholarship to the site:</strong></p>
        <ol style="font-size: 13px; color: #4A5568; line-height: 1.8;">
          <li>Verify the link works and the scholarship is real</li>
          <li>Go to your <a href="https://github.com/hannamickedu/ksscholarshiphub" style="color: #0F2044;">GitHub repository</a></li>
          <li>Open <code>update_scholarships.py</code> and add it to PERMANENT_SCHOLARSHIPS</li>
          <li>Commit the change — it appears on the site within minutes</li>
        </ol>
      </div>
    </div>
    <div style="background: #F5F7FA; padding: 16px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #A0AEC0;">
      Kansas Scholarship Hub &nbsp;·&nbsp; hannamickedu.github.io/ksscholarshiphub &nbsp;·&nbsp; Updated every Monday
    </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📚 Scholarship Digest — " + today
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, gmail_user, msg.as_string())
        print("Scholarship digest sent to " + gmail_user)
    except Exception as e:
        print("Email error: " + str(e))


def main():
    print("Generating scholarship digest...")
    suggestions = fetch_scholarship_suggestions()
    send_email(suggestions)
    print("Done!")


if __name__ == "__main__":
    main()
