# xPea

I created xPea, a job recommendation system that suggests jobs tailored to each user's preferred balance between good company experience and job title. A user inputs a job title at a publicly traded company, and xPea will compare 13,000 unique job titles at over 4,000 companies to suggest similar jobs at companies. I deployed this project as a Flask web app hosted on AWS at xpeashare.work . This project was created as a Fellow in 4 weeks during the Fall 2018 session of Insight Data Science.

![xPea logo](https://raw.githubusercontent.com/djjung2/xPea-Share-Insight-DS/master/src/flaskexample/static/images/xPea_Logo.png)

# Motivation

It's hard to find a job that you want and can get (at least starting out). You may have a dream job at a company, but you'd feel better if you had more options. You could spend hours reading reviews of companies, hoping for a nice backup, but you have better things to do. Or maybe there is a job title you think you're trajectorying towards, but you would like to learn about other jobs you could do. That's where xPea comes in! xPea find jobs at companies similar to ones you're interested in by reading reviews and applying the nation's largest occupational database. Searching for jobs is hard enough. Let xPea xPeadite the process.

# Layout

    .
    ├── data                      # company and occupational data
    │   ├── external              # skills, abilities, and knowledge required for 967 jobs
    │   ├── interim               # Glassdoor category descriptions, common words in reviews, problematic job titles
    │   ├── processed             # data used to compare companies and job titles
    ├── notebooks                 # Jupyter notebooks
    │   ├── classification        # classification of reviews
    │   ├── hand-labeling         # hand label categories of review sentences 
    │   ├── jobs-at-companies     # EDA on reviews and find available jobs at companies
    │   ├── occupational-data     # represent jobs as vectors based on skills required
    ├── reports                   # compare my scores and Glassdoor's ratings
    │   ├── visualizations        # Jupyter notebooks coming my scores and Glassdoor's ratings
    ├── src                       # Source files
    │   ├── flaskexample          # creates Flask web app
    └── README.md
