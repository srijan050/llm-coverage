<img width="213" alt="image" src="https://github.com/user-attachments/assets/2675a383-3c10-471a-a062-bc18ad4efeef" />


# LLM-Coverage: Large Language Model-Driven Hardware Coverage Generation

**A comprehensive framework that leverages Large Language Models (LLMs) to automatically generate test stimuli for achieving functional coverage in hardware verification. This project is tested on multiple Design Under Test (DUT) configurations and provides an intelligent, iterative approach to coverage-driven verification.**

## Overview

This repository implements an LLM-based agent system that generates targeted test stimuli to maximize functional coverage for hardware designs. The system uses intelligent prompt generation, stimulus extraction, and coverage feedback loops to efficiently explore the design space and hit coverage bins. The project addresses the critical challenge of generating effective test stimuli to achieve maximum coverage of predefined test bins, making verification processes more efficient and cost-effective.

The framework implements a sophisticated client-server architecture where LLMs generate test stimuli based on coverage feedback, enabling adaptive and intelligent test generation.

## Project Structure

```
llm-coverage/
├── agents/                    # LLM agent implementations
├── models/                    # LLM model integrations (GPT, Llama)
├── prompt_generators/         # Prompt generation strategies
├── loggers/                   # Logging and data collection
├── stride_detector/           # Stride Detector DUT
├── ibex_cpu/                  # Ibex CPU DUT 
├── ibex_decoder/              # Ibex Decoder DUT
├── examples_SD/               # Stride Detector examples
├── examples_IC/               # Ibex CPU examples
├── examples_ID/               # Ibex Decoder examples
├── examples_SD_analogue/      # Additional SD examples
├── stimuli_extractor.py       # Extract stimuli from LLM responses
├── stimuli_filter.py          # Filter and validate stimuli
├── csv_helper.py              # CSV utility functions
└── global_shared_types.py     # Shared type definitions

```

<img width="213" alt="image" src="https://github.com/user-attachments/assets/2e38ce1c-6e8b-4ae9-af64-abf10029299f" />

<img width="534" alt="image" src="https://github.com/user-attachments/assets/a4141bb5-f9f2-4345-b97c-8ab17bb1f558" />



## Architecture and Core Components

### Client-Server Model

The framework operates on a client-server architecture designed for scalability and modularity :

- **Server Side**: Runs hardware simulations using Cocotb testbenches, computes coverage metrics, and returns DUT state information
- **Client Side**: Generates intelligent stimuli using LLM agents and sends them to the server for evaluation

### LLM Agent Architecture

The core innovation lies in the sophisticated LLM agent implementation, which consists of five interconnected components :

#### 1. Prompt Generator
Responsible for creating system messages, initial queries, and iterative queries using various templates tailored to different Device Under Test (DUT) types. This component implements "Missed-bin sampling" methodologies to focus on uncovered test cases.

#### 2. Stimulus Generator (LLM Core)
The heart of the system, utilizing state-of-the-art language models including OpenAI's GPT models and Siemens' in-house hosted Llama 3. This component implements sophisticated conversation management and iterative message sampling strategies.

#### 3. Stimulus Extractor
Processes LLM text responses to extract numerical values that can be used as test stimuli.

#### 4. Stimulus Filter
Validates and filters extracted stimuli to ensure they meet design constraints and are suitable for testing.

#### 5. Comprehensive Logging System
Tracks prompts, responses, coverage metrics, and experimental data across multiple trials for analysis and reproducibility.

### Intelligent Dialogue Management

The system implements sophisticated dialogue restarting strategies to prevent convergence and maintain exploration effectiveness. Multiple restart plans are available, including tolerance-based and coverage-rate-based strategies.

<img width="1261" alt="image" src="https://github.com/user-attachments/assets/f8d141c5-d023-4d3d-8c94-6c31c6be8434" />


## Design Under Test (DUT) Modules

The framework includes three carefully selected hardware designs of increasing complexity:

### 1. Stride Detector
A mock design representing the core functionality of a data prefetcher. This module detects patterns in incoming data streams, identifying single and double stride patterns within a 5-bit signed integer range (-16 to 15).

**Key Features:**
- Single stride detection (e.g., 1,2,3,4,5 with stride +1)
- Double stride detection (e.g., 1,2,4,5,7,8 with alternating strides +1,+2)
- Overflow handling for strides outside the detectable range
- Comprehensive coverage metrics for verification

### 2. Ibex Instruction Decoder
A standalone instantiation of the instruction decoder from the open-source Ibex RISC-V processor core. This provides a realistic, industry-relevant verification target with complex instruction decode logic.

### 3. Ibex CPU Core
The complete Ibex RISC-V processor core, representing the most complex verification challenge in the framework. This full processor implementation tests the framework's scalability to real-world hardware verification scenarios.

## Advanced Implementation Features

### Token Budget Management
The framework includes sophisticated token budget management to control API costs while maximizing coverage efficiency. This feature enables cost-effective experimentation with various LLM strategies.

### Multi-Model Support
Support for multiple LLM backends including OpenAI's GPT models with advanced conversation compression algorithms :
- Recent message prioritization
- Successful response selection
- Difficulty-based response prioritization
- Mixed sampling strategies

### Adaptive Coverage Strategies
The system implements multiple coverage-driven strategies:
- **Missed-bin sampling**: Focuses on uncovered test cases
- **Best-iterative-message sampling**: Selects most effective previous responses
- **Coverage rate-based tolerance**: Adapts restart frequency based on current coverage levels

### Comprehensive State Management
Global state management system that abstracts different DUT types while providing unified interfaces for coverage tracking and state monitoring.

## Installation and Setup

### Prerequisites

**Core Dependencies:**
- **Cocotb**: Hardware simulation framework
- **Verilator v5+**: High-performance hardware simulator
- **Python Dependencies**: Specified in requirements.txt

### Installation Process

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build Verilator from source (recommended for latest features)
# Follow instructions at: https://verilator.org/guide/latest/install.html
```

## Usage and Execution

### Running Simulations

The framework uses a two-process execution model :

1. **Start the Simulation Server:**
   ```bash
   cd [module_directory]
   make
   ```

2. **Launch the Stimulus Generation Client:**
   ```bash
   python generate_stimulus.py
   ```

3. **Configure Experiments:**
   Edit the `generate_stimulus.py` file to specify experimental parameters and LLM strategies.

### Logging and Analysis

All experimental data is automatically logged in structured formats:
- **TXT Logs**: Human-readable conversation histories
- **CSV Logs**: Structured data for statistical analysis
- **Coverage Metrics**: Detailed bin-by-bin coverage tracking

## Extensibility

### Experimental Framework
The modular design enables researchers to:
- Implement custom prompt generation strategies
- Integrate new LLM backends
- Define novel coverage metrics
- Explore different dialogue management approaches

### Benchmarking Capabilities
The framework provides standardized benchmarks for:
- LLM effectiveness in hardware verification
- Token efficiency analysis
- Coverage convergence studies
- Comparative analysis of different AI approaches

