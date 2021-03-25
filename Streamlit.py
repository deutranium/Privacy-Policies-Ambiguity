# Libraries
import streamlit as st
import pandas as pd
import os
import functions
import numpy as np


# Data
Path = "./New Folder With Items/"
filelist = os.listdir(Path)
txt_files = []
file_names = []

# constants for query analysis
data = pd.read_json('queries.json')
queries = data.queries

query_list = []
org_list = {}
chart_dict = {}
columns_queries = ["Keyword", "Phrase", "Relevance"]


# file read
for i in filelist:
    if i.endswith(".txt"):
        file_names.append(i)
        with open(Path + i, 'r', encoding='utf8') as f:
            txt_files.append(f.read())

preprocessed_files = [ functions.preprocess_text(i) for i in txt_files ]

distrubutions = [functions.generate_distrubution(i) for i in preprocessed_files]

Df = pd.DataFrame(distrubutions,
                  columns=['Condition', 'Generalization',
                        'Modality', 'Numeric quantifier', 'Num Vague Terms'],
                 index = file_names)
Df[Df['Num Vague Terms']!=0].to_csv('./Distrubution.csv')
Df[Df['Num Vague Terms']==0].to_csv('./No_Terms.csv')

Columns = Df.columns
Company = Df.index

table = {'Category': ['Condition', 'Generalization' , 'Modality', 'Numeric Quantifier'] , 
'Meaning': ['Action(s) to be performed are dependent on a variable or unclear trigger.' , 'Action(s)/Information Types are vaguely abstracted with unclear conditions.', 'Vague likelihood of action(s) or ambiguous possibility of action or event.', 'Vague quantifier of action/information type.'] ,
'Examples':["""depending, necessary, appropriate,
inappropriate, as needed, as applicable,
otherwise reasonably, sometimes, from time
to time""","""generally, mostly, widely, general, commonly,
usually, normally, typically, largely, often,
primarily, among other things""","""may, might, can, could, would, likely, possible,
possibly""","""anyone, certain, everyone, numerous, some,
most, few, much, many, various, including but
not limited to """] }

tab = pd.DataFrame(table)






# Navigation and visualsation


rad = st.sidebar.selectbox("Navigation", ["Overview", "Data Analysis", "Query Analysis"])

# Navigation: Overview
if rad == "Overview":


    st.markdown("""# **Ambiguity in Privacy Policies**""")
    st.subheader("**Corpus:** 73 privacy policies taken from publicly available apps on the Google Play Store")

    st.subheader("Inspiration")
    st.markdown(""" We have used the methodology from the paper [Ambiguity in Privacy Policies and the Impact of Regulation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2715164) to quantify the degree of ambiguity in the set of privacy policies gathered. The paradigm they present categorizes ambiguous terms into the **four categories: Condition, Generalization, Modality and Numeric Quanitifiers**. The same have been described with examples in the table below.
     """)
    st.table(tab.set_index('Category'))
    
    st.subheader("Methodology")
    st.markdown(" The process involved scraping the privacy policies, categorizing the different terms into their respective categories, finding their percentages and finally displaying them in the form of an interactive charts accessible using the navigation on the left")
    

    # st.markdown("Link to paper : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2715164")

if rad == "Data Analysis":

    st.header("**Data Analysis**")

    st.subheader("Company wise data")
    st.markdown("To view, companywise, the percentage breakdown of which category of ambiguity inducing terminologies introduce ambiguity to which extent, measured as percentages, we offer the following drop down menu displaying values, in each case, of - Condition, Generalization, Modality, Numeric Quantifier and the Number of Vague terms")
    rad_comp = st.selectbox("Select the Company.", Company)

    for i in range(0, len(Company)):
        if rad_comp == Company[i]:
            st.dataframe(Df.loc[Company[i], :])
            
    st.markdown("----")
    
        
# Navigation : Columns

    st.subheader("Parameter wise data")
    st.markdown("To view the data in terms of the categories that introduce ambiguity into the document, we present the this section, which displays the data visually about the distribution of quantities like condition, generalization etc. across the companies whose privacy policies were used in the corpu.s")
    radio = st.selectbox("Select the parameter", Columns)
   
    for i in range(0, len(Columns)):
        if radio == Columns[i]:
             
            st.dataframe(Df.loc[:,Columns[i]])
            st.line_chart(Df.loc[:,Columns[i]])

    st.markdown("----")

    st.subheader("_**Average values**_")
    st.markdown("The average values across the whole corpus")
    for i in Df:
        st.write(i, ": ", Df[Df['Num Vague Terms'] != 0][i].mean())
    

if rad == "Query Analysis":

    st.header("Query Analysis")
    st.markdown("Using the Closed Domain Question Answering toolkit we created a system to query the privacy policy documents for verbal answers. The model was trained upon the corpus, after which queries regarding comon concerns were made. Answers as found, are displayed below for the user to view.")


    # parse data into meaningful dataframes and arrays
    for i in queries:
        query = i["query"]
        query_list.append(query)
        response = i["response"]

        org_list[query] = []    # store the organisations for this query
        chart_dict[query] = {}  # data for this query's plot
        org_avg = {}    # average pre org for this query 

        for res in response:
            org = res[1]
            val = res[3]
            if org in org_list[query]:
                org_avg[org].append(res[3])
                continue
            else:
                org_list[query].append(org)
                chart_dict[query][org] = 0
                org_avg[org] = [res[3]]

        # Calculate the average of the array
        for org in org_list[query]:
            chart_dict[query][org] = sum(org_avg[org])/len(org_avg[org])

    # Select question
    query_selected = st.selectbox('Select query', options = query_list)
    query_index = query_list.index(query_selected)
    row_list = []

    chart_df = pd.DataFrame(chart_dict[query_selected].values(), index=chart_dict[query_selected].keys())

    # Print line chart
    st.line_chart(chart_df)

    # Select the company
    org_selected = st.selectbox('Select org', options = org_list[query_selected])

    # Create the dataframe to be printed
    for i in queries[query_index]["response"]:
        if(i[1] == org_selected):
            this_dict = {"Keyword": i[0], "Phrase": i[2], "Relevance": i[3]}
            row_list.append(this_dict)

    selected_df = pd.DataFrame(row_list, columns = columns_queries)

    st.dataframe(selected_df)



