import os
from dotenv import load_dotenv
from crewai import Crew, Task, Process
from config.agent_config import AgentConfig
from agents.code_explorer import CodeExplorer
from typing import List
import re

class CodebaseAssistant:
    def __init__(self, project_path: str):
        load_dotenv()
        self.project_path = project_path
        self.agent_config = AgentConfig()
        self.code_explorer = CodeExplorer(project_path)
        self.setup_crew()

    def setup_crew(self):
        """Initialize the crew with specialized agents."""
        self.crew = Crew(
            agents=[
                self.agent_config.create_code_explorer(),
                self.agent_config.create_architecture_expert(),
                self.agent_config.create_dependency_analyzer()
            ],
            process=Process.sequential,
        )

    def ask_question(self, question: str):
        """Process a developer's question about the codebase."""
        
        # First search for relevant code using the code explorer
        relevant_code = self.code_explorer.search_code(question)
        
        if not relevant_code:
            return "No relevant code found in the project for your query. Please try a different question."
        
        # Create more detailed context with file relationships
        code_context = "\n\nDetailed Code Analysis:\n"
        for idx, result in enumerate(relevant_code, 1):
            code_context += f"\n{idx}. File: {result['file']} "
            code_context += f"(Line {result['line_number']})\n"
            
            # Add import analysis
            imports = self._extract_file_imports(result['file'])
            if imports:
                code_context += "Dependencies:\n"
                for imp in imports:
                    code_context += f"- Imports from: {imp}\n"
            
            if result.get('context'):
                code_context += f"Implementation Context:\n{result['context']}"
            code_context += "```python\n"
            code_context += f"{result['content']}\n"
            code_context += "```\n"

        task = Task(
            description=f"""
            Performing deep technical analysis of code from {self.project_path}.
            Question: {question}
            {code_context}

            Provide a comprehensive low-level analysis of the implementation:

            1. Code Structure and Flow:
               - Analyze the exact implementation patterns used
               - Explain the control flow and execution path
               - Detail any async/sync operations and their handling
               - Identify key algorithms and their complexity
               - Examine error handling and edge cases

            2. Data Flow Analysis:
               - Track how data moves through the components
               - Identify state management patterns
               - Analyze data transformations and processing
               - Examine input validation and sanitization
               - Detail the data lifecycle

            3. Dependencies and Integration:
               - Map all internal and external dependencies
               - Explain how components communicate
               - Analyze coupling between components
               - Identify potential bottlenecks
               - Detail the integration patterns used

            4. Technical Implementation Details:
               - Examine memory usage and performance implications
               - Analyze any caching or optimization strategies
               - Detail the security measures implemented
               - Identify potential technical debt
               - Analyze scalability considerations

            5. Framework-Specific Patterns:
               - Detail how framework features are utilized
               - Analyze component lifecycle management
               - Examine framework-specific optimizations
               - Detail any custom framework extensions

            Reference specific:
            - File names and exact line numbers
            - Function and method implementations
            - Variable usage and scope
            - Design patterns and their implementation
            - Framework-specific features used

            Focus on concrete implementation details, not abstract concepts.
            Explain WHY certain patterns or approaches were chosen.
            """,
            expected_output="""
            A detailed technical analysis including:
            - Low-level implementation details
            - Data and control flow analysis
            - Component interactions and dependencies
            - Performance and optimization considerations
            - Framework-specific implementation patterns
            - Concrete examples with file and line references
            """,
            agent=self.crew.agents[0]
        )

        self.crew.tasks = [task]
        result = self.crew.kickoff()
        return result

    def _extract_file_imports(self, file_path: str) -> List[str]:
        """Extract imports from a file to understand dependencies."""
        imports = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Match different import patterns
            import_patterns = [
                r'import\s+{[^}]+}\s+from\s+[\'"]([^\'"]+)[\'"]',  # ES6 imports
                r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',    # Default imports
                r'from\s+[\'"]([^\'"]+)[\'"]',                     # Python imports
                r'require\([\'"]([^\'"]+)[\'"]\)',                 # CommonJS
                r'@import\s+[\'"]([^\'"]+)[\'"]'                   # SCSS/CSS imports
            ]
            
            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    imports.append(match.group(1))
                    
        except Exception as e:
            print(f"Error analyzing imports in {file_path}: {e}")
        
        return list(set(imports))  # Remove duplicates

def main():
    # Get project path from user
    project_path = input("Enter the path to your project: ")
    
    if not os.path.exists(project_path):
        print("Invalid project path!")
        return

    # Initialize the assistant
    assistant = CodebaseAssistant(project_path)
    
    # Interactive loop
    while True:
        question = input("\nAsk a question about the codebase (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
            
        response = assistant.ask_question(question)
        print("\nResponse:", response)

if __name__ == "__main__":
    main() 