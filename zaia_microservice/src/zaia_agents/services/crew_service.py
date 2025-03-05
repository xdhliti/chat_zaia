import json
import re
import os
from typing import Optional

from pydantic import BaseModel, ValidationError
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage import ltm_sqlite_storage
from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool, SerperDevTool, PDFSearchTool
from crewai.tasks.conditional_task import ConditionalTask

from src.zaia_agents.tools.custom_tool import FReadTool

from src.zaia_agents.helpers.conditions_helper import (
    weather_condition,
    currency_condition,
    pdf_reader_condition,
    pdf_analyzer_condition,
    casual_chat_condition
)

class ZaiaAgentsConfigError(Exception):
    """Exception para casos de config faltando ou inválida"""
    pass

@CrewBase
class ZaiaAgents:
    """ZaiaAgents crew"""

    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'

    def __init__(self, file_path: str = None, user_id: str = None, messages: str = None):
        self.file_path = file_path
        self.user_id = user_id
        self.messages = json.loads(messages) if messages else []

    # ----------------------------
    # Agents
    # ----------------------------
    @agent
    def context_extractor_agent(self) -> Agent:
        try:
            config = self.agents_config['context_extractor_agent']  # se isso for um dict, etc.
        except KeyError:
            raise ZaiaAgentsConfigError("Config 'context_extractor_agent' não encontrado em agents_config.")

        return Agent(
            config=config,
            verbose=True,
            memory=True,
            max_iter=3,
            max_retry_limit=2
        )

    @agent
    def weather_agent(self) -> Agent:
        web_scrape_tool = ScrapeWebsiteTool(website_url='https://www.windy.com/')
        serper_tool = SerperDevTool(search_url="https://google.serper.dev/search", n_results=3)
        web_search_tool = WebsiteSearchTool()
        return Agent(
            config=self.agents_config['weather_coworker_agent'],
            verbose=True,
            tools=[web_search_tool, web_scrape_tool, serper_tool],
            cache=True,
            max_iter=3,
            max_retry_limit=2
        )

    @agent
    def currency_agent(self) -> Agent:
        web_scrape_tool = ScrapeWebsiteTool(website_url='https://br.investing.com/currencies/streaming-forex-rates-majors')
        web_search_tool = WebsiteSearchTool()
        return Agent(
            config=self.agents_config['currency_coworker_agent'],
            verbose=True,
            tools=[web_search_tool, web_scrape_tool],
            cache=True,
            max_iter=3,
            max_retry_limit=2
        )

    @agent
    def pdf_reader_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_reader_agent'],
            verbose=True,
            tools=[
                FReadTool(pdf_path=self.file_path),
                PDFSearchTool(pdf_path=self.file_path)
            ],
            cache=True,
            memory=True,
            max_iter=3,
            max_retry_limit=2
        )

    @agent
    def pdf_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_analyzer_agent'],
            verbose=True,
            max_iter=3,
            max_retry_limit=2
        )

    @agent
    def casual_chat_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['casual_chat_agent'],
            verbose=True,
            max_iter=5,
            max_retry_limit=2
        )

    @agent
    def report_to_user_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['report_to_user_agent'],
            verbose=True,
        )

    # ----------------------------
    # Tasks
    # ----------------------------
    @task
    def extract_context_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_context_task'],
            agent=self.context_extractor_agent()
        )

    @task
    def weather_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['weather_task'],
            context=[self.extract_context_task()],
            agent=self.weather_agent(),
            condition=weather_condition
        )

    @task
    def currency_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['currency_task'],
            context=[self.extract_context_task()],
            agent=self.currency_agent(),
            condition=currency_condition
        )

    @task
    def pdf_reader_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['pdf_reader_task'],
            context=[self.extract_context_task()],
            agent=self.pdf_reader_agent(),
            condition=pdf_reader_condition
        )

    @task
    def pdf_analyzer_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['pdf_analyzer_task'],
            context=[self.pdf_reader_task()],
            agent=self.pdf_analyzer_agent(),
            condition=pdf_analyzer_condition
        )

    @task
    def casual_chat_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['casual_chat_task'],
            context=[self.extract_context_task()],
            agent=self.casual_chat_agent(),
            condition=casual_chat_condition
        )

    @task 
    def report_to_user_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_to_user_task'],
            context=[
                self.weather_task(),
                self.currency_task(),
                self.pdf_analyzer_task(),
                self.casual_chat_task(),
                self.extract_context_task()
            ],
            agent=self.report_to_user_agent(),
        )

    # ----------------------------
    # Crew
    # ----------------------------
    @crew
    def crew(self) -> Crew:
        """Cria o Crew ZaiaAgents"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm='gpt-4o',
            verbose=True,
            language='pt-br',
            planning=True,
            memory=True,
            memory_config={
                "provider": "mem0",
                "config": {
                    "user_id": self.user_id,
                    "output_format": "v1.1"
                }
            },
            output_log_file='reportCrew.json'
        )
