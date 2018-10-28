from urllib.parse import unquote

from .models import Dialect, Replacement, Reference, ReplacementCategory, Topic
from .debug import Debug as DebugClass
import re
from __init__ import *

debug = DebugClass()


def saveall():
    i = 0
    for obj in Replacement.objects.all():
        obj.save()
        if i%10 == 0:
            print(obj)
        i += 1
    print('done')



def updatetopiccitations(topicpk):
    topic = Topic.objects.get(pk=topicpk)
    text = topic.text

    citationpattern = r"(?<=[\<\[])(?P<pk>\d+)(?=[\:\]])"

    for match in re.finditer(citationpattern, topic.text):
        pk = match.groupdict()['pk']
        try:
            reference = Reference.objects.get(pk=pk)
            if reference not in topic.citations.all():
                topic.citations.add(reference)
        except ObjectDoesNotExist:
            continue

    topic.save()

    print(str(Topic.objects.get(pk=topicpk).citations.all()))


def fixsearchstrings():
    for r in Replacement.objects.all():
        oldsearchstrings = r.searchstrings
        # if '###' in r.searchstrings:
        #     stringlist = [w.strip() for w in r.searchstrings.split('\r\n') if w.strip() != '']
        #     for i, s in enumerate(stringlist):
        #         if '###' in s:
        #             stringlist[i] = '#' + s.replace('###', '').strip()
        #     searchstrings = u"\r\n".join(stringlist)
        #     r.searchstrings = searchstrings
        if (',' in r.searchstrings) or ('!' in r.searchstrings):
            print(r.searchstrings)
            print(' ')
            # stringlist = [w.strip() for w in r.searchstrings.split('\r\n') if w.strip() != '']
            # for i, s in enumerate(stringlist):
            #     if s[-1] == ',' or s[-1] == '!':
            #         stringlist[i] = s[:len(s)-1] + '.'
            #     stringlist = list(set(list(stringlist)))
            # searchstrings = u"\r\n".join(stringlist)
            # r.searchstrings = searchstrings

        # if oldsearchstrings != r.searchstrings:
        #     print(oldsearchstrings)
        #     print(r'-->')
        #     print(r.searchstrings)
        #     # r.save()

    print('done')


#find errors
# incorrect markup
# words with



def addreplacementtype():
    for obj in Replacement.objects.all():
        if obj.mandatory:
            obj.replacementtype = ReplacementCategory.objects.get(name='mandatory')
        elif obj.informal:
            obj.replacementtype = ReplacementCategory.objects.get(name='informal')
        elif obj.slang:
            obj.replacementtype = ReplacementCategory.objects.get(name='slang')
        else:
            obj.replacementtype = ReplacementCategory.objects.get(name='suggested')
        obj.save()
    print('done')








def findmultiplecategories():
    for obj in Replacement.objects.all():
        i = 0
        if obj.mandatory:
            i += 1
        if obj.informal:
            i += 1
        if obj.slang:
            i += 1
        if i > 1:
            print (obj)



def changebritishdialectname():
    for obj in Replacement.objects.all():
        if obj.dialect.name == 'British (Generic)':
            obj.dialect = Dialect.objects.get(name='British')
            obj.save()
            debug.add(['obj', obj], max=10)
    debug.print()


def addsbaclcitations():
    urlstart = "https://separatedbyacommonlanguage.blogspot.com/search/label/"
    labels = ["food%2Fcooking","idioms","pronunciation","adjectives","epithets","medicine%2Fdisease","spelling","WotY","babies and children","education","grammar","fashion%2Fclothing","adverbs","morphology","prepositions","body parts","books","taboo","time","politeness","names","rituals","transport%28ation%29","sport","shopping","games","more complicated than you might think","architecture","holidays","prepositional%2Fphrasal verbs","dialect","sex","politics%2Fhistory","money","AusE","class","interjections","prescriptivism","Canadian count","animals","bodily functions","geography","humo%28u%29r","law","occupations","SAfE","Scrabble","bureaucracy","count%2Fmass","metaphor","numbers","recreation","television","trade names","ScottishE","intoxicants","journalism","music","punctuation","stereotypes","untranslatable","French","clipping","foreign words","measurement","signage","Janus words","Latin","crime%2Fpunishment","furniture","gender","Americanization","U and non-U","communication","euphemism","hardware","housework","hygiene","project ideas","rhoticity","IrishE","auxiliary verbs","cliche","competition","containers","determiners","dictionaries","disability","emotions%2Fmoods","film","negation","plants","plurals","pronouns%2Fproforms","AVIC","conjunctions","guest bloggers","race%2Fethnicity","CanE","Greek","announcements","backformation","blends","colo%28u%29rs","exclamations","overstatement","understatement","Lynneukah","Sweden","alphabet","contractions","death","information structure","office supplies","onomatopoeia","questions","weather","Britishization","German","Italian","NZE","Spanish","computers","global English","nominali%7Bs%2Fz%7Dation","packaging","religion","swedish","symbols","theat%7Ber%2Fre%7D","Dutch","linguistic relativity","puzzle","subjunctive","supernatural","weapons"]

    for labelurl in labels:
        labeltext = unquote(labelurl)

        url = urlstart + labelurl
        adminname = "zsbacl-" + labeltext
        name = "Separated by a Common Language: %s tag" % labeltext

        citation = Reference(name=name, adminname=adminname, url=url)
        citation.save()

        print(citation)