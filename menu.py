
from __future__ import print_function, unicode_literals

from pprint import pprint
import os
import inquirer
from examples import custom_style_1 as style
from PyInquirer import Separator, print_json, prompt

from autobt import InteractiveBT
from BaseHaas import Bot, MadHatterBot
from botdatabase import BotDB


def main_menu():
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Make a choice between the following:',
            'choices': [
                'InteractiveBT',
                'Apply Bot Config from a file',
                # Separator(),
                {
                    'name': 'Change Backtesting date',
                    'disabled': 'Not yet implemented. Manually edit configs.ini'
                },
                
                'Read the docs'
            ]
        }
    ]

    answers = prompt(questions, style=style)
    pprint(answers)
    return answers
def main_menu_answers(answers):
    if answers['action'] == 'InteractiveBT':
        os.system('clear')
        print('InteractiveBT implies that you are manually changing bot parameters while backtesting is triggered automatically at a given interval or by a bot parameter change')
        print('Every BT session, is saved on your drive. Session ends if the ROI of the last 10 backtests was exactly the same. Every config from it can be applied to any other MH bot afterwards')
        print('Open any Mad-Hatter bot in FULL SCREEN, open BOT REMOTE to instantly see backtestin results, navigate to indicators tab, click on any parameter value. Now, with keyaboard arrow keys change the value up and down.')
        print('TAB and SHIFT+TAB keys, provide you with immense speed of indicators navigation!') 
        print('As long as typing coursor able to edit indicator values now, pressing TAB will move it to the next numeric parameter above. SHIFT+TAB moves it down.')
        print('Parameters with options like MA type are skipped.')
        print('bBands deviations have to be changed by quickly writing values down by numbers')
        print('To begin the process, simply chose Mad-Hatter Bot and change a few params here and there with the above written method!')
        print('Waiting for any MH bot parameter to change')
        # print('By the way, you can make a good config every 5 minutes this way.')
        InteractiveBT().backtest()
    elif answers['action'] == 'Apply Bot Config from a file':
        botlist = InteractiveBT().return_botlist()
        configs = InteractiveBT().load_results()

def select_config(configs):
    configs_sorted = configs.sort_values(by='roi', ascending=True)
    questions = [{
        'type': 'list',
        'name': 'bot',
        'message':'Select config based soley on ROI performance to apply',
        'choices':[i.roi for i in configs_sorted]
    }]


if __name__ == '__main__':
    os.system('clear')
    
    answers = main_menu()
    action = main_menu_answers(answers)