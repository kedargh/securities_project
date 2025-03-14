# securities_project
Project for Internship
# GRAPH AND NODES INVOLVED - 
![Workflow](images/workflow.png)

# Project Description - 
- This project is a Data Science project based on market research and LLMs.
- The first part of this project is purely based on Postgres based market data series extraction using yfinance and Supabase - 
  - Time series extraction for over 150 listed companies.
  - Daily data extraction scheduled using Apache Airflow DAGs.
  - Calculating market stats - PE ratio, Liquidity, Volumes, 52-week statistics, EPS ratio, etc.
  - Fetching company data - Founders, history, exchange listed on, capital holdings, etc.
  - Alternate method is running a bash script scheduler in the operating system.
  - Supabase used for data warehousing.
 
- The second part of the project is the sentiment analysis for any stock using FinBERT -
  - Uses locally install FinBERT for news classification.
  - Categorizes the market news for that stock and lists all the hot tips from the market.
  - Gives a summary of classified news.
 


## Tools being used for data extraction and cleansing - 
1) yfinance API
2) Supabase docker and API
3) XML files for config and creating tables
4) Autogen 0.4.5 for Agentic Workflows and dynamic function calls.
5) ChatGPT 4o-mini for handling NLP prompts

## LLM operations and RAG - 
1) FinBERT
2) Autogen Agentic Workflow
3) Langgraph Nodes and Graphs

## Tools used for scheduling and workflow management- 
1) Apache Airflow
2) Supervisor Autogen Agent for addressing FunctionTool() calls.
