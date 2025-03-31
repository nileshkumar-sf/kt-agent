import os
from typing import List, Dict, Set
from pathlib import Path
from fnmatch import fnmatch
import re
from collections import Counter

class CodeExplorer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.file_contents: Dict[str, str] = {}
        self.ignored_patterns = self._load_gitignore()
        self.project_type = self._detect_project_type()
        self.framework_patterns = self._get_framework_patterns()
        self.load_codebase()

    def _load_gitignore(self) -> List[str]:
        """Load .gitignore patterns from the project root."""
        gitignore_path = os.path.join(self.project_path, '.gitignore')
        ignored = [
            # Build and dependency directories
            'node_modules',
            'dist',
            'build',
            'out',
            '.next',
            
            # Python specific
            '__pycache__',
            '*.pyc',
            'venv',
            '.env',
            '*.egg-info',
            
            # Assets and media
            'assets',
            'images',
            'media',
            '*.jpg',
            '*.jpeg',
            '*.png',
            '*.gif',
            '*.svg',
            '*.ico',
            '*.pdf',
            
            # IDE and editor files
            '.idea',
            '.vscode',
            '.DS_Store',
            
            # Package files
            'package-lock.json',
            'yarn.lock',
            
            # Log and cache files
            'logs',
            '*.log',
            '.cache',
            
            # Test coverage
            'coverage',
            '.coverage',
            
            # Documentation
            'docs',
            '*.md',
            
            # Config files
            '*.config.js',
            '*.conf',
            '*.lock'
        ]
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignored.append(line)
        
        return ignored

    def _is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored based on .gitignore patterns."""
        rel_path = os.path.relpath(path, self.project_path)
        
        # Check each pattern
        for pattern in self.ignored_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if fnmatch(rel_path + '/', pattern + '*'):
                    return True
            # Handle file patterns
            elif fnmatch(rel_path, pattern):
                return True
            # Handle patterns without slashes as both file and directory patterns
            elif '/' not in pattern and fnmatch(os.path.basename(rel_path), pattern):
                return True
        
        return False

    def _detect_project_type(self) -> str:
        """Detect the type of project based on config files and structure."""
        # Check for Angular
        if os.path.exists(os.path.join(self.project_path, 'angular.json')):
            return 'angular'
        # Check for React
        elif os.path.exists(os.path.join(self.project_path, 'package.json')):
            try:
                with open(os.path.join(self.project_path, 'package.json')) as f:
                    import json
                    package = json.load(f)
                    if 'dependencies' in package:
                        if '@angular' in package['dependencies']:
                            return 'angular'
                        elif 'react' in package['dependencies']:
                            return 'react'
                        elif 'vue' in package['dependencies']:
                            return 'vue'
            except:
                pass
        return 'unknown'

    def _get_framework_patterns(self) -> Dict:
        """Get framework-specific patterns based on project type."""
        patterns = {
            'angular': {
                'file_types': ('.ts', '.html'),
                'component_patterns': [
                    r'@Component\s*\(\s*{[^}]*}\s*\)',
                    r'@Injectable\s*\(\s*{[^}]*}\s*\)',
                    r'@Directive\s*\(\s*{[^}]*}\s*\)',
                    r'@Pipe\s*\(\s*{[^}]*}\s*\)',
                    r'@NgModule\s*\(\s*{[^}]*}\s*\)',
                ],
                'service_patterns': [
                    r'class\s+\w+Service',
                    r'constructor\s*\([^)]*\)',
                    r'@Injectable',
                ],
                'template_patterns': [
                    r'\*ngFor',
                    r'\*ngIf',
                    r'\[(ngModel)\]',
                    r'\(click\)',
                    r'{{[^}]*}}',
                ],
                'module_patterns': [
                    r'imports\s*:',
                    r'declarations\s*:',
                    r'providers\s*:',
                    r'exports\s*:',
                ],
                'routing_patterns': [
                    r'RouterModule',
                    r'Routes',
                    r'@RouteConfig',
                ]
            },
            'react': {
                'file_types': ('.jsx', '.tsx', '.js', '.ts'),
                # Add React patterns here
            },
            'vue': {
                'file_types': ('.vue', '.js', '.ts'),
                # Add Vue patterns here
            },
            'unknown': {
                'file_types': ('.ts', '.html'),
                'component_patterns': [],
                'service_patterns': [],
                'template_patterns': [],
                'module_patterns': [],
                'routing_patterns': []
            }
        }
        return patterns[self.project_type]

    def load_codebase(self):
        """Load all code files from the project directory."""
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            for file in files:
                if file.endswith(self.framework_patterns['file_types']):
                    file_path = os.path.join(root, file)
                    
                    if self._is_ignored(file_path):
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.file_contents[file_path] = f.read()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    def _get_stop_words(self) -> Set[str]:
        """Common English words to ignore in search."""
        return {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
            'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
            'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
            'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
            'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been',
            'has', 'had', 'where', 'why', 'who', 'which', 'what', 'explain',
            'tell', 'show', 'find', 'help', 'need', 'using', 'used', 'done'
        }

    def _extract_technical_terms(self, query: str) -> List[str]:
        """Extract technical terms and code patterns from query."""
        # Common code-related patterns
        code_patterns = {
            r'\w+\(\)',  # Function calls
            r'\w+\.\w+',  # Method/property access
            r'[A-Z]\w+',  # CamelCase class names
            r'\w+_\w+',  # snake_case names
            r'[a-z]+[A-Z]\w*',  # camelCase names
            r'<\w+>',  # Generic types
            r'\w+\[\w+\]',  # Array/generic syntax
            r'@\w+',  # Decorators
            r'\$\w+',  # Special variables
            r'#\w+',  # Hash references
            r'`[^`]+`',  # Code in backticks
        }
        
        terms = []
        
        # Extract terms matching code patterns
        for pattern in code_patterns:
            matches = re.findall(pattern, query)
            terms.extend(matches)
        
        # Split remaining text into words
        words = re.findall(r'\b\w+\b', query)
        
        return list(set(terms + words))

    def search_code(self, query: str) -> List[Dict]:
        """Search for relevant code snippets with deep analysis."""
        stop_words = self._get_stop_words()
        search_terms = set(
            term.lower() for term in self._extract_technical_terms(query) 
            if len(term) > 2 and term.lower() not in stop_words
        )
        
        if not search_terms:
            return []

        # Add framework-specific search context
        if self.project_type == 'angular':
            # If query mentions component/service/module, prioritize those patterns
            if 'component' in query.lower():
                patterns = self.framework_patterns['component_patterns']
            elif 'service' in query.lower():
                patterns = self.framework_patterns['service_patterns']
            elif 'module' in query.lower():
                patterns = self.framework_patterns['module_patterns']
            elif 'template' in query.lower() or 'html' in query.lower():
                patterns = self.framework_patterns['template_patterns']
            elif 'routing' in query.lower():
                patterns = self.framework_patterns['routing_patterns']
            else:
                patterns = []
                for key in ['component_patterns', 'service_patterns', 'template_patterns', 
                           'module_patterns', 'routing_patterns']:
                    patterns.extend(self.framework_patterns[key])

        relevant_files = {}
        for file_path, content in self.file_contents.items():
            content_lower = content.lower()
            file_name = os.path.basename(file_path).lower()
            
            # Framework-specific scoring
            framework_score = 0
            if self.project_type == 'angular':
                # Higher score for matching file types
                if file_name.endswith('.component.ts'):
                    framework_score += 10
                elif file_name.endswith('.service.ts'):
                    framework_score += 8
                elif file_name.endswith('.module.ts'):
                    framework_score += 6
                
                # Check for framework patterns
                for pattern in patterns:
                    if re.search(pattern, content):
                        framework_score += 5

            scores = {
                'filename_exact': sum(20 for term in search_terms if term in file_name.split('.')),
                'filename_partial': sum(5 for term in search_terms if term in file_name),
                'content_matches': [],
                'technical_score': framework_score
            }
            
            lines = content.split('\n')
            
            # Analyze each line
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Check for technical patterns
                if any(re.search(pattern, line) for pattern in [
                    r'class\s+\w+',
                    r'def\s+\w+',
                    r'function\s+\w+',
                    r'import\s+\w+',
                    r'from\s+\w+\s+import',
                    r'require\(',
                    r'export\s+',
                    r'@\w+',
                ]):
                    scores['technical_score'] += 5
                
                # Find term matches
                term_matches = [term for term in search_terms if term in line_lower]
                if term_matches:
                    scores['content_matches'].append({
                        'line_num': i,
                        'terms': term_matches,
                        'line': line,
                        'is_technical': bool(re.search(r'(class|def|function|import|export|require|@)\s+\w+', line))
                    })
            
            # Enhanced technical analysis
            technical_analysis = {
                'patterns': self._analyze_patterns(content),
                'complexity': self._analyze_complexity(content),
                'dependencies': self._analyze_dependencies(content),
                'data_flow': self._analyze_data_flow(content)
            }

            scores['technical_score'] += (
                len(technical_analysis['patterns']) * 2 +
                technical_analysis['complexity']['score'] +
                len(technical_analysis['dependencies']) * 3 +
                len(technical_analysis['data_flow']) * 2
            )
            
            # Calculate final score
            total_score = (
                scores['filename_exact'] +
                scores['filename_partial'] +
                len(scores['content_matches']) * 2 +
                scores['technical_score']
            )
            
            if total_score > 0:
                relevant_files[file_path] = {
                    'scores': scores,
                    'total_score': total_score,
                    'lines': lines,
                    'technical_analysis': technical_analysis
                }
        
        # Process top relevant files
        results = []
        top_files = dict(sorted(
            relevant_files.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )[:3])
        
        for file_path, data in top_files.items():
            matches = data['scores']['content_matches']
            lines = data['lines']
            
            # Group nearby matches
            for match in matches:
                start_line = max(0, match['line_num'] - 5)
                end_line = min(len(lines), match['line_num'] + 6)
                
                context_info = self._get_better_context(lines, match['line_num'])
                relevant_section = '\n'.join(lines[start_line:end_line])
                
                results.append({
                    'file': file_path,
                    'content': relevant_section,
                    'context': context_info,
                    'relevance': data['total_score'],
                    'line_number': match['line_num'] + 1,
                    'matched_terms': match['terms'],
                    'is_technical_match': match['is_technical']
                })
        
        # Sort by relevance and technical matches
        return sorted(
            results,
            key=lambda x: (x['relevance'], x['is_technical_match']),
            reverse=True
        )

    def _get_better_context(self, lines: List[str], current_line: int) -> str:
        """Improved context finder that looks for class/function definitions."""
        context = []
        
        # Look up for class/function definitions
        for i in range(current_line, -1, -1):
            line = lines[i].strip()
            
            # Check for class or function definitions
            if line.startswith(('def ', 'class ', 'async def ')):
                context.append(line)
                # If we found a class, look for its methods too
                if line.startswith('class '):
                    for j in range(i + 1, current_line):
                        if lines[j].strip().startswith(('def ', 'async def ')):
                            context.append('  ' + lines[j].strip())
                break
            
            # Stop if we hit another major block
            if line and not line.startswith((' ', '\t')):
                break
        
        return '\n'.join(context) + '\n' if context else ""

    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score of content for the given query."""
        # Simple relevance calculation based on term frequency
        return content.lower().count(query.lower()) / len(content)

    def _analyze_patterns(self, content: str) -> List[Dict]:
        """Analyze implementation patterns in the code."""
        patterns = []
        pattern_definitions = {
            'singleton': r'private\s+static\s+\w+\s+instance',
            'factory': r'create\w+|factory',
            'observer': r'subscribe|observer|addEventListener',
            'dependency_injection': r'constructor\s*\([^)]+\)',
            'decorator': r'@\w+',
            'async_pattern': r'async|await|Promise|Observable'
        }
        
        for pattern_name, pattern in pattern_definitions.items():
            if re.search(pattern, content):
                patterns.append({
                    'name': pattern_name,
                    'locations': [m.start() for m in re.finditer(pattern, content)]
                })
        
        return patterns

    def _analyze_complexity(self, content: str) -> Dict:
        """Analyze code complexity."""
        analysis = {
            'cyclomatic': 0,
            'cognitive': 0,
            'score': 0
        }
        
        # Count control structures
        control_structures = len(re.findall(
            r'\b(if|else|for|while|do|switch|case|catch)\b', 
            content
        ))
        
        # Count nested structures
        nested_depth = 0
        max_depth = 0
        for line in content.split('\n'):
            if re.search(r'{|\(|\[', line):
                nested_depth += 1
                max_depth = max(max_depth, nested_depth)
            if re.search(r'}|\)|\]', line):
                nested_depth -= 1
        
        analysis['cyclomatic'] = control_structures + 1
        analysis['cognitive'] = control_structures + max_depth
        analysis['score'] = (analysis['cyclomatic'] + analysis['cognitive']) // 2
        
        return analysis

    def _analyze_dependencies(self, content: str) -> List[Dict]:
        """Analyze code dependencies."""
        dependencies = []
        
        # Analyze imports
        import_matches = re.finditer(
            r'import\s+{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]|'
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]|'
            r'require\([\'"]([^\'"]+)[\'"]\)',
            content
        )
        
        for match in import_matches:
            if match.group(1):  # Named imports
                imports = [imp.strip() for imp in match.group(1).split(',')]
                source = match.group(2)
            elif match.group(3):  # Default import
                imports = [match.group(3)]
                source = match.group(4)
            else:  # Require
                imports = ['*']
                source = match.group(5)
            
            dependencies.append({
                'type': 'import',
                'source': source,
                'imports': imports
            })
        
        return dependencies

    def _analyze_data_flow(self, content: str) -> List[Dict]:
        """Analyze data flow in the code."""
        data_flows = []
        
        # Analyze state management
        state_patterns = [
            (r'this\.(\w+)\s*=', 'class_property'),
            (r'useState\([^)]*\)', 'react_state'),
            (r'new\s+Subject\([^)]*\)', 'rxjs_subject'),
            (r'@Input\([^)]*\)', 'angular_input'),
            (r'@Output\([^)]*\)', 'angular_output')
        ]
        
        for pattern, flow_type in state_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                data_flows.append({
                    'type': flow_type,
                    'location': match.start(),
                    'variable': match.group(1) if flow_type == 'class_property' else None
                })
        
        return data_flows 