# Trade Bot

A Python-based cryptocurrency trade bot using the Kraken API.

## Setup Instructions

1. **Install Python**:
   Ensure you have Python 3.8+ installed.

2. **Create a virtual environment**:
   ```bash
   cd Python
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Testing**:
   ```bash
   pytest tests/

5. **Run the bot in live mode(WARNING)**:
   ```bash
   python src/bot.py

6. **Run the bot in mock mode**:
   ```bash
   python src/bot.py --mock