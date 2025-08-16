import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
# Only load .env locally
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

client = OpenAI(api_key=OPENAI_API_KEY)

CATEGORIES = ["sports", "business", "science", "politics"]

def fetch_news(category):
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&pageSize=3&apiKey={NEWS_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    return [
        {
            "title": article["title"],
            "description": article.get("description", ""),
            "url": article["url"]
        }
        for article in data.get("articles", [])
    ]

def summarize_news(news_items):
    summaries = []
    for item in news_items:
        prompt = f"Summarize this news in one short sentence:\nTitle: {item['title']}\nDescription: {item['description']}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        summary = resp.choices[0].message.content.strip()
        summaries.append(f"- {summary} ([Read more]({item['url']}))")
    return "\n".join(summaries)

def build_email():
    email_content = "📅 **Your Daily News Digest**\n\n"
    for cat in CATEGORIES:
        news = fetch_news(cat)
        if news:
            email_content += f"### {cat.capitalize()}:\n"
            email_content += summarize_news(news)
            email_content += "\n\n"
    return email_content

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())

if __name__ == "__main__":
    content = build_email()
    send_email("Daily News Digest", content)
    print("Email sent!")
