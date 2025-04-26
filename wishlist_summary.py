import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Load secrets from environment variables
SHOP_URL = os.getenv('SHOP_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

# Fetch customers and wishlist data
def get_today_wishlist_count():
    today = datetime.now().date()

    url = f"https://{SHOP_URL}/admin/api/2023-10/customers.json?fields=id,email,created_at,metafields"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    customers = response.json().get('customers', [])

    count = 0

    for customer in customers:
        customer_id = customer['id']
        
        # Fetch metafields for each customer
        metafield_url = f"https://{SHOP_URL}/admin/api/2023-10/customers/{customer_id}/metafields.json"
        metafield_resp = requests.get(metafield_url, headers=headers)
        metafields = metafield_resp.json().get('metafields', [])

        for mf in metafields:
            if mf['namespace'] == 'swishlist' and mf['key'] == 'wishlist':
                created_at = datetime.strptime(mf['created_at'], "%Y-%m-%dT%H:%M:%S%z").date()
                if created_at == today:
                    count += 1

    return count

# Send email
def send_email(wishlist_count):
    subject = "Daily Wishlist Summary"
    body = f"Today, {wishlist_count} wishlist items were added to your store."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())

# Main script
if __name__ == "__main__":
    try:
        wishlist_count = get_today_wishlist_count()
        send_email(wishlist_count)
        print(f"Email sent successfully with {wishlist_count} wishlist items.")
    except Exception as e:
        print(f"Error: {e}")
