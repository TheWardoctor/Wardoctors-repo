# -*- coding: utf-8 -*-

"""
    messages.py ---
    Copyright (C) 2017, Wardoctor, Midraal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import xbmcaddon
import random


def get_link_message():
    """
    helper function to get a random message when selecting links
    """
    import random
    messages = [
        {'HD': 'Nice if there',
         'SD': 'Usually there'
         },
        {'HD': 'Click it',
         'SD': 'Better than Nothing'
         },
        {'HD': 'Looks the shizz',
         'SD': 'Teen with Shakey Cam maybe'
         },
        {'HD': 'This is the one you will love',
         'SD': 'From a zip up bag at a Car Boot Sale'
         },
        {'HD': 'Good Internets',
         'SD': 'Vermin Speeds'
         },
        {'HD': 'Awesome! Quality of Kings',
         'SD': 'My Eyesight is Poor so it will be blurry anyway'
         },
        {'HD': 'BluRay or even better',
         'SD': 'VHS Quality if you are lucky'
         },
        {'HD': 'Single Malt 21 Year Old Scotch',
         'SD': 'Skol Lager'
         },
        {'HD': 'The Highest Quality for the connoisseur',
         'SD': 'Just want to watch it, it will be rubbish anyway'
         },
        {'HD': 'Jump Jet',
         'SD': 'Hillbilly Ute'
         },
        {'HD': 'Sexy',
         'SD': 'Granmas naked again, wheres the eye bleach'
         },
        {'HD': 'High Definition',
         'SD': 'Through Frosted Glass'
         },
        {'HD': 'Deadpool',
         'SD': 'Deadmurky'
         },
    ]

    if xbmcaddon.Addon().getSetting('enable_offensive') == 'true':
        messages.extend([
            {'HD': 'Fucking Brilliant Quality',
             'SD': 'Fucking Gash'
             },
            {'HD': 'This Shit Rocks!!',
             'SD': 'This Shit Sucks!!'
             },
            {'HD': 'Massive Firm Tits',
             'SD': 'Granny Knee Knockers',
             },
        ])

    if xbmcaddon.Addon().getSetting('disable_messages') == 'true':
        message = {
            'HD': 'If Available',
            'SD': ''
        }
    else:
        message = random.choice(messages)
    return message


def get_searching_message(preset):
    """
    helper function to select a message for video items
    Args:
        preset: search quality preset ("HD", "SD" or None)
    Returns:
        random message for video items
    """
    if xbmcaddon.Addon().getSetting('disable_messages') == "true":
        return ' '
    messages = [
        '',
        'Missy has stolen the Tardis, back soon',
        'Missy is snoring',
        'Missy\s dedication knows no bounds',
        'Searching the Interwebs for your selection',
        'Missy needs to have a work with you about your taste in Movies',
        'Missy will find that for you now',
        'Missy likes you, run',
        'Missy is getting annoyed that you are on your phone',
        'Missy is wanted throughout the Universe',
        'Missy loves your Movie choices',
        'When Missy watches a Movie, She watches it before its made',
        'Missy is fear itself',
        'Missy makes Paranoia scared',
        'Missy has no need for money, she does it because she cares',
        'Hidden under Missy\s dress is an entire squad of Judoon',
        'Missy Lives',
    ]

    if xbmcaddon.Addon().getSetting('enable_offensive') == "true":
        messages.extend([
            'It\s an absolute Cunt of a Day -- Kevin Wilson',
            'Really can\t be Fucked Today',
            'None Tardis Build Detected, Installing shit to fuck up your day',
            'Missy want\s to play with your sticky inside bits'
        ])

    if preset == "search":
        messages.extend([
            'Missy is checking the console for you'
        ])
    elif preset == "searchsd":
        messages.extend([
            'Missy is going back in time to the 80\s for a VHS copy',
        ])

    return random.choice(messages)
