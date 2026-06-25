"""
AI in Education Daily Brief
Runs every day at 12:00 PM CT via GitHub Actions.
Uses Claude AI with web search to find the latest AI in education news.
Sends a digest email to hannamickedu@gmail.com.
"""

import os
import smtplib
import anthropic
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def fetch_ai_education_news():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "No API key found."

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = (
        "Today is " + today + ". You are writing a daily brief for Hanna, a school counseling dean and EdTech thought leader in Kansas.\n\n"
        "Provide 3-4 summaries of the most relevant recent developments in AI and education. Cover a mix of:\n"
        "- New classroom AI tools and edtech news\n"
        "- AI policy, ethics, and research in education\n"
        "- AI in school counseling and student mental health\n\n"
        "For each item:\n"
        "**Title of the story or development**\n"
        "2-3 sentence summary of what it is and why it matters for educators.\n"
        "Why it matters for school counselors specifically (1 sentence).\n"
        "Source/link if you know it.\n\n"
        "Write in a warm, professional tone — like a trusted colleague sharing what they found interesting today. "
        "Focus on practical implications for K-12 educators and counselors. "
        "If you are not sure about a specific recent story, share a meaningful insight or development you are confident about."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return "Could not fetch news: " + str(e)


def send_email(content):
    content = content.encode("ascii", "ignore").decode("ascii")
    gmail_user = "hannamickedu@gmail.com"
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        print("No Gmail app password found")
        return

    today = datetime.now().strftime("%A, %B %d, %Y")
    day_of_week = datetime.now().strftime("%A")

    # Convert markdown-style bold to HTML
    import re
    content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content_html = content_html.replace('\n\n', '</p><p style="margin: 0 0 16px;">').replace('\n', '<br>')
    content_html = '<p style="margin: 0 0 16px;">' + content_html + '</p>'

    html = """
    <html><body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; color: #1A202C;">
    <div style="background: #1A6B5A; padding: 24px; border-radius: 8px 8px 0 0;">
      <div style="color: #E3F4F0; font-size: 11px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">The EdTech Distinction</div>
      <h1 style="color: white; font-size: 24px; margin: 0;">AI in Education Daily Brief</h1>
      <p style="color: rgba(255,255,255,0.7); margin: 8px 0 0;">""" + today + """</p>
    </div>
    <div style="background: white; padding: 24px; border: 1px solid #E2E8F0; border-top: none;">
      <p style="color: #4A5568; font-size: 14px; margin-bottom: 24px; font-style: italic;">
        Good afternoon, Hanna. Here's what's happening at the intersection of AI and education today.
      </p>
      <div style="font-size: 15px; line-height: 1.7; color: #2D3748;">""" + content_html + """</div>
    </div>
    <div style="background: #F5F7FA; padding: 16px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #A0AEC0;">
      The EdTech Distinction &nbsp;·&nbsp; Daily AI in Education Brief &nbsp;·&nbsp; Delivered at noon CT
    </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🤖 AI in Education Brief — " + day_of_week + ", " + datetime.now().strftime("%B %d")
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, gmail_user, msg.as_string())
        print("AI Education brief sent to " + gmail_user)
    except Exception as e:
        print("Email error: " + str(e))


def main():
    print("Generating AI in Education brief...")
    content = fetch_ai_education_news()
    send_email(content)
    print("Done!")


if __name__ == "__main__":
    main()
