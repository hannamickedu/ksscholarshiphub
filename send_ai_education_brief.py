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
    prompt = "Today is " + today + ". You are writing a daily brief for Hanna, a school counseling dean and EdTech thought leader in Kansas. Provide 3-4 summaries of recent developments in AI and education. Cover classroom AI tools, AI policy and ethics in education, and AI in school counseling. For each item provide a title, 2-3 sentence summary, why it matters for counselors, and a source link. Write in a warm professional tone. Use only plain ASCII characters."
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
    month_day = datetime.now().strftime("%B %d")

    content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content_html = content_html.replace('\n\n', '<br><br>').replace('\n', '<br>')

    header_style = 'background:#1A6B5A;padding:24px;border-radius:8px 8px 0 0;'
    eyebrow_style = 'color:#E3F4F0;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'
    h1_style = 'color:white;font-size:24px;margin:0;'
    date_style = 'color:rgba(255,255,255,0.7);margin:8px 0 0;'
    body_style = 'background:white;padding:24px;border:1px solid #E2E8F0;border-top:none;'
    intro_style = 'color:#4A5568;font-size:14px;margin-bottom:24px;font-style:italic;'
    content_style = 'font-size:15px;line-height:1.7;color:#2D3748;'
    footer_style = 'background:#F5F7FA;padding:16px;border-radius:0 0 8px 8px;text-align:center;font-size:12px;color:#A0AEC0;'

    html = (
        '<html><body style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#1A202C;">'
        '<div style="' + header_style + '">'
        '<div style="' + eyebrow_style + '">The EdTech Distinction</div>'
        '<h1 style="' + h1_style + '">AI in Education Daily Brief</h1>'
        '<p style="' + date_style + '">' + today + '</p>'
        '</div>'
        '<div style="' + body_style + '">'
        '<p style="' + intro_style + '">Good afternoon, Hanna. Here is what is happening at the intersection of AI and education today.</p>'
        '<div style="' + content_style + '">' + content_html + '</div>'
        '</div>'
        '<div style="' + footer_style + '">The EdTech Distinction - Daily AI in Education Brief - Delivered at noon CT</div>'
        '</body></html>'
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "AI in Education Brief - " + day_of_week + ", " + month_day
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.attach(MIMEText(html, "html", "utf-8"))

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
