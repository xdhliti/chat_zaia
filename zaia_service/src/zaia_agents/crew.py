from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage import ltm_sqlite_storage
from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool, SerperDevTool, PDFSearchTool
from crewai.tasks.conditional_task import ConditionalTask
from tools.custom_tool import FReadTool
from pydantic import BaseModel, ValidationError
from typing import Optional
from mem0 import MemoryClient
import json
import re
import os

class TaskOutputModel(BaseModel):
    context: Optional[str] = None
    content: Optional[str] = None
def clean_json_string(json_str: str) -> str:
    cleaned = re.sub(r'```+', '', json_str).strip()
    return cleaned
def weather_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "climate"
    except ValidationError:
        return False

def currency_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "currency"
    except ValidationError:
        return False
def pdf_reader_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "pdf_analysis"
    except ValidationError:
        return False

def pdf_analyzer_condition(task_output) -> bool:
	try:
		raw_str = clean_json_string(task_output.raw)
		data = TaskOutputModel.model_validate_json(raw_str)
		return (data.context == "pdf_analysis") and (data.content and data.content.strip())
	except ValidationError:
		return False
    
def casual_chat_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "casual_chat"
    except ValidationError:
        return False


@CrewBase
class ZaiaAgents():
	"""ZaiaAgents crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	def __init__(self, file_path: str = None, user_id: str = None, messages: str = None):
		self.file_path = file_path
		self.user_id = user_id
		self.messages = json.loads(messages)

	@agent
	def context_extractor_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['context_extractor_agent'],
			verbose=True,
			memory=True,
			max_iter=3,
			max_retry_limit=2
		)
	@task
	def extract_context_task(self) -> Task:
		return Task(
			config=self.tasks_config['extract_context_task'],
			agent=self.context_extractor_agent()
		)
	@agent
	def weather_agent(self) -> Agent:
		web_scrape_tool = ScrapeWebsiteTool(website_url='https://www.windy.com/')
		serper_tool = SerperDevTool(
			search_url="https://google.serper.dev/search",
			n_results=3,
		)
		web_search_tool = WebsiteSearchTool()
		return Agent(
			config=self.agents_config['weather_coworker_agent'],
			verbose=True,
			tools=[web_search_tool, web_scrape_tool, serper_tool],
			cache=True,
			max_iter=3,
			max_retry_limit=2
		)
	@task
	def weather_task(self) -> ConditionalTask:
		return ConditionalTask(
			config=self.tasks_config['weather_task'],
			context=[self.extract_context_task()],
			agent=self.weather_agent(),
			condition=weather_condition
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
	@task
	def currency_task(self) -> ConditionalTask:
		return ConditionalTask(
			config=self.tasks_config['currency_task'],
			context=[self.extract_context_task()],
			agent=self.currency_agent(),
			condition=currency_condition
		)

	@agent
	def pdf_reader_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['pdf_reader_agent'],
			verbose=True,
			tools=[FReadTool(pdf_path=self.file_path), PDFSearchTool(pdf_path=self.file_path)],
			cache=True,
			memory=True,
			max_iter=3,
			max_retry_limit=2
		)
	@task
	def pdf_reader_task(self) -> ConditionalTask:
		return ConditionalTask(
			config=self.tasks_config['pdf_reader_task'],
			context=[self.extract_context_task()],
			agent=self.pdf_reader_agent(),
			condition=pdf_reader_condition
		)
	@agent
	def pdf_analyzer_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['pdf_analyzer_agent'],
			verbose=True,
			max_iter=3,
			max_retry_limit=2
		)

	@task
	def pdf_analyzer_task(self) -> ConditionalTask:
		return ConditionalTask(
			config=self.tasks_config['pdf_analyzer_task'],
			context=[self.pdf_reader_task()],
			agent=self.pdf_analyzer_agent(),
			condition=pdf_analyzer_condition
		)
	@agent
	def casual_chat_agent(self) -> Agent:
		return Agent(
            config=self.agents_config['casual_chat_agent'],
            verbose=True,
            max_iter=5,
            max_retry_limit=2
		)
      
	@task
	def casual_chat_task(self) -> ConditionalTask:
		return ConditionalTask(
			config=self.tasks_config['casual_chat_task'],
			context=[self.extract_context_task()],
			agent=self.casual_chat_agent(),
			condition=casual_chat_condition
		)
	
	@agent
	def report_to_user_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['report_to_user_agent'],
			verbose=True,
		)
	@task 
	def report_to_user_task(self) -> Task:
		return Task(
			config=self.tasks_config['report_to_user_task'],
			context=[self.weather_task(), self.currency_task(), self.pdf_analyzer_task(), self.casual_chat_task(), self.extract_context_task()],
			agent=self.report_to_user_agent(),
		)
	@crew
	def crew(self) -> Crew:
		"""Creates the ZaiaAgents crew"""

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
                },
			},
			output_log_file='reportCrew.json'
		)
