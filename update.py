"""
Python script to run for updating CSV commits from markdown files in the ./commits directory  
"""
from os import listdir
from os.path import isfile, join

from datetime import datetime, timedelta

import argparse


def is_current_md(fname):
    """Function to determine if .md file corresponds to the current time"""
    date1 = datetime.strptime(fname.split('.md')[0], '%m.%d.%y')
    date2 = date1 + timedelta(days=7)
    return (date1 < today) and (date2 > today)


def get_commits(md_section):
    """Parse markdown section for individual commits"""
    try:
        commit_data = []
        processed_commits = []  # Keep track of which commits were processed
        section_date = md_section.split('\n')[0]
        commits = md_section.split('\n-')
        for commit in commits[1:]:
            if '[done]' in commit:
                commit_datum = {}
                commit_datum['date'] = section_date
                commit_datum['description'] = commit.split('[done]')[0]
                commit_datum['categories'] = commit.split('[categories: ')[1].split(']')[
                    0].split(', ')
                commit_datum['time'] = current_time
                commit_data.append(commit_datum)
                # Mark that this commit has been parsed
                processed_commit = commit.replace('[done]', '<done>')
                process_commits.append((commit, processed_commit))
        return commit_data, process_commits
    except:
        print('** No commits for {} **'.format(section_date))


def process_commits(processed_commits, md_path):
    for commits in processed_commits:
        # replace [done] with <done>
        markdown = markdown.replace(commits[0], commits[1])
    # Overwrite data in md file to included processing (probs more efficient way to do this)
    with open(md_path, 'w') as f:
        f.write(markdown)


if __name__ == '__main__':
    current_time = datetime.now()
    # config file
    # from config file, could also be '%-m.%-d.%y' or '%m/%d/%y' (mm/dd/yy)
    date_format = '%-m/%-d/%y'

    parser = argparse.ArgumentParser(description='Command line options')
    parser.add_argument('-d', '--dir', type=str,
                        default='./commits/', help='Commits directory')
    parser.add_argument('-a', '--all', type=bool, action='store_true',
                        default=False, help='Parse all dates or today only')
    args = parser.parse_args()

    # Pull up the currently relevant markdown file.
    md_path = args.dir
    md_files = [f for f in listdir(md_path) if isfile(
        join(md_path, f)) and f[-3:] == '.md']

    today = datetime.today()  # Get current date
    current_md = None

    for md in reversed(md_files):  # Go backwards for ~O(1) time
        if is_current_md(md):
            current_md = md

    md_path = '{}/{}'.format(args.dir, current_md)

    try:
        with open(md_path, 'r') as f:
            markdown = f.read()
    except FileNotFoundError:
        print('Make sure to create a current week markdown file first!')

    # Process commits
    if args.all:
        processed_commits = []
        sections = markdown.split('\n## ')
        for section in sections:
            commit_data, new_processed_commits = get_commits(section)
            processed_commits.extend(new_processed_commits)
    else:
        current_date = datetime.today().strftime(date_format)
        section = markdown.split(current_date)[-1].split('\n## ')[0]
        # Prefix date to md section
        section = '{}{}'.format(current_date, section)
        commit_data, processed_commits = get_commits(section)

    # Mark all processed commits in markdown file
    process_commits(processed_commits, md_path)

    # Update json file with new commit data

    #

# # Get categories from setup.json

# # As long as following prescribed formatting rules, should be ok.
# dates = markdown.split('\n## ')

# for date in dates:
#     try:
#         commits = date.split('\n-')
#         for commit in commits[1:]:
#             if '[done]' in commit:
#                 description = commit.split('[done]')[0]
#                 categories = commit.split('[categories: ')[1].split(']')[
#                     0].split(', ')
#                 print('Date: {}'.format(date.split('\n')[0]))
#                 print('Description: {}'.format(description))
#                 print('Categories: {}'.format(categories))
#     except:
#         print('** No commits for {} **'.format(date.split('\n')[0]))

# # Should be another option where you just get everything from the current date.
# commits_today = markdown.split()


# current_date = datetime.today().strftime(date_format)
# date = markdown.split(current_date)[-1].split('\n## ')[0]
# date = '{}{}'.format(current_date, date)  # Prefix date to md section

# commits = date.split('\n-')

# current_time = datetime.now()
