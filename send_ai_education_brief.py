import os
import smtplib
import re
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
        "For each item provide a title, 2-3 sentence summary, why it matters for counselors, and a source link.\n\n"
        "Write in a warm professional tone. Use only plain ASCII characters - no special quotes or dashes."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text
        text = text.encode("utf-8").decode("ascii", "ignore")
        return text
    except Exception as e:
        return "Could not fetch news: " + str(e)


def send_email(content):
    gmail_user = "hannamickedu@gmail.com"
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        print("No Gmail app password found")
        return

    today = datetime.now().strftime("%A, %B %d, %Y")
    day_of_week = datetime.now().strftime("%A")

    content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content_html = content_html.replace('\n\n', '</p><p style="margin: 0 0 16px;">').replace('\n', '<br>')
    content_html = '<p style="margin: 0 0 16px;">' + content_html + '</p>'

    html = (
        '<html><body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; color: #1A202C;">'
        '<div style="background: #1A6B5A; padding: 24px; border-radius: 8px 8px 0 0;">'
        '<div style="color: #E3F4F0; font-size: 11px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">The EdTech Distinction</div>'
        '<h1 style="color: white; font-size: 24px; margin: 0;">AI in Education Daily Brief</h1>'
        '<p style="color: rgba(255,255,255,0.7); margin: 8px 0 0;">' + today + '</p>'
        '</div>'
        '<div style="background: white; padding: 24px; border: 1px solid #E2E8F0; border-top: none;">'
        '<p style="color: #4A5568; font-size: 14px; margin-bottom: 24px; font-style:
