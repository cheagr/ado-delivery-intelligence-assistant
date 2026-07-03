\# ADO Delivery Intelligence Assistant



A prototype AI-assisted workflow analyzer built to automate delivery tracking for enterprise product development teams.



\## Problem



Product managers often spend time manually reviewing engineering tickets across multi-sprint feature delivery to understand:



\- Current feature completion status

\- Stories completed vs pending

\- Blocked tickets

\- Status inconsistencies between parent stories and subtasks

\- Sprint planning candidates for next execution cycle



\## Current MVP Features



\- Excel upload for ADO export data

\- Feature > Story > Subtask hierarchy detection

\- Business rule engine for story completion validation

\- Detection of status mismatches requiring manual review

\- Feature completion percentage calculation

\- Blocked ticket identification



\## Planned Enhancements



\- LLM-powered dependency intelligence

\- Ticket description semantic analysis

\- PM action recommendations



\## Tech Stack



\- Python

\- Streamlit

\- Pandas

\- OpenPyXL



\## Architecture



Excel Input  

→ Parser Layer  

→ Hierarchy Builder  

→ Deterministic Business Rule Engine  

→ Structured Delivery Intelligence Output

