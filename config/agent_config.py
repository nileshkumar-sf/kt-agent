import os
from crewai import Agent, LLM

class AgentConfig:
    def __init__(self):
        # Initialize Gemini LLM through Crew.ai's integration
        self.llm = LLM(
            model="gemini/gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def create_code_explorer(self):
        return Agent(
            role='Code Explorer',
            goal='Analyze and explain code structure and functionality',
            backstory="""You are an expert code analyzer with deep understanding of 
            software architecture and patterns. Your role is to help developers 
            understand specific parts of the codebase.""",
            verbose=True,
            llm=self.llm
        )

    def create_architecture_expert(self):
        return Agent(
            role='Architecture Expert',
            goal='Explain system architecture and component relationships',
            backstory="""You are a software architect with expertise in designing 
            and explaining complex systems. You help developers understand the 
            high-level architecture and design patterns.""",
            verbose=True,
            llm=self.llm
        )

    def create_dependency_analyzer(self):
        return Agent(
            role='Dependency Analyzer',
            goal='Analyze and explain project dependencies and relationships',
            backstory="""You are an expert in understanding project dependencies,
            import relationships, and module interactions. You help developers 
            understand how different parts of the system connect.""",
            verbose=True,
            llm=self.llm
        ) 