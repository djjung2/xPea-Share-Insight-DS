from flask import render_template
from flask import request
from flaskexample import app
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from inflection import singularize




# Python code to connect to Postgres
# You may need to modify this based on your OS, 
# as detailed in the postgres dev setup materials.
#user = 'derekjung' #add your Postgres username here      
#host = 'localhost'
#dbname = 'birth_db'
#db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#con = None
#con = psycopg2.connect(database = dbname, user = user)

#required skills, abilities, and knowledge for 13,172 job positions
skills_abilities_knowledge_first_half = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'skills_abilities_knowledge_all_half1.csv')
skills_abilities_knowledge_second_half = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'skills_abilities_knowledge_all_half2.csv')

skills_abilities_knowledge = pd.concat([skills_abilities_knowledge_first_half,
                                      skills_abilities_knowledge_second_half])
all_job_titles = skills_abilities_knowledge.loc[:,'Job Title']
skills_abilities_knowledge = skills_abilities_knowledge.set_index('Job Title',drop=True)


bad_jobs = requests.get('https://raw.githubusercontent.com/djjung2/'
                        + 'xPea-Share-Insight-DS/master/data/processed/'
                        + 'titles_not_scored.txt').text.strip().split(' AKLDJJ ')

skills_abilities_knowledge = skills_abilities_knowledge.dropna()


#has required skills, abilities, and knowledge for 967 jobs in ONet Database
skills_abilities_knowledge_967 = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'skills_abilities_knowledge_967_companies.csv',
  index_col = 'Title')
skills_abilities_knowledge_967 = skills_abilities_knowledge_967.drop(['Unnamed: 0','skills_N','abilities_N','knowledge N'], axis=1)

#Pros and Cons ratings of companies
pros_cons_by_company = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'companies_pros_cons_scores.csv',
  index_col='Company Id')
#drop columns outside of company ID and 5 categories pros/cons
pros_cons_by_company = pros_cons_by_company.loc[:,:'CONs Career Opportunities mean']
pros_cons_by_company = pros_cons_by_company.drop('Unnamed: 0', axis=1)

all_company_ids = pros_cons_by_company.index.tolist()

#Companies included in Glassdoor reviews
reviewed_companies = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'companies_reviewed.csv',
  index_col='Unnamed: 0')
#will only use Company Id, Company URL, company_name
reviewed_companies = reviewed_companies.loc[:,['Company Id', 'Company URL', 'company_name']]

#DataFrame has index: company ID's, column: list of available jobs
company_jobs_df = pd.read_csv(
  'https://raw.githubusercontent.com/djjung2'
  '/xPea-Share-Insight-DS/master/data/processed/'
  'companies_available_jobs.csv',
  index_col='Company Id')
company_jobs_df = company_jobs_df.drop(10139) #no jobs not in bad jobs for company ID 10139

#keys: company ID's
#values: list of jobs at company
company_jobs_dict = {company_id: company_jobs_df.loc[company_id,'Available Jobs'].split(' AKLDJJ ') 
                     for company_id in company_jobs_df.index}

@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html",
      title = 'Home', user = { 'nickname': 'Miguel' },
      )


@app.route('/behind_the_search')
def behindthesearch():
   return render_template("behind_the_search.html")

@app.route('/why_the_name')
def thename():
   return render_template("thename.html")

@app.route('/about_me')
def aboutme():
   return render_template("aboutme.html")


@app.route('/input')
def jobs_input():


   return render_template("input.html")

@app.route('/output')
def jobs_output():
 
 ##########################
 ##########################
 ### user input
 ##########################
 ##########################

 input_company_name = request.args.get('company_name')
 input_title = request.args.get('job_title')
 input_scale = request.args.get('scale')
 input_num_options = request.args.get('num_options')



 #index at which company occur in reviewed_companies df
 company_index = reviewed_companies[reviewed_companies['company_name'] == input_company_name].index[0]

 #Company ID of company
 company_id = int(reviewed_companies.loc[company_index, 'Company Id'])

 #####################
 ### Company Scores
 #####################

 #Series of distances from inputted company to every other company
 company_distance = (pros_cons_by_company - pros_cons_by_company.loc[company_id,:]).applymap(lambda x: x**2).sum(axis=1)

 #apply square root transformation to decrease spread of distances
 company_distance = company_distance.apply(lambda x: x**(1/2))


 #max distance from inputted company to another company
 max_company_distance = company_distance.describe()['max']


 #find company similarity scores (1-5) between company_id and all other companies
 companies_scores = company_distance.apply(lambda x: 5 - 4 * x / max_company_distance)


 #############################################
 ### Find vector representation of job title
 #############################################

 if input_title in set(all_job_titles):
     input_title_vector = skills_abilities_knowledge.loc[input_title,:]
 
 else:
     #find closest jobs to title by searching on ONet Database
     search_url = 'https://www.onetonline.org/find/quick?s=' + input_title
     htm_cont = requests.get(search_url).content #get htm l of search results page
 
     #find best 3 jobs suggested
     soup = BeautifulSoup(htm_cont,'lxml')
     divs = soup.find_all('td',{'class':'report2ed'})[:3]

     closest_jobs = [str(a) for div in divs for a in div.find('a')]

     #check if it is in Database by seeing if it matches first of closest_20_jobs (up to case, plural)
     if singularize(closest_jobs[0].lower()) == singularize(title.lower()): #title is in Database
         input_title_vector = skills_abilities_knowledge_967.loc[closest_jobs[0],:]
 
     #otherwise return a number of jobs
     else:
         #return the average of these three vectors
         input_title_vector = pd.concat([skills_abilities_knowledge_967.loc[closest_jobs[idx],:]
                  for idx in range(3)], axis=1).mean(axis=1)

 ##############################################
 ### Find job similarity scores
 #############################################       

 #Series of distances from inputted company to every other company
 titles_distance = (skills_abilities_knowledge - input_title_vector).applymap(lambda x: x**2).sum(axis=1)
 
 #apply square root transformation to shrink range of distances
 titles_distance = titles_distance.apply(lambda x: x**(1/2))

 #max distance from inputted company to another company
 max_title_distance = titles_distance.describe()['max']
 
 #score of inputted company to every other company
 titles_scores = titles_distance.apply(lambda x: 5 - 4*x/max_title_distance)

 #################################################################
 ### Find most similar title (to inputted title) at each company
 #################################################################

 #keys: company ID's
 #values: list of pairs (job, job score) for jobs at company
 company_job_scores_dict = {comp_id:[(title, titles_scores[title])
                                for title in company_jobs_dict[comp_id]
                                if title not in bad_jobs]
                       for comp_id in company_jobs_dict}

 #keys: company ID's
 #value: pair (job, job score) with job score among all jobs at company
 company_best_job_dict = {comp_id: max(company_job_scores_dict[comp_id], key=lambda x: x[1])
                     for comp_id in company_jobs_dict
                     if bool(company_job_scores_dict[comp_id])}

 #need to find companies where you get empty sequence


 scores_df = pd.DataFrame.from_dict({'Company score': companies_scores,
                                'Title score': [company_best_job_dict[comp_id][1] for comp_id in all_company_ids],
                                'Best title': [company_best_job_dict[comp_id][0] for comp_id in all_company_ids]})

 #input scale: how open are you to learning new skills
 #input scale=5: company score more important <- here
 #input scale=1: title score more important
 scores_df.loc[:,'Overall score'] = scores_df.apply(lambda row:
                                                float(input_scale)/6*row['Company score'] + (6-float(input_scale))/6*row['Title score'],
                                                axis=1)

 #sort by overall score
 scores_df = scores_df.sort_values(by=['Overall score'], ascending=False)

 scores_df_best = scores_df.iloc[:int(input_num_options),:].merge(reviewed_companies, 
                                                         on='Company Id')

 
 company_titles = []
 company_title_scores = []
 company_similarities = []
 company_urls = []
 
 for idx in range(int(input_num_options)):
     company_option = scores_df_best.iloc[idx]
     #Job title and company name


     
     company_titles.append('{}. {} at {}'.format(idx+1, 
                                         company_option['Best title'],
                                         company_option['company_name']))
                                      
     
     #print scores
     company_title_scores.append('Overall: {0:.2f}/5.00,  Company similarity: {1:.2f}/5,  Job similarity: {2:.2f}/5'.format(company_option['Overall score'],
                                                                                                              company_option['Company score'],
                                                                                                              company_option['Title score']))
     ###
     company_difference_vector = (pros_cons_by_company.loc[company_id,:] - pros_cons_by_company.loc[company_option['Company Id'],:]).apply(lambda x: abs(x)).copy()
             
     two_most_similar = company_difference_vector.sort_values().index[:2].tolist()

     #remove 'mean' from end of category name
     two_most_similar = [cat.strip('mean').strip() for cat in two_most_similar]
     
     #switch order of 'PROs/CONs' then 'category' to 'category' then 'PROs/CONs' (for readability)
     for list_idx in range(2):
         two_most_similar[list_idx] = two_most_similar[list_idx][5:] + ' ' + two_most_similar[list_idx][:4]
     
     #include main company similarities
     company_similarities.append('Most similar to {} in: {}, {}'.format(input_company_name, two_most_similar[0],two_most_similar[1]))
     

     
     
     #link to learn more
     company_urls.append(company_option['Company URL'])
     #output.append('Learn more at {}'.format("<a href='" + company_option['Company URL'] + "'>" + company_option['Company URL'] +"</a>"))
     
 data = pd.DataFrame.from_dict({'company_title': company_titles, 
  'scores':company_title_scores,
  'similarities': company_similarities,
  'company_URL': company_urls})
     
     
 #dataframe = pd.DataFrame(output)

 #dataframe = scores_df_best

 return render_template("output.html", 
  data = data,
  input_company_name = input_company_name,
  input_title = input_title,
  input_scale = input_scale,
  input_num_options = input_num_options)


@app.route('/behind_the_search')
def behind_the_search():


   return render_template("behind_the_search.html")