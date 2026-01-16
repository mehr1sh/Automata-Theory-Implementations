# Automata Theory Implementations

Comprehensive implementations of core automata theory concepts including Hidden Markov Models for sequence prediction and a compiler front-end with lexical and syntactic analysis.

## Project Overview

This repository contains two major implementations demonstrating practical applications of automata theory:

1. **Hidden Markov Model Framework** - Statistical sequence modeling with Viterbi decoding
2. **Compiler Front-End** - Lexical tokenization and context-free grammar parsing

## Question 1: Hidden Markov Models

### Overview

Implementation of a complete Hidden Markov Model system for probabilistic sequence analysis and prediction. The system learns state transition and emission probabilities from empirical data and performs maximum a-posteriori (MAP) decoding.

### Components

#### `construct.py` - HMM Matrix Construction
- Parses labeled state-observation sequences from dataset
- Computes transition probability matrix A via frequency estimation
- Computes emission probability matrix B
- Handles arbitrary state spaces with proper normalization
- Output precision: 5 decimal places (IEEE 754 compliant)

**Usage:**
```bash
python construct.py <dataset_file>
```

**Input Format:**
```
<num_runs>
<state_sequence_1>
<observation_sequence_1>
<state_sequence_2>
<observation_sequence_2>
...
```

**Output:** Probability matrices in text format

#### `predictions.py` - Viterbi Decoding
- Implements Viterbi algorithm for maximum probability path finding
- Reconstructs most likely hidden state sequence from observations
- Handles variable-length observation sequences
- Uses dynamic programming for O(N²T) time complexity

**Usage:**
```bash
python predictions.py <input_file>
```

**Input Format:**
```
<dataset_file_for_hmm>
<num_test_cases>
<length_1>
<observations_1>
<length_2>
<observations_2>
...
```

### Implementation Details

**Mathematical Foundation:**
- Transition Matrix A: P(state_j | state_i) computed as count(i→j) / count(outgoing from i)
- Emission Matrix B: P(observation_j | state_i) computed as count(observation_j in state_i) / count(state_i)
- Viterbi: max_path = argmax Π P(state) × P(observation | state) × P(next_state | state)

**Key Features:**
- Probability matrix normalization ensures sum-to-1 constraints
- Proper handling of unseen transitions (zero probability)
- State indexing maintained for deterministic output ordering
- Numerical stability through direct probability computation (no log-space needed for these datasets)

## Question 2: Compiler Front-End

### Overview

A two-phase compiler implementation with lexical analysis and syntax analysis for a custom simple programming language. Supports if-else conditionals, expressions, and print statements with proper error classification.

### Components

#### `compiler.py` - Main Implementation
Integrated compiler with three primary classes:

**LexicalAnalyzer**
- Regex-based tokenization matching multiple token types
- Token hierarchy: Keywords > Identifiers > Numbers > Symbols
- Detects invalid identifiers, malformed numbers, unrecognized characters
- Single-pass scanning with maximal munch tokenization

**SyntaxAnalyzer**
- Recursive descent parser following grammar specification
- Validates statement sequences, conditionals, and expressions
- Operator precedence handling (binary operators left-associative)
- Lookahead parsing for optional else clauses

**CompilerEngine**
- Orchestrates lexical → syntax analysis pipeline
- File I/O handling for batch processing
- Distinction between lexical and syntax errors

### Grammar Specification

```
program         : statement_list
statement_list  : statement | statement_list statement
statement       : if_statement | simple_statement
if_statement    : if condition statement | if condition statement else statement
condition       : expression
expression      : term | term op term
term            : factor | factor op term
factor          : identifier | number | if_statement
op              : + | - | * | / | ^ | < | > | =
simple_statement: identifier | number | print | keyword
```

### Language Specification

**Token Types:**

| Type | Pattern | Examples |
|------|---------|----------|
| KEYWORD | Reserved words | if, else, print |
| IDENTIFIER | [a-zA-Z_][a-zA-Z0-9_]* | x, var_1, count |
| INTEGER | [0-9]+ | 42, 0, 1000 |
| FLOAT | [0-9]*\.[0-9]+\|[0-9]+\.* | 3.14, .5, 42.0 |
| SYMBOL | Operators and punctuation | +, -, *, /, ^, <, >, =, ; |

**Lexical Rules:**
- Identifiers cannot start with digits
- Floating-point numbers require decimal point
- Keywords take precedence over identifiers
- Whitespace separates tokens but isn't tokenized

**Syntax Rules:**
- Every if must have matching else or be standalone
- Operators require operands on both sides
- Expressions build left-to-right with operators
- Parentheses not required (simplified for assignment scope)

### Error Classification

**Lexical Errors:**
- Invalid identifier format (2xi, _-var, @name)
- Malformed numbers (1.2.3, 1., .1e)
- Invalid character sequences

**Syntax Errors:**
- else without preceding if
- Missing operands (+ x, x *, empty expressions)
- Improper statement nesting
- Type mismatches in grammar rules

### Usage

**File Processing:**
```bash
python compiler.py <input_file>
```

**Input Format:** One statement per line

**Output Format:** 
- If no errors: Token classification list
- If lexical error: `ValueError: <description>`
- If syntax error: `SyntaxError: <description>`

### Example

**Input:**
```
if 2 + x > 0 print 5 else print 10
```

**Output:**
```
Token Type: KEYWORD, Token Value: if
Token Type: INTEGER, Token Value: 2
Token Type: SYMBOL, Token Value: +
Token Type: IDENTIFIER, Token Value: x
Token Type: SYMBOL, Token Value: >
Token Type: INTEGER, Token Value: 0
Token Type: KEYWORD, Token Value: print
Token Type: INTEGER, Token Value: 5
Token Type: KEYWORD, Token Value: else
Token Type: KEYWORD, Token Value: print
Token Type: INTEGER, Token Value: 10
```

## Architecture & Design Decisions

### HMM Implementation Choices

1. **Frequency-Based Estimation** - Maximum likelihood estimation from empirical counts ensures unbiased probability estimates
2. **Matrix Format** - Dense 2D arrays for O(1) lookup despite potential sparsity (acceptable for small state spaces)
3. **Viterbi Over Forward Algorithm** - Decoding requires most probable sequence, not probability sums
4. **No Smoothing** - Zero probabilities for unseen transitions reflect true data distribution

### Compiler Design Choices

1. **Regex-Based Lexical Analysis** - Flexible, maintainable, and sufficient for this grammar complexity
2. **Recursive Descent Parser** - Natural fit for this grammar; easier to understand than table-driven approaches
3. **Single-Pass Compilation** - No AST generation; validation-focused for assignment scope
4. **Early Error Reporting** - First error stops analysis (consistent with educational compiler design)

## Complexity Analysis

### HMM
- **Matrix Construction:** O(D × L) where D = runs, L = sequence length
- **Viterbi Decoding:** O(N² × T) where N = states, T = observation sequence length
- **Space:** O(N²) for matrices, O(N × T) for DP table

### Compiler
- **Lexical Analysis:** O(n) single-pass scan over character input
- **Syntax Analysis:** O(m) where m = token count (linear in grammar depth)
- **Overall:** O(n) character processing + O(m) token processing

## Testing

Both components include built-in file I/O:
- HMM: Outputs probability matrices for verification
- Compiler: Produces classification or error messages

Validate against provided autograders through:
1. Matrix precision comparison (5 decimal places)
2. Token sequence correctness
3. Error classification accuracy

## Future Enhancements

**HMM Extensions:**
- Forward-backward algorithm for probability computation
- Baum-Welch for unsupervised parameter learning
- Hidden state annotation with confidence scores
- Performance optimization with sparse matrices

**Compiler Extensions:**
- Semantic analysis and type checking
- Symbol table construction
- Abstract Syntax Tree (AST) generation
- Code generation for simple bytecode
- Error recovery and multiple error reporting

