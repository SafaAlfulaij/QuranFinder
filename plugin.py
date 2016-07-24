# Copyright 2016 Safa AlFulaij <safa1996alfulaij@gmail.com>
#
# This file is part of QuranFinder.
#
# QuranFinder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QuranFinder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QuranFinder.  If not, see <http://www.gnu.org/licenses/>.

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('QuranFinder')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

API_URL = "http://api.globalquran.com/ayah/"#verse:ayah/quranID
# Set languages and translations the bot will accept
quranID = {
    "ar" : "quran-simple",
    "en" : "en.sahih",
    "tr" : "tr.yazir",
    "fa" : "fa.fooladvand"
}

TOKEN = "the token" # Token obtained from http://docs.globalquran.com

import requests

class qdata():
    def __init__(self, chapter, ayah, lang):
        if(lang == None):
            lang = "en"
        if(len(lang) == 2):
            if(lang not in quranID):
                raise ValueError("Only " + " ,".join(quranID) + " languages " + 
                    "are supported using two letters code. Maybe you would " + 
                    "like to use a translation/tafsir code instead, Check: " + 
                    "https://git.io/vwMz4 for a list of avalible sources.")
            lang = quranID[lang]

        if (chapter > 114 or chapter < 1):
            raise ValueError("Invalid Surah number.")

        json = self.requestData(chapter,ayah, lang)
        self.parseResponse(json)

        if (int(self.SurahNumber) != chapter):
        #If the ayah number is biger than the ayahs in the surah,
        # the API jump to another surah.
            raise ValueError("Invalid Ayah number.")

    def requestData(self, chapter, ayah, lang):
        url = API_URL + str(chapter) + ":" + str(ayah) + "/" + lang
        request = requests.get(url, params = {'key' : TOKEN})
        json = request.json()

        #the ID differs for each verse. So there is no static key to call in
        # the main json.
        for quran in json:
            json = json[quran]
            for quranVer in json:
                #the QuranID in the json. Here we used quranVar to avoid
                # conflict with the quranID above.
                json = json[quranVer]
                for ID in json:
                    json = json[ID]

        return json

    def parseResponse(self, json):
        self.SurahNumber = json["surah"]
        self.ayahNumber = json["ayah"]
        self.ayahText = json["verse"]



class QuranFinder(callbacks.Plugin):
    """This plugin gets verse and aya number and sends you the ayah using a web API."""

    def __init__(self, irc):
         self.__parent = super(QuranFinder, self)
         self.__parent.__init__(irc)

    def quran(self, irc, msg, args, surah, ayah, lang):
        """<surah> <ayah> <lang>

        returns ayah number <ayah> of surah number <surah> in <lang> language or translation or tafsir. for more information visit: https://git.io/vwMz9
        """
  
        if ayah.isdigit():
            data = qdatae(surah, int(ayah), lang)
            if type(data) == str:
                irc.reply(data)
                return
            else:
                if self.registryValue('splitMessages'):
                    ircMsgBytes = (str(data.SurahNumber) + "," + str(data.ayahNumber) +
                        ": " + data.ayahText).encode('utf-8')
                    splited_msg_bytes = split_irc_msg(ircMsgBytes)
                    for m in splited_msg_bytes:
                        irc.reply(m)
                else:
                    irc.reply(str(data.SurahNumber) + "," + str(data.ayahNumber) + ": "
                        + data.ayahText)
            return

        ayahs = _2nd_form(ayah)
        if not ayahs:
            irc.reply("Error! Not a valid format") #TODO: replace with better msg
            return

        for a in range(ayahs[0], ayahs[1] + 1):
            #TODO: better variable name(a)
            data = qdatae(surah, a, lang)
            if type(data) == str:
                irc.reply(data)
            else:
                if self.registryValue('splitMessages'):
                    ircMsgBytes = (str(data.SurahNumber) + "," + str(data.ayahNumber) +
                        ": " + data.ayahText).encode('utf-8')
                    splited_msg_bytes = split_irc_msg(ircMsgBytes)
                    for m in splited_msg_bytes:
                        #TODO: better variable name
                        irc.reply(m)
                else:
                    irc.reply(str(data.SurahNumber) + "," + str(data.ayahNumber) + ": "
                        + data.ayahText)

       
       
    quran = wrap(quran, ["int", "str", optional("something")])



Class = QuranFinder

def split_irc_msg(MessageBytes):
    splited_msg = []
    while len(ircMsgBytes) > 350:
        splitPoint = MessageBytes[0:351].rfind(' '.encode('utf-8'))
        splited_msg.extend([MessageBytes[0:splitPoint].decode('utf-8').strip()])
        MessageBytes = MessageBytes[splitPoint:]
   splited_msg.extend([MessageBytes[:]]
   return splited_msg

def qdatae(surah, ayah, lang):
    #TODO: give me a better name
    try:
        return qdata(surah, ayah, lang)
    except ValueError as e:
            return str(e)
    except (KeyError, TypeError) as e:
        #TypeError incase requesting a audio version. The json would
        # contain a list so qdata would raise a TypeError
        return "Wrong translation code or broken API."

def _2nd_form(ayah):
    #TODO: give me a better name
    ayah = ayah.split('-')
    if len(ayah) != 2:
        return 0
    elif not (ayah[0].isdigit() and ayah[1].isdigit()):
        return 0

    diff =  int(ayah[1]) - int(ayah[0]) 
    if (diff > 5) or (diff  < 1):
        return 0
    
    return [int(ayah[0]), int(ayah[1])]



# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
