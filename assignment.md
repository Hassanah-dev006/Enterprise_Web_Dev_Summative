Assignment Overview
In this summative assignment, you will demonstrate your ability to design and develop an enterprise-level fullstack application using real-world urban mobility datasets. You will work with raw data from the New York City Taxi Trip dataset, which contains trip records including timestamps, distances, durations, pickup/dropoff locations, and other metadata. More info on the new york taxi data.Links to an external site.
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Your task is to:

Clean and process the raw dataset

Store the processed data in a well-designed relational database

Build a backend service to query the data

Create a frontend dashboard that allows users to explore urban mobility patterns and draw meaningful insights

This assignment is designed to challenge your technical skills and your ability to think creatively and critically about real-world data. You are encouraged to explore the data deeply and communicate your findings effectively through your application.

Learning Objectives
By completing this assignment, you will:

Apply data preprocessing techniques to make sense of messy real-world data

Design and implement a normalized relational database schema

Develop a backend API to serve data efficiently

Build an interactive, responsive frontend application

Present analytical insights using meaningful and relevant visualizations

Demonstrate full-cycle system design, engineering, and problem-solving skills

Dataset

You are required to engineer a solution using the following three official NYC Taxi & Limousine Commission (TLC) data components. These files represent a raw relational environment (Fact and Dimension tables) that must be integrated into your system:
yellow_tripdata (Fact TableDownload Fact Table):  Contains raw trip-level records (timestamps, distances, rate codes, and itemized fare details). Refer to the TLC Trip Record User Guide for technical field definitions.
taxi_zone_lookup (Dimension TableDownload Dimension Table): Provides the categorical mapping for PULocationID and DOLocationID (Boroughs and Service Zones).
taxi_zones (Spatial MetadataDownload Spatial Metadata): Contains the raw GeoJSON spatial boundaries (polygons) corresponding to the Taxi Zone IDs.
Assignment Tasks
1. Data Processing and Cleaning (Backend)
Data Integration: Implement a pipeline to load the .parquet trip data and programmatically associate it with the taxi_zone_lookup.csv and taxi_zones metadata.

Data Integrity: Identify and resolve missing values, duplicates, and physical/logical outliers (e.g., anomalies in distance, fare amounts, or temporal records).

Normalization: Standardize all timestamps, numeric fields, and categorical identifiers for database storage.

Feature Engineering: Define and justify at least three derived features (e.g., metrics calculated from multiple raw columns) that provide deeper insight into urban movement or economics.

Transparency: Maintain a log of excluded or suspicious records to be discussed in your technical report.

You may use Flask or Node.js for your backend.

2. Database Design and Implementation
Design a normalized relational schema with appropriate indexing

Implement the database in PostgreSQL, SQLite, or MySQL

Write scripts to insert cleaned and enriched data into the database

Ensure data integrity and enable efficient queries

3. Frontend Dashboard Development
Build a web-based dashboard using HTML, CSS, and JavaScript

Include filtering and sorting options (e.g., by time, distance, location, fare)

Enable dynamic interaction with the data (e.g., visual summaries, detail views)

You are not told what to visualize. It is your responsibility to explore the dataset and decide what is insightful or useful. Original, well-justified visualization choices will be rewarded.

Deliverables
Team participation sheet: The group team lead should make a copy of the team participation sheet LinkLinks to an external site.   cohort 1 sheet LinkLinks to an external site. and edit the team part and add your team name. Make sure that you add each team's role and participation. Also add team meeting and notes. Make sure that all sections and well completed before submission. Only the team lead should make changes in the team participation sheet and other team members should be added with comment permissions only- failure to do this will lead to a zero on the assignment.
Codebase (.zip) and GitHub link:

All backend and frontend code

Clean project structure and README file with setup instructions

Link to your video walkthrough in the README

Team participation sheet
Database dump or schema files

PDF documentation report (see below)

Video walkthrough (5 minutes)

Overview of your system

Technical descriptions(architecture designs)
Explanation of your architecture and choices

Demonstration of working features

Your README file must be fully runnable without additional support. It should include installation steps, environment setup, and how to launch both the backend and frontend.

Deployment is not required but will be rewarded under the ‘Product Quality & Storytelling’ section if done properly.
Submissions without a video, documentation or readme file will receive a grade of zero.

Documentation Guidelines (2–3 Pages)
Each team must submit a technical report that reflects your design thinking and engineering decisions. The report must include:

1. Problem Framing and Dataset Analysis
Describe the dataset and its context

Identify data challenges (e.g., missing fields, outliers, anomalies)

Explain assumptions made during data cleaning

Highlight one unexpected observation that influenced your design

2. System Architecture and Design Decisions
Include a system architecture diagram (frontend, backend, database)

Justify your stack choices and schema structure

Discuss trade-offs you made during the design process

3. Algorithmic Logic and Data Structures
You are required to manually implement at least one algorithm or data structure as part of your system — without relying on built-in libraries or prewritten logic.

This should address a real problem in your dataset or application (e.g., filtering, ranking, grouping, anomaly detection, etc.).

Your implementation must include:

Custom code (no use of libraries like heapq, Counter, sort_values, etc.)

A brief explanation of your approach

Pseudo-code and time/space complexity analysis

The goal is to assess your understanding of algorithmic thinking in the context of real-world data — not your ability to call built-in functions.

4. Insights and Interpretation
Present three meaningful insights derived from the data. For each:

Show how you derived it (via query, algorithm, or visualization)

Include a visual (e.g., chart or screenshot)

Interpret what it means in the context of urban mobility

5. Reflection and Future Work
Reflect on technical and team challenges

Suggest improvements and next steps if this were a real-world product