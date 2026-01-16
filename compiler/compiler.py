import sys
import os
import re

class LexicalAnalyzer:
    """Handles tokenization with a completely different approach using regex patterns"""
    
    def init(self):
        # Define token patterns using regex
        self.patterns = [
            ('WHITESPACE', r'[ \t]+'),
            ('KEYWORD_IF', r'\bif\b'),
            ('KEYWORD_ELSE', r'\belse\b'), 
            ('KEYWORD_PRINT', r'\bprint\b'),
            ('FLOAT_NUM', r'\d*\.\d+|\d+\.\d*'),
            ('INTEGER_NUM', r'\d+'),
            ('IDENTIFIER_TOKEN', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERATOR_SYMBOL', r'[+\-*/^<>=!&|%]'),
            ('OTHER_SYMBOL', r'[.;(),:@#$~`?\\{}\[\]]'),
        ]
        
        self.reserved_words = {'if', 'else', 'print'}
    
    def scan_input(self, source_text):
        """Main tokenization method using a different scanning approach"""
        token_list = []
        line_position = 0
        
        while line_position < len(source_text):
            match_found = False
            
            # Try each pattern
            for pattern_name, pattern_regex in self.patterns:
                compiled_pattern = re.compile(pattern_regex)
                match_result = compiled_pattern.match(source_text, line_position)
                
                if match_result:
                    matched_text = match_result.group(0)
                    
                    if pattern_name != 'WHITESPACE':  # Skip whitespace tokens
                        # Special handling for different token types
                        if pattern_name == 'IDENTIFIER_TOKEN':
                            if matched_text in self.reserved_words:
                                token_list.append(('KEYWORD', matched_text))
                            else:
                                # Check for invalid identifier patterns
                                if self._is_invalid_identifier(matched_text, source_text, line_position):
                                    raise Exception(f"Invalid token: {matched_text}")
                                token_list.append(('IDENTIFIER', matched_text))
                        elif pattern_name.startswith('KEYWORD_'):
                            token_list.append(('KEYWORD', matched_text))
                        elif pattern_name == 'INTEGER_NUM':
                            # Check if number is followed by letter
                            next_pos = match_result.end()
                            if next_pos < len(source_text) and source_text[next_pos].isalpha():
                                raise Exception("Number followed by letter")
                            token_list.append(('NUMBER', matched_text))
                        elif pattern_name == 'FLOAT_NUM':
                            token_list.append(('NUMBER', matched_text))
                        else:
                            token_list.append(('SYMBOL', matched_text))
                    
                    line_position = match_result.end()
                    match_found = True
                    break
            
            if not match_found:
                raise Exception(f"Unrecognized character: {source_text[line_position]}")
        
        return token_list
    
    def _is_invalid_identifier(self, identifier, full_text, position):
        """Check for various invalid identifier patterns"""
        # Check if identifier starts with digit (should be caught earlier but double-check)
        if identifier[0].isdigit():
            return True
        return False

class SyntaxAnalyzer:
    """Handles syntax analysis with a different parsing strategy"""
    
    def init(self, tokens):
        self.token_stream = tokens
        self.current_index = 0
    
    def validate_syntax(self):
        """Main syntax validation using recursive descent parsing"""
        if not self.token_stream:
            return "No Error"
        
        try:
            self._analyze_statement_sequence()
            return "No Error"
        except SyntaxException as e:
            return "Syntax Error"
    
    def _current_token(self):
        """Get current token without consuming it"""
        if self.current_index < len(self.token_stream):
            return self.token_stream[self.current_index]
        return None
    
    def _consume_token(self):
        """Consume and return current token"""
        if self.current_index < len(self.token_stream):
            token = self.token_stream[self.current_index]
            self.current_index += 1
            return token
        return None
    
    def _analyze_statement_sequence(self):
        """Parse sequence of statements"""
        while self.current_index < len(self.token_stream):
            self._parse_single_statement()
    
    def _parse_single_statement(self):
        """Parse individual statement with different logic"""
        current = self._current_token()
        
        if not current:
            return
        
        token_type, token_value = current
        
        if token_type == 'KEYWORD':
            if token_value == 'if':
                self._handle_conditional_statement()
            elif token_value == 'else':
                # Standalone else is error
                raise SyntaxException("Unexpected else")
            elif token_value == 'print':
                self._handle_print_statement()
        elif token_type in ['IDENTIFIER', 'NUMBER']:
            self._handle_expression_statement()
        elif token_type == 'SYMBOL':
            # Standalone symbols are generally errors
            if token_value in '+-*/^<>=':
                raise SyntaxException("Unexpected operator")
            self._consume_token()  # Other symbols might be valid
        else:
            self._consume_token()
    
    def _handle_conditional_statement(self):
        """Handle if-else constructs with different parsing approach"""
        self._consume_token()  # consume 'if'
        
        # Parse condition
        self._parse_condition_expression()
        
        # Parse then-statement
        self._parse_single_statement()
        
        # Check for else clause
        current = self._current_token()
        if current and current[0] == 'KEYWORD' and current[1] == 'else':
            self._consume_token()  # consume 'else'
            self._parse_single_statement()
    
    def _handle_print_statement(self):
        """Handle print statements"""
        self._consume_token()  # consume 'print'
        # Could add more print-specific parsing here
    
    def _handle_expression_statement(self):
        """Handle expression statements"""
        self._parse_expression()
    
    def _parse_condition_expression(self):
        """Parse conditional expressions"""
        self._parse_expression()
    
    def _parse_expression(self):
        """Parse expressions with operator precedence"""
        self._parse_primary()
        
        while True:
            current = self._current_token()
            if current and current[0] == 'SYMBOL' and current[1] in '+-*/^<>=':
                self._consume_token()  # consume operator
                self._parse_primary()
            else:
                break
    
    def _parse_primary(self):
        """Parse primary expressions (identifiers, numbers)"""
        current = self._current_token()
        
        if not current:
            raise SyntaxException("Unexpected end of input")
        
        token_type, token_value = current
        
        if token_type in ['IDENTIFIER', 'NUMBER']:
            self._consume_token()
        elif token_type == 'KEYWORD' and token_value == 'if':
            # Nested if in expression context
            self._handle_conditional_statement()
        else:
            raise SyntaxException(f"Unexpected token: {token_value}")

class SyntaxException(Exception):
    """Custom exception for syntax errors"""
    pass

class CompilerEngine:
    """Main compiler class with different architecture"""
    
    def init(self):
        self.lexer = LexicalAnalyzer()
    
    def process_source_line(self, source_line):
        """Process a single line of source code"""
        try:
            # Tokenization phase
            tokens = self.lexer.scan_input(source_line)
            
            # Syntax analysis phase
            parser = SyntaxAnalyzer(tokens)
            result = parser.validate_syntax()
            
            return result
            
        except Exception as e:
            # Any exception during tokenization is lexical error
            return "Lexical Error"

def process_input_file(file_path):
    """Process input file and generate output"""
    compiler = CompilerEngine()
    output_lines = []
    
    try:
        with open(file_path, 'r') as input_file:
            for line in input_file:
                cleaned_line = line.rstrip('\n')
                
                if not cleaned_line.strip():
                    output_lines.append("No Error")
                else:
                    result = compiler.process_source_line(cleaned_line)
                    output_lines.append(result)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return
    
    # Generate output file
    base_name = os.path.splitext(file_path)[0]
    output_file_path = f"{base_name}_output.txt"
    
    with open(output_file_path, 'w') as output_file:
        for line in output_lines:
            output_file.write(line + '\n')

def main():
    """Main entry point with different command line handling"""
    if len(sys.argv) != 2:
        print("Usage: python q2.py <input_file>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    process_input_file(input_file_path)

if __name__ == "main":
    main()
