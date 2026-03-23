📧 Gmail Automation with CrewAI

AI-powered tool to automatically manage your Gmail — categorize emails, assign priority, generate replies, and clean your inbox.

🚀 Features
📋 Email categorization
🔔 Priority detection
💬 Auto reply drafts
🏷️ Labels & organization
🧹 Inbox cleanup
🔔 Slack notifications
⚙️ Setup
git clone https://github.com/sankalppanchabhai123/Email-Workflow-Automation.git
cd crewai-gmail-automation
python -m venv .venv
.venv\Scripts\activate
crewai install

Create .env file:

MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=your_api_key
EMAIL_ADDRESS=your_email@gmail.com
APP_PASSWORD=your_app_password
▶️ Run
crewai run