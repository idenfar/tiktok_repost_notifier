diff --git a//dev/null b/tiktok_notifier.py
index 0000000000000000000000000000000000000000..791cfd0f19370c03b98b50d87ea1d22970e04b5a 100644
--- a//dev/null
+++ b/tiktok_notifier.py
@@ -0,0 +1,121 @@
+import json
+import os
+import smtplib
+from email.mime.text import MIMEText
+from pathlib import Path
+import requests
+from bs4 import BeautifulSoup
+
+try:
+    from twilio.rest import Client
+    TWILIO_AVAILABLE = True
+except ImportError:
+    TWILIO_AVAILABLE = False
+
+BASE_DIR = Path(__file__).resolve().parent
+CONFIG_FILE = BASE_DIR / "config.json"
+DATA_DIR = BASE_DIR / "data"
+DATA_DIR.mkdir(exist_ok=True)
+
+
+def _expand_env_vars(value):
+    if isinstance(value, dict):
+        return {k: _expand_env_vars(v) for k, v in value.items()}
+    if isinstance(value, list):
+        return [_expand_env_vars(v) for v in value]
+    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
+        return os.getenv(value[2:-1], "")
+    return value
+
+
+def load_config():
+    with CONFIG_FILE.open() as f:
+        data = json.load(f)
+    return _expand_env_vars(data)
+
+
+def load_seen(username):
+    file = DATA_DIR / f"seen_{username}.json"
+    if file.exists():
+        with file.open() as f:
+            return json.load(f)
+    return []
+
+
+def save_seen(username, seen):
+    file = DATA_DIR / f"seen_{username}.json"
+    with file.open("w") as f:
+        json.dump(seen, f)
+
+
+def scrape_user(username):
+    url = f"https://www.tiktok.com/@{username}"
+    headers = {"User-Agent": "Mozilla/5.0"}
+    resp = requests.get(url, headers=headers)
+    if resp.status_code != 200:
+        raise RuntimeError(f"Failed to fetch {username}: {resp.status_code}")
+    soup = BeautifulSoup(resp.text, "html.parser")
+    links = set()
+    for a in soup.find_all("a", href=True):
+        href = a["href"]
+        if f"/@{username}/video/" in href:
+            if href.startswith("/"):
+                href = "https://www.tiktok.com" + href
+            links.add(href)
+    return list(links)
+
+
+def send_email(config, new_items):
+    if not config.get("enabled"):
+        return
+    body_lines = ["New TikTok posts:"]
+    for username, link in new_items:
+        body_lines.append(f"- {username}: {link}")
+    msg = MIMEText("\n".join(body_lines))
+    msg["Subject"] = "TikTok Updates"
+    msg["From"] = config["address"]
+    msg["To"] = config["to"]
+
+    with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
+        server.starttls()
+        server.login(config["address"], config["password"])
+        server.send_message(msg)
+    print("Email sent")
+
+
+def send_sms(config, new_items):
+    if not config.get("enabled") or not TWILIO_AVAILABLE:
+        return
+    client = Client(config["account_sid"], config["auth_token"])
+    lines = [f"{u}: {l}" for u, l in new_items]
+    body = "\n".join(lines)
+    if len(body) > 160:
+        body = body[:157] + "..."
+    message = client.messages.create(
+        body=body,
+        from_=config["from_number"],
+        to=config["to_number"],
+    )
+    print("SMS sent", message.sid)
+
+
+def main():
+    config = load_config()
+    all_new = []
+    for username in config.get("usernames", []):
+        seen = load_seen(username)
+        links = scrape_user(username)
+        new_links = [l for l in links if l not in seen]
+        if new_links:
+            all_new.extend([(username, l) for l in new_links])
+            seen.extend(new_links)
+            save_seen(username, seen)
+    if all_new:
+        send_email(config.get("email", {}), all_new)
+        send_sms(config.get("twilio", {}), all_new)
+    else:
+        print("No new posts")
+
+
+if __name__ == "__main__":
+    main()
