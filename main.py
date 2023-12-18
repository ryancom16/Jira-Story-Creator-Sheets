import os
import pandas as pd
from jira import JIRA
from dotenv import load_dotenv
import getpass
from typing import List

# Load environment variables
load_dotenv()

# Custom Field Processing for Acceptance Criteria
def get_ac_input_from_field(field: List[str]):
    ac = []
    for i, text in enumerate(field):
        ac.append({
            "assigneeIds": [],
            "id": i,
            "isHeader": False,
            "mandatory": True,
            "name": text,
            "rank": 0,
            "status": None
        })
    return ac

# Jira Setup with getpass
def initialize_jira():
    jira_server = 'https://yourdomain.atlassian.net'
    username = getpass.getuser()
    password = getpass.getpass(f"Jira Password for {username}: ")
    jira = JIRA(basic_auth=(username, password), server=jira_server)
    return jira

# Check for missing data
def get_field_value(row, column_name):
    if column_name in row and pd.notna(row[column_name]):
        return row[column_name]
    return None

# Print Jira Tickets to be Created
def preview_jira_tickets(csv_file_path):
    df = pd.read_csv(csv_file_path)
    print("The following Jira tickets will be created:\n")
    for _, row in df.iterrows():
        print(f"Project Key: {get_field_value(row, 'Project Key')}, Summary: {get_field_value(row, 'Summary')}, Description: {get_field_value(row, 'Description')}, Issue Type: {get_field_value(row, 'Issue Type')}\n")
    return df

# Create Jira Tickets from CSV
def create_jira_tickets_from_csv(df, jira):
    for _, row in df.iterrows():
        issue_dict = {
            'project': {'key': get_field_value(row, 'Project Key')},
            'issuetype': {'id': '7'},
            'customfield_10811': {'key': get_field_value(row, 'Product Owner')},
            'customfield_11248': {'id': get_field_value(row, 'Team ID')},
            'customfield_10400': get_field_value(row, 'Epic'),
            'summary': get_field_value(row, 'Summary'),
            'description': get_field_value(row, 'Description'),
            'customfield_17600': get_ac_input_from_field(row['AC'].split(';')) if get_field_value(row, 'AC') else []
        }
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Created issue {new_issue.key}")

def main():
    csv_file_path = 'path_to_your_csv_file.csv'  # Update with the path to your CSV file
    df = preview_jira_tickets(csv_file_path)
    
    confirm = input("Do you want to proceed with creating these Jira tickets? (yes/no): ")
    if confirm.lower() == 'yes':
        jira = initialize_jira()
        create_jira_tickets_from_csv(df, jira)
    else:
        print("Jira ticket creation cancelled.")

if __name__ == "__main__":
    main()
