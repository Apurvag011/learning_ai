# create cookiecutter code that runs this file
import os
import json
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from IPython.display import display, Markdown
from openai import OpenAI

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/138.0.0.0 Safari/537.36"
}



class JOBSite:
    def __init__(self, url):
        self.url = url
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else 'Empty title'
        if soup.body:
            for irrelevant in soup.body(['script', 'style', 'img', 'input']):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)

    def get_user_prompt(self):
        user_prompt = (f"You are looking at a job description website "
                      f"titled {self.title}")
        user_prompt += ("\nThe contents of this website is as follows; "
                       "please provide analysis of this job and let me know "
                       "if this job would support visa sponsorship. "
                       "make sure this job is for Data Engineer.\n\n")
        user_prompt += self.text
        return user_prompt

    def get_system_prompt(self):
        return ("You are an assistant that analyzes the contents of a JOB "
                "description and provides a recommendation based on user "
                "specific criteria, ignoring text that might be navigation "
                "related. Respond in markdown.")

    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self.get_user_prompt()}
        ]
    

# create get api key function
def get_openai_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment "
                        "variables.")
    if not openai_api_key.startswith("sk-") or " " in openai_api_key:
        raise ValueError("OPENAI_API_KEY is not valid. It should start with "
                        "'sk-' and not contain spaces.")
    return openai_api_key


def get_theirstack_key():
    theirstack_api_key = os.getenv("THEIRSTACK_KEY")
    if not theirstack_api_key:
        raise ValueError("THEIRSTACK_KEY is not set in the environment "
                        "variables.")
    if not theirstack_api_key.startswith("ey") or " " in theirstack_api_key:
        raise ValueError("THEIRSTACK_KEY is not valid. It should start with "
                        "'sk-' and not contain spaces.")
    return theirstack_api_key


def display_content(content):
    """
    Display content appropriately for the current environment.
    Uses Jupyter display if available, otherwise prints to command line.
    """
    # Check if we're in an interactive environment
    in_notebook = False
    try:
        # Check if we're in IPython/Jupyter
        __IPYTHON__
        in_notebook = True
    except NameError:
        in_notebook = False
    
    if in_notebook:
        try:
            display(Markdown(content))
        except:
            # Fallback to print even in notebook if display fails
            print(content)
    else:
        # We're in command line - format nicely
        print("=" * 80)
        print("JOB ANALYSIS RESULT")
        print("=" * 80)
        print(content)
        print("=" * 80)

def main():
    # there is .env file in root dir load it
    try:
        url = ("https://careers.chewy.com/us/en/job/"
               "CHINUS7032055EXTERNALENUS/Data-Engineer-II?"
               "utm_medium=phenom-feeds%3Fgh_src%3Do8ua3y1&"
               "utm_source=linkedin")
        summarize(url)
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        exit(1)
    


def summarize(url):
    load_dotenv()
    job_site = JOBSite(url)
    openai_api_key = get_openai_api_key()
    openai = OpenAI(api_key=openai_api_key)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=job_site.get_messages()  # type: ignore
    )

    content = response.choices[0].message.content
    display_content(content)

if __name__ == "__main__":
    main()