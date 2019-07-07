import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Command line options')
parser.add_argument('-d', '--dir', type=str,
                    default='./commits/', help="Commits directory. Please include all /'s thx")
args = parser.parse_args()

# Automatically determine date of first day of the week when run (setting this to Monday)
today = datetime.today()
start_date = (today - timedelta(days=today.weekday()))  # Date object

fname = start_date.strftime('%m.%d.%y.md')

eol = 2 * ' '  # Markdown end-of-line i.e. 2 spaces

# Actually create and write to file
with open('{}{}'.format(args.dir, fname), 'w') as f:
    # Starter markdown to be edited
    f.write('Weekly Commits for {}{}\n\n'.format(
        start_date.strftime('%D'), eol))
    f.write('## ' + start_date.strftime('%-m/%-d') + eol + '\n\n')
    f.write('### Sample header - change this!' + eol + '\n')
    f.write('Write logs or other notes here. Use ### for organizational sectioning.' + eol + '\n')
    f.write('* To render markdown lists, use asterisks like this.' + eol + '\n\n')
    f.write('Otherwise, to list commits or things to do that should render in your contribution calendar, do:' + eol + '\n')
    f.write(
        "- Example completed commit [done] [categories: sample_category]" + eol + '\n')
    f.write('or\n')
    f.write(
        "- Example not completed commit [] [categories: sample_category]" + eol + '\n\n')

    for i in range(1, 7):
        f.write('## ' + (start_date + timedelta(days=i)
                         ).strftime('%-m/%-d') + eol + '\n\n')

    f.write('Other settings (like categories and their colors) can be found and edited in config.json.')
