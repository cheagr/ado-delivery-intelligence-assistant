# ADO Delivery Intelligence Assistant

An AI-powered assistant that analyzes Azure DevOps (ADO) work item exports to generate delivery insights for Product Managers and Delivery Leads.

The application combines deterministic business rules with Large Language Model (LLM) reasoning to summarize feature progress, identify delivery risks, recommend PM actions, and highlight manual review items.

---

## Problem Statement

Large software features are often delivered across multiple sprints involving Features, Stories and Subtasks.

Although Azure DevOps contains all implementation details, understanding delivery progress requires manually reviewing dozens of work items, dependencies, comments and statuses.

This prototype reduces that effort by automatically:

- Building Feature → Story → Subtask hierarchy

- Evaluating delivery progress using deterministic business rules

- Identifying delivery inconsistencies

- Highlighting blocked work

- Producing an AI-generated executive delivery summary

---

## Key Features

### Deterministic Analysis

- Parses Azure DevOps Excel exports

- Builds hierarchical ticket relationships

- Calculates feature completion

- Detects parent/child status inconsistencies

- Identifies blocked tickets

- Highlights manual review items

### AI Insights

Using Google Gemini, the assistant generates:

- Executive Summary

- Delivery Risks

- Suggested PM Actions

- Manual Review Summary

- Confidence Assessment

The AI layer reasons only over validated business-rule outputs rather than raw ticket data, reducing hallucination risk.

---

## Architecture

```

                Streamlit UI

                     │

                     ▼

             excel_[parser.py](http://parser.py)

                     │

                     ▼

          business_[rules.py](http://rules.py)

                     │

                     ▼

          prompt_[builder.py](http://builder.py)

                     │

                     ▼

               [schemas.py](http://schemas.py)

                     │

                     ▼

           gemini_[client.py](http://client.py)

                     │

                     ▼

          Google Gemini 2.5 Flash

```

Configuration is managed through:

- [config.py](http://config.py)

- app_[startup.py](http://startup.py)

- .env

---

## Tech Stack

- Python

- Streamlit

- Pandas

- OpenPyXL

- Google Gemini 2.5 Flash

- Google GenAI SDK

---

## Design Principles

### Deterministic before AI

Business calculations remain deterministic.

The LLM performs reasoning—not calculations.

### Modular Architecture

Responsibilities are separated into dedicated modules:

- Excel Parsing

- Business Rule Engine

- Prompt Builder

- Response Schema

- Gemini Client

- Application Startup Validation

### Structured AI Outputs

The application uses schema-based structured outputs instead of prompt-engineered JSON, improving reliability and simplifying downstream processing.

---

## AI Concepts Demonstrated

- Enterprise AI Architecture

- LLM Integration

- Prompt Engineering

- Structured Outputs

- Response Schemas

- Modular AI Design

- Hallucination Mitigation

- Secure API Configuration

- Configuration Validation

- AI-assisted Product Management

---

## Sample Workflow

```

Upload ADO Excel

        │

        ▼

Parse & Normalize Tickets

        │

        ▼

Build Ticket Hierarchy

        │

        ▼

Evaluate Business Rules

        │

        ▼

Generate AI Delivery Insights

        │

        ▼

Display Executive Dashboard

```

---

## Future Enhancements

- Direct Azure DevOps REST API integration

- Sprint forecasting

- Historical trend analysis

- Team capacity insights

- Multi-feature portfolio analysis

- Release health dashboard

- PDF / PowerPoint report export

---

## Repository Structure

```

ado-delivery-intelligence-assistant/

├── [app.py](http://app.py)

├── app_[startup.py](http://startup.py)

├── [config.py](http://config.py)

├── excel_[parser.py](http://parser.py)

├── business_[rules.py](http://rules.py)

├── prompt_[builder.py](http://builder.py)

├── [schemas.py](http://schemas.py)

├── gemini_[client.py](http://client.py)

├── requirements.txt

├── [README.md](http://README.md)

└── .env (local only)

```

---

## Why this project?

This project was built to explore how Generative AI can augment Product Managers by combining deterministic software delivery metrics with LLM reasoning.

Rather than replacing existing delivery processes, the assistant accelerates delivery reviews while ensuring factual accuracy through rule-based validation before AI reasoning.