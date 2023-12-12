#!/usr/bin/env python3
from openai import OpenAI
import sys
import os
import configparser

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

def create_template_ini_file():
    """
    If the ini file does not exist, create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')
            f.write('model=gpt-3.5-turbo-0613\n')

        print(f'OpenAI API config file created at {API_KEYS_LOCATION}')
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
               'https://openai.com/blog/openai-codex/')
        sys.exit(1)

# Check if file at API_KEYS_LOCATION exists
create_template_ini_file()
config = configparser.ConfigParser()
config.read(API_KEYS_LOCATION)

client = OpenAI(
  api_key=config['openai']['secret_key'].strip('"').strip("'")
)

model = config['openai'].get('model', 'gpt-3.5-turbo')

cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix
response = client.chat.completions.create(model=model, messages=[
    {
        "role": 'system',
        "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation",
    },
    {
        "role": 'user',
        "content": full_command,
    }
])
completed_command = response.choices[0].message.content
sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)}")
