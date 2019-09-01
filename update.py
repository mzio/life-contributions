"""
Python script to run for updating CSV commits from markdown files in the ./commits directory  
"""
import json
import argparse
import numpy as np

from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta


class Commits(object):

    def __init__(self, md_path, save_path, process_all, max_threshold):
        # Hue values (percentages) for each category
        self.categories = {
            'code': 0,
            'school': 55,
            'side_projects': 144,
            'research': 216,
            'life': 288
        }

        self.date_format = '%-m/%-d/%y'
        self.hues = np.array(list(self.categories.values()))
        self.md_path = md_path
        self.save_path = save_path
        self.today = None
        self.md_files = None
        self.current_md = None
        self.markdown = None
        self.new_commits = []
        self.max_threshold = max_threshold
        self.process_all = process_all

    def save_commits(self):
        current_time = datetime.now()
        # config file
        # from config file, could also be '%-m.%-d.%y' or '%m/%d/%y' (mm/dd/yy)
        date_format = '%-m/%-d/%y'
        self.md_files = [f for f in listdir(self.md_path) if
                         isfile(join(self.md_path, f))
                         and f[-3:] == '.md']

        self.today = datetime.today()  # Get current date

        for md in reversed(self.md_files):  # Go backwards for ~O(1) time
            if self.is_current_md(md):
                self.current_md = md

        self.md_path = '{}/{}'.format(args.dir, self.current_md)

        try:
            print('Reading from {}...'.format(self.md_path))
            with open(self.md_path, 'r') as f:
                self.markdown = f.read()
        except FileNotFoundError:
            print('Make sure to create a current week markdown file first!')

        # Process commits
        if self.process_all:
            processed_commits = []
            sections = self.markdown.split('\n## ')
            # print('SECTIONS: {}'.format(sections))
            for section in sections:
                commit_data, new_processed_commits = self.get_commits(section)
                processed_commits.extend(new_processed_commits)
                self.new_commits.extend(commit_data)
        else:
            current_date = datetime.today().strftime(self.date_format)
            section = self.markdown.split(current_date)[-1].split('\n## ')[0]
            # Prefix date to md section
            section = '{}{}'.format(current_date, section)
            commit_data, processed_commits = self.get_commits(section)
            self.new_commits.extend(commit_data)

        self.save_aggregate(self.new_commits)

        # Mark all processed commits in markdown file
        self.mark_done(processed_commits, self.md_path)

    def is_current_md(self, fname):
        """Function to determine if .md file corresponds to the current time"""
        date1 = datetime.strptime(fname.split('.md')[0], '%m.%d.%y')
        date2 = date1 + timedelta(days=7)
        return (date1 < self.today) and (date2 > self.today)

    def get_commits(self, md_section):
        """Parse markdown section for individual commits"""
        try:
            commit_data = []
            processed_commits = []  # Keep track of which commits were processed
            section_date = md_section.split('\n')[0].split(' ')[0]
            commits = md_section.split('\n-')
            # print('COMMITS: {}'.format(commits))
            # print('SECTION: {}'.format(md_section))
            for commit in commits[1:]:
                if '[done]' in commit:
                    commit_datum = {}
                    commit_datum['date'] = section_date
                    commit_datum['description'] = commit.split(
                        '[done]')[0][1:-2]
                    commit_datum['categories'] = commit.split(
                        '[categories: ')[1].split(']')[0].split(', ')
                    commit_datum['time'] = current_time
                    commit_data.append(commit_datum)
                    # Mark that this commit has been parsed
                    processed_commit = commit.replace('[done]', '<done>')
                    processed_commits.append((commit, processed_commit))
            return commit_data, processed_commits
        except:
            print('** No commits for {} **'.format(section_date))

    def mark_done(self, processed_commits, md_path):
        # Overwrite data in md file to included processing (probs more efficient way to do this)
        with open(md_path, 'r') as f:
            markdown = f.read()
        for commits in processed_commits:
            markdown = markdown.replace(commits[0], commits[1])
        with open(md_path, 'w') as f:
            f.write(markdown)

    def save_aggregate(self, commit_data):
        try:
            with open(self.save_path, 'r') as f:
                # with open('./app/public/commits.json', 'r') as f:
                self.all_commits = json.load(f)
        except:
            self.all_commits = {}  # New commit log

        for commit in commit_data:
            self.process_commit(commit)

        for date in self.all_commits:
            h, s, l = self.get_hsl(self.all_commits[date])
            self.all_commits[date]['h'] = h
            self.all_commits[date]['s'] = s
            self.all_commits[date]['l'] = l
        json_commit = json.dumps(
            self.all_commits, indent=2, sort_keys=True, default=str)
        with open(self.save_path, 'w') as f:
            f.write(json_commit)
        print('{} updates committed!'.format(len(commit_data)))

    def get_hsl(self, date_data):
        counts = list(date_data['counts'].values())
        total_count = sum(counts)
        # Get hue as weighted sum of colors
        hue_weights = np.array(counts) / total_count
        hue = np.average(self.hues, weights=hue_weights)
        # Get saturation
        saturation = 0.5 + 0.5 * \
            np.min([self.max_threshold, total_count]) / self.max_threshold
        return hue, saturation, 0.5  # 0.5 lightness by default

    def process_commit(self, commit):
        # For each new commit,
        date = commit['date']
        if date not in self.all_commits:
            self.all_commits[date] = {'h': None, 's': None, 'l': None}
            self.all_commits[date]['counts'] = {k: 0 for k in self.categories}
        for category in commit['categories']:
            if category in self.categories:
                self.all_commits[date]['counts'][category] += 1


if __name__ == '__main__':

    current_time = datetime.now()
    # config file
    # from config file, could also be '%-m.%-d.%y' or '%m/%d/%y' (mm/dd/yy)
    date_format = '%-m/%-d/%y'

    parser = argparse.ArgumentParser(description='Command line options')
    parser.add_argument('-d', '--dir', default='./commits', type=str,
                        help='Commits directory')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='Parse all dates or today only')
    parser.add_argument('--save_path', default='commits.json', type=str,
                        help='Where to save file for js processing')
    parser.add_argument('--max_threshold', default=20, type=int,
                        help='Max value for color saturation')
    args = parser.parse_args()

    commits = Commits(md_path=args.dir,
                      save_path=args.save_path,
                      process_all=args.all,
                      max_threshold=args.max_threshold)
    commits.save_commits()
