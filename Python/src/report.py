import os
from datetime import datetime, timedelta
import pandas as pd
from notifier import send_email

def generate_html_report(log_file='trade_bot.log'):
    try:
        # Read the log file
        with open(log_file, 'r') as file:
            lines = file.readlines()

        # Parse log data into a DataFrame
        data = []
        for line in lines:
            parts = line.split(' - ')
            if len(parts) >= 3:
                timestamp, level, message = parts[0], parts[1], parts[2]
                if "BUY" in message or "SELL" in message:
                    action, details = message.split(' - ')[0], message.split(' - ')[1]
                    price = details.split('Price: ')[1].split()[0]
                    data.append([timestamp, action, price])

        df = pd.DataFrame(data, columns=["Timestamp", "Type", "Price (USD)"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

        # Generate report for the last 24 hours
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        df_24h = df[df["Timestamp"] >= yesterday]

        # Calculate net change
        net_change = df_24h["Price (USD)"].astype(float).sum()

        # Create HTML table
        html_table = df_24h.to_html(index=False, border=0)

        # Build the email content
        html_content = f"""
        <html>
        <body>
            <h1>24-Hour Trade Report</h1>
            {html_table}
            <h3>Net Change: {net_change:.2f} USD</h3>
        </body>
        </html>
        """

        # Send the report via email
        send_email("Daily Trade Report", html_content)
    except Exception as e:
        print(f"Error generating report: {e}")
