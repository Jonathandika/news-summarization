import streamlit as st
import pandas as pd
import numpy as np
import openai

openai.api_key = "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"


## STREAMLIT APP

st.title('Headline Summarization')
st.subheader("Upload your file in Excel format (.xlsx)")
st.text("Format Example:")

headlines = {
    "Headline": ["Apple's new iPhone 12 is a big hit", "Apple is releasing Vision Pro in 2023", "Apple iPhone 15 Pro is the next major release"],
}
df_apple = pd.DataFrame(headlines)
st.dataframe(df_apple)

COMPANY_NAME = st.text_input("Enter Company Name")

## FUNCTIONS

system_prompt_summary = f'''

    As an AI trained by OpenAI, your task is to summarize the daily news headlines concerning a specific company, named '{COMPANY_NAME}'. 
    Analyze the headlines from various reputable news sources and generate a concise summary report in bullet points, 
    focusing on the key points and crucial information about the company.

    For your summary, include the following details:

    1. Major news headlines concerning the company.
    2. Key events or developments related to the company.
    3. Implications of these events or updates for the company.
    4. Any notable changes or trends in company performance.
    5. Any product announcements or launches.
    6. Any rumors or speculations about the company.
    7. Any financial updates or announcements.
    8. Any other relevant information.

    Remember to provide accurate, factual information in a neutral and professional tone. And return the summary in english.

'''


user_prompt_summary = f'''

    Summarize this headlines into a few bullet points talking about what is going on with '{COMPANY_NAME}' right now in english. 
    A text will be given to you which is a collection of headlines separated by '||'. 

'''

system_prompt_combine = f'''

    As an AI trained by OpenAI, your task is to combine this bullet points from different sources into a single summary that consist of bullet points.
    The goal here is to just combine the different documents that seperated by '||' into a single document of bullet points. 
    You just need to make sure that the bullet pointst are not duplicated. But, please keep the detail intact and generate a minimum of 20 bullet points.
    Also please do it in english.

'''

user_prompt_combine = f'''

    Combine this bullet points seperated by || into one single document that consist of many bullet points and make sure that there is no duplication. 
    Here is the text that you need to combine:

'''


system_prompt_short = f'''

    As an AI trained by OpenAI, your task is to combine this bullet points into a single summary that consist of maximum 20 bullet points.
    The goal here is to combine the bullet points based on the topic of the sentence. Combine the bullet points that have the same topic/product/feature. 

'''

user_prompt_short = f'''

    Combine this bullet points into a single summary that consist of maximum 20 bullet points.
    Remember to just give maximum 20 bullet points and please do it in english.
    Here is the text that you need to combine:

'''


def summarize_helper(text: str) -> str:
    messages = [
                    {"role": "system", "content": system_prompt_summary},
                    {"role": "user", "content": user_prompt_summary + f"This is the headlines: {text}" },
                ]

    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        n = 1,
        stop = None,
        temperature = 1,
        top_p = 1
    )

    response_text = completion.choices[0].message.content

    return response_text

def combine_helper(text: str) -> str:
    messages = [
                    {"role": "system", "content": system_prompt_combine},
                    {"role": "user", "content": user_prompt_combine + text },
                ]

    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        n = 1,
        stop = None,
        temperature = 1,
        top_p = 1
    )

    response_text = completion.choices[0].message.content

    return response_text


def summarize(headlines : list) -> str:


    summaries = headlines

    cnt = 1
    while len(summaries) > 1: 

        if cnt == 1:
            print(f"Summarizing headlines")
            print(f"Number of headlines: {len(summaries)}")
            
            summaries_new = []
            for i in range(0, len(summaries), 100):
                if i+100 <= len(summaries):
                    end = i + 100
                else:
                    end = len(summaries)
                try: 
                    print("-- Summarizing headlines from index {} to {}".format(i, end-1))
                    combined_string = " || ".join(headlines[i:end])
                    summary = summarize_helper(combined_string)

                    summaries_new.append(summary)

                except Exception as e:
                    print(e)
                    pass   

            print("\n") 

        else:
            print(f"Combining round: {cnt-1}")
            print(f"Number of summary: {len(summaries)}")

            summaries_new = []
            for i in range(0, len(summaries), 100):
                if i+100 <= len(summaries):
                    end = i + 100
                else:
                    end = len(summaries)
                try: 
                    print("-- Combining summary from index {} to {}".format(i, end-1))
                    combined_string = " || ".join(summaries[i:end])
                    summary = combine_helper(combined_string)

                    summaries_new.append(summary)

                except Exception as e:
                    print(e)
                    pass


        summaries = summaries_new
        cnt += 1

    return summaries[0]


def short_summary(text: str) -> str:
    messages = [
                    {"role": "system", "content": system_prompt_short},
                    {"role": "user", "content": user_prompt_short + text },
                ]

    completion = openai.ChatCompletion.create(
        model = "gpt-4-0613",
        messages = messages,
        n = 1,
        stop = None,
        temperature = 0.2,
        top_p = 1
    )

    response_text = completion.choices[0].message.content

    return response_text

uploaded_file = st.file_uploader("Upload your headlines in Excel format here", type=['csv'])

if st.button("Summarize Headlines"):
    if uploaded_file is None or COMPANY_NAME == "":
        if uploaded_file is None:
            st.error("Please upload an Excel file")
        if COMPANY_NAME == "":
            st.error("Please enter a company name")

    else:
        try:
            df = pd.read_excel(uploaded_file)
            df = df.drop_duplicates(subset=['Headline'])

            st.text("Successfully uploaded headlines")
            st.dataframe(df['Headline'].head(5))

            # Filter headlines that start with company name
            df = df[df['Headline'].str.startswith(COMPANY_NAME)]

            st.text("Filtered headlines that start with company name")
            st.text("Number of headlines: {}".format(len(df)))

            with st.spinner('Summarizing...'):
                summary = summarize(df['Headline'].tolist())
                short_summary = short_summary(summary)

            st.success('Summarization Successful')
            st.download_button('Download Summary', short_summary)
            
            st.subheader("Summary")
            st.text(short_summary)
            
        except Exception as e:
            st.error("Something went wrong...")
            st.error(e)




