from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai_tools import FileReadTool
import json
import os
from typing import Dict, Any
from datetime import date, datetime

from gmail_crew_ai.tools.gmail_tools import (
    GetUnreadEmailsTool,
    SaveDraftTool,
    GmailOrganizeTool,
    GmailDeleteTool,
    EmptyTrashTool
)
from gmail_crew_ai.tools.slack_tool import SlackNotificationTool
from gmail_crew_ai.models import (
    OrganizedEmail,
    EmailResponse,
    SlackNotification,
    EmailCleanupInfo,
    SimpleCategorizedEmail,
    EmailDetails
)

@CrewBase
class GmailCrewAi():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # ✅ FORCE OLLAMA ONLY
    llm = LLM(
        model="ollama/llama3",
        base_url="http://localhost:11434",
        provider="ollama",
        temperature=0.3
    )

    @before_kickoff
    def fetch_emails(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print("Fetching emails...")

        email_limit = inputs.get('email_limit', 5)
        os.makedirs("output", exist_ok=True)

        email_tool = GetUnreadEmailsTool()
        email_tuples = email_tool._run(limit=email_limit)

        emails = []
        today = date.today()

        for email_tuple in email_tuples:
            email_detail = EmailDetails.from_email_tuple(email_tuple)

            if email_detail.date:
                try:
                    email_date_obj = datetime.strptime(email_detail.date, "%Y-%m-%d").date()
                    email_detail.age_days = (today - email_date_obj).days
                except:
                    email_detail.age_days = None

            emails.append(email_detail.dict())

        with open('output/fetched_emails.json', 'w') as f:
            json.dump(emails, f, indent=2)

        return inputs

    # ------------------ AGENTS ------------------

    @agent
    def categorizer(self) -> Agent:
        return Agent(
            config=self.agents_config['categorizer'],
            tools=[FileReadTool()],
            llm=self.llm
        )

    @agent
    def organizer(self) -> Agent:
        return Agent(
            config=self.agents_config['organizer'],
            tools=[GmailOrganizeTool(), FileReadTool()],
            llm=self.llm
        )

    @agent
    def response_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['response_generator'],
            tools=[SaveDraftTool()],
            llm=self.llm
        )

    @agent
    def notifier(self) -> Agent:
        return Agent(
            config=self.agents_config['notifier'],
            tools=[SlackNotificationTool()],
            llm=self.llm
        )

    @agent
    def cleaner(self) -> Agent:
        return Agent(
            config=self.agents_config['cleaner'],
            tools=[GmailDeleteTool(), EmptyTrashTool()],
            llm=self.llm
        )

    # ------------------ TASKS ------------------

    @task
    def categorization_task(self) -> Task:
        return Task(
            config=self.tasks_config['categorization_task'],
            output_pydantic=SimpleCategorizedEmail
        )

    @task
    def organization_task(self) -> Task:
        return Task(
            config=self.tasks_config['organization_task'],
            output_pydantic=OrganizedEmail
        )

    @task
    def response_task(self) -> Task:
        return Task(
            config=self.tasks_config['response_task'],
            output_pydantic=EmailResponse
        )

    @task
    def notification_task(self) -> Task:
        return Task(
            config=self.tasks_config['notification_task'],
            output_pydantic=SlackNotification
        )

    @task
    def cleanup_task(self) -> Task:
        return Task(
            config=self.tasks_config['cleanup_task'],
            output_pydantic=EmailCleanupInfo
        )

    # ------------------ CREW ------------------

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,

            # 🔥 CRITICAL FIXES
            memory=False,
            cache=False,
            max_rpm=None
        )