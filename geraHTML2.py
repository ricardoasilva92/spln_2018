import xml.etree.ElementTree as ET
import pprint
import os, json
from os import listdir
from os.path import isfile, join

import codecs, re, getopt, sys, string, csv
import nltk
sys.excepthook = sys.__excepthook__

from itertools import tee, islice, chain
pp = pprint.PrettyPrinter(indent=4)

import unidecode as ud

#___________________CRIACAO DE SETs com NOMES, APELIDOS e stopWords PORTUGUESES_____________
    #nomes proprios
nomePortuguesesFicheiro = open('nomes_e_palavras/nomes_proprios.tsv',encoding="utf8")
nomePtReader = csv.DictReader(nomePortuguesesFicheiro,delimiter='\t',fieldnames=['nome','numero'])

nomesPtSet = set()
i=0
for row in nomePtReader:
    i+=1
    print(i)
    nomesPtSet.add(row['nome'])

    #apelidos
apelidosPortuguesesFicheiro = open('nomes_e_palavras/apelidos.tsv',encoding="utf8")
apelidoPtReader = csv.DictReader(apelidosPortuguesesFicheiro,delimiter='\t',fieldnames=['apelido','numero'])

apelidosPtSet = set()
for row in apelidoPtReader:
    apelidosPtSet.add(row['apelido'])

    #stopwords portuguesas
stopPortuguesesFicheiro = open('nomes_e_palavras/stopwords.txt')
stopPtSet = set()
for row in stopPortuguesesFicheiro:
    stopPtSet.add(row.split('\n')[0])
conetoresNomes = ['de','da','dos','das','do']

profissoesPtFicheiro = open('nomes_e_palavras/profissões.txt',encoding="utf8")
profissoesPtSet = set()
for row in profissoesPtFicheiro:
    profissoesPtSet.add(row.split('\n')[0])

worldCitiesFicheiro = open('nomes_e_palavras/cities.txt',encoding="utf8")
worldCitiesSet = set()
for row in worldCitiesFicheiro:
    worldCitiesSet.add(row.split('\n')[0])

temasFicheiro = open('nomes_e_palavras/temas.txt',encoding="utf8")
temasSet = set()
for row in temasFicheiro:
    temasSet.add(row.split('\n')[0])

#_____________________________________________________________________


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


#______________________DIARIO DE NOTICIAS_______________________________
onlyfiles = [f for f in listdir('obter_colecoes/[PT] Diario de Noticias/noticias/') if isfile(join('obter_colecoes/[PT] Diario de Noticias/noticias/',f))]
dict_DN = {}
for filename in onlyfiles:
    aux_set = set ()
    profissoes_set = set()
    #print(filename)
    path= 'obter_colecoes/[PT] Diario de Noticias/noticias/' + filename
    tree = ET.parse(path)
    root = tree.getroot()
    data = "data Null"
    locals = set()
    temas = set()
    tema = ''
    for child in root:
        if child.tag == "Date":
            data = child.text

        if child.tag == "Text":
            tokens = nltk.word_tokenize(child.text)
            #for pal in tokens:
            for previous, item, nxt in previous_and_next(tokens):
            #for item in tokens:
                decoded = ud.unidecode(item)
                if item[0].isupper() and decoded in worldCitiesSet:
                    locals.add(decoded)

                if item.lower() in temasSet:
                    temas.add(item)

                if item[0].isupper() and item.upper() in nomesPtSet:
                    #nomeProprio + (nomeProprio || apelido)

                    if previous and previous.lower() in profissoesPtSet:
                        profissoes_set.add(previous)
                    else:
                        profissoes_set.add('')

                    if nxt.upper() in apelidosPtSet or nxt.upper() in nomesPtSet:
                        nome_completo = item + ' ' + nxt

                        aux_set.add(nome_completo)

                    else:
                        #se nao tem nome nem atras nem à frente
                        if previous:
                            if previous.upper() not in nomesPtSet:
                                aux_set.add(item)

                #se anterior for nome e seguinte tambem nome_completo
                else:
                    if item in conetoresNomes:
                        if previous.upper() in nomesPtSet and (nxt.upper() in nomesPtSet or nxt.upper() in apelidosPtSet) and previous[0].isupper():
                            nome_completo = previous + ' ' + item + ' ' + nxt
                            aux_set.add(nome_completo)



            dataAsKey = ((data.split('/')[0]).strip('\n')).strip()
            c = dataAsKey.split(',')
            if len(c)>1:
                c = c[1].strip().split(' ')
                dataAsKey = c[0] + ' ' + c[1] + ' ' + c[2]

            if locals == set():
                locals = ''
            if temas == set():
                temas = ''


            for elem in aux_set:
                if elem in dict_DN:
                    for prof in profissoes_set:
                        dict_DN[elem].append({'prof':prof})
                    dict_DN[elem].append({'locals':locals, 'temas':temas})
                else:
                    dict_DN[elem] = []
                    for prof in profissoes_set:
                        dict_DN[elem].append({'prof':prof})
                    dict_DN[elem].append({'locals':locals, 'temas':temas})

            #print('-------------')
            #print('PERSONS [DN] : ' + data.split('/')[0])
            #for pal in aux_set:
                #print(pal)

pp.pprint(dict_DN)
i = 0
f=open('DN.html',mode='w')
f.write('<meta charset=\"UTF-8\">')
for elem in dict_DN:
    #pp.pprint(dict_DN[elem])
    decoded_elem = ud.unidecode(elem)
    decoded_elem = decoded_elem.replace(' ','_')

    tag = '<a href=dn_html/'+decoded_elem+'.html>'+elem+'</a><br>'

    f.write(tag)

    html=open('dn_html/'+decoded_elem+'.html','w')
    html.write('<meta charset=\"UTF-8\">\n')
    html.write('<table width=\"100%\" heigth=\"100%\">')
    html.write('<td width=\"33%\" heigth=\"100%\">')
    html.write('PROFISSOES<br>')
    for i in range(0,len(dict_DN[elem]),1):
        if 'prof' in dict_DN[elem][i]:
            if dict_DN[elem][i]['prof'] != '':
                html.write(dict_DN[elem][i]['prof']+'<br>')

    html.write('</td><td width=\"33%\" heigth=\"100%\">')
    html.write('LOCAIS<br>')
    for i in range(0,len(dict_DN[elem]),1):
        if 'locals' in dict_DN[elem][i]:
            for local in dict_DN[elem][i]['locals']:
                html.write(local+'<br>')
    html.write('</td><td width=\"33%\" heigth=\"100%\">')
    html.write('TEMAS<br>')
    for i in range(0,len(dict_DN[elem]),1):
        if 'temas' in dict_DN[elem][i]:
            for tema in dict_DN[elem][i]['temas']:
                html.write(tema+'<br>')
    html.write('</td>')
    html.write('</table>')
    html.close()

f.close()
'''
json = json.dumps(dict_DN)
f=open("DNprofs.json","w")
f.write(json)
f.close()
'''
"""#________________________________JORNAL DE ANGOLA_________________________________________-
onlyfiles = [f for f in listdir('obter_colecoes/[AGO] jornal angola/noticias/') if isfile(join('obter_colecoes/[AGO] jornal angola/noticias/',f))]
dict_JA = {}
for filename in onlyfiles:
    aux_set = set ()
    #print(filename)
    path= 'obter_colecoes/[AGO] jornal angola/noticias/' + filename
    tree = ET.parse(path)
    root = tree.getroot()
    data = "data Null"
    for child in root:
        if child.tag == "Date":
            data = child.text

        if child.tag == "Text":
            tokens = nltk.word_tokenize(child.text)
            #for pal in tokens:
            for previous, item, nxt in previous_and_next(tokens):
                if item[0].isupper() and item.upper() in nomesPtSet:
                    #nomeProprio + (nomeProprio || apelido)
                    if nxt.upper() in apelidosPtSet or nxt.upper() in nomesPtSet:
                        nome_completo = item + ' ' + nxt
                        aux_set.add(nome_completo)
                    else:
                        #se nao tem nome nem atras nem à frente
                        if previous:
                            if previous.upper() not in nomesPtSet:
                                aux_set.add(item)

                #se anterior for nome e seguinte tambem nome_completo
                else:
                    if item in conetoresNomes:
                        if previous.upper() in nomesPtSet and (nxt.upper() in nomesPtSet or nxt.upper() in apelidosPtSet) and previous[0].isupper():
                            nome_completo = previous + ' ' + item + ' ' + nxt
                            aux_set.add(nome_completo)

            #Antes: "Sexta, 04 de Maio 2018 22:38"
            #Depois: "04 Mai 2018"
            aux = (data.split(' '))
            dataAsKey = aux[1] + ' ' + aux[3][:3] + ' ' + aux[4]


            if dataAsKey in dict_JA:
                for elem in aux_set:
                    dict_JA[dataAsKey].append(elem)
            else:
                dict_JA[dataAsKey] = []
                for elem in aux_set:
                    dict_JA[dataAsKey].append(elem)
            #print('-------------')
            #print('PERSONS [DN] : ' + data.split('/')[0])
            #for pal in aux_set:
                #print(pal)

print(dict_JA)
json = json.dumps(dict_JA)
f=open("JA.json","w")
f.write(json)
f.close()"""

#_________________________CABO VERDE - A semana______________________________-

"""onlyfiles = [f for f in listdir('obter_colecoes/[CV] A_Semana/noticias/') if isfile(join('obter_colecoes/[CV] A_Semana/noticias/',f))]
dict_AS = {}
for filename in onlyfiles:
    aux_set = set ()
    #print(filename)
    path= 'obter_colecoes/[CV] A_Semana/noticias/' + filename
    tree = ET.parse(path)
    root = tree.getroot()
    data = "data Null"
    for child in root:
        if child.tag == "Date":
            data = child.text

        if child.tag == "Text":
            tokens = nltk.word_tokenize(child.text)
            #for pal in tokens:
            for previous, item, nxt in previous_and_next(tokens):
                if item[0].isupper() and item.upper() in nomesPtSet:
                    #nomeProprio + (nomeProprio || apelido)
                    if nxt.upper() in apelidosPtSet or nxt.upper() in nomesPtSet:
                        nome_completo = item + ' ' + nxt
                        aux_set.add(nome_completo)
                    else:
                        #se nao tem nome nem atras nem à frente
                        if previous:
                            if previous.upper() not in nomesPtSet:
                                aux_set.add(item)

                #se anterior for nome e seguinte tambem nome_completo
                else:
                    if item in conetoresNomes:
                        if previous.upper() in nomesPtSet and (nxt.upper() in nomesPtSet or nxt.upper() in apelidosPtSet) and previous[0].isupper():
                            nome_completo = previous + ' ' + item + ' ' + nxt
                            aux_set.add(nome_completo)

            #Antes: "\n02 Maio 2018\n"
            #Depois: "02 Mai 2018"
            aux = (data.split(' '))
            dataAsKey = aux[0].strip('\n') + ' ' + aux[1][:3] + ' ' + aux[2].strip('\n')


            if dataAsKey in dict_AS:
                for elem in aux_set:
                    dict_AS[dataAsKey].append(elem)
            else:
                dict_AS[dataAsKey] = []
                for elem in aux_set:
                    dict_AS[dataAsKey].append(elem)
            #print('-------------')
            #print('PERSONS [DN] : ' + data.split('/')[0])
            #for pal in aux_set:
                #print(pal)

print(dict_AS)
json = json.dumps(dict_AS)
f=open("AS.json","w")
f.write(json)
f.close()"""


#______________________________S.TOME - Tela_Non________________________
"""onlyfiles = [f for f in listdir('obter_colecoes/[ST] Tela_Non/noticias/') if isfile(join('obter_colecoes/[ST] Tela_Non/noticias/',f))]
dict_TN = {}
for filename in onlyfiles:
    aux_set = set ()
    #print(filename)
    path= 'obter_colecoes/[ST] Tela_Non/noticias/' + filename
    tree = ET.parse(path)
    root = tree.getroot()
    data = "data Null"
    for child in root:
        if child.tag == "Date":
            data = child.text

        if child.tag == "Text":
            tokens = nltk.word_tokenize(child.text)
            #for pal in tokens:
            for previous, item, nxt in previous_and_next(tokens):
                if item[0].isupper() and item.upper() in nomesPtSet:
                    #nomeProprio + (nomeProprio || apelido)
                    if nxt.upper() in apelidosPtSet or nxt.upper() in nomesPtSet:
                        nome_completo = item + ' ' + nxt
                        aux_set.add(nome_completo)
                    else:
                        #se nao tem nome nem atras nem à frente
                        if previous:
                            if previous.upper() not in nomesPtSet:
                                aux_set.add(item)

                #se anterior for nome e seguinte tambem nome_completo
                else:
                    if item in conetoresNomes:
                        if previous.upper() in nomesPtSet and (nxt.upper() in nomesPtSet or nxt.upper() in apelidosPtSet) and previous[0].isupper():
                            nome_completo = previous + ' ' + item + ' ' + nxt
                            aux_set.add(nome_completo)

            #Antes: "\n02 Maio 2018\n"
            #Depois: "02 Mai 2018"
            aux = (data.split(' '))
            dataAsKey = aux[0].strip('\n') + ' ' + aux[1][:3] + ' ' + aux[2].strip('\n')


            if dataAsKey in dict_TN:
                for elem in aux_set:
                    dict_TN[dataAsKey].append(elem)
            else:
                dict_TN[dataAsKey] = []
                for elem in aux_set:
                    dict_TN[dataAsKey].append(elem)
            #print('-------------')
            #print('PERSONS [DN] : ' + data.split('/')[0])
            #for pal in aux_set:
                #print(pal)

print(dict_TN)
json = json.dumps(dict_TN)
f=open("ST_TN.json","w")
f.write(json)
f.close()"""

#___________________________________TIMOR LESTE _______________________________________-
"""onlyfiles = [f for f in listdir('obter_colecoes/[TL] Governo Timor-Leste/noticias/') if isfile(join('obter_colecoes/[TL] Governo Timor-Leste/noticias/',f))]
dict_TLEST = {}
for filename in onlyfiles:
    aux_set = set ()
    #print(filename)
    path= 'obter_colecoes/[TL] Governo Timor-Leste/noticias/' + filename
    tree = ET.parse(path)
    root = tree.getroot()
    data = "data Null"
    for child in root:
        if child.tag == "Date":
            data = child.text

        if child.tag == "Text":
            tokens = nltk.word_tokenize(child.text)
            #for pal in tokens:
            for previous, item, nxt in previous_and_next(tokens):
                if item[0].isupper() and item.upper() in nomesPtSet:
                    #nomeProprio + (nomeProprio || apelido)
                    if nxt.upper() in apelidosPtSet or nxt.upper() in nomesPtSet:
                        nome_completo = item + ' ' + nxt
                        aux_set.add(nome_completo)
                    else:
                        #se nao tem nome nem atras nem à frente
                        if previous:
                            if previous.upper() not in nomesPtSet:
                                aux_set.add(item)

                #se anterior for nome e seguinte tambem nome_completo
                else:
                    if item in conetoresNomes:
                        if previous.upper() in nomesPtSet and (nxt.upper() in nomesPtSet or nxt.upper() in apelidosPtSet) and previous[0].isupper():
                            nome_completo = previous + ' ' + item + ' ' + nxt
                            aux_set.add(nome_completo)

            #Antes: "\nSeg. 19 de março de 2018, 10:35h\n"
            #Depois: "19 Mar 2018"
            aux = (data.split(' '))
            dataAsKey = aux[1] + ' ' + (aux[3][:3]).title() + ' ' + aux[5].strip(',')


            if dataAsKey in dict_TLEST:
                for elem in aux_set:
                    dict_TLEST[dataAsKey].append(elem)
            else:
                dict_TLEST[dataAsKey] = []
                for elem in aux_set:
                    dict_TLEST[dataAsKey].append(elem)
            #print('-------------')
            #print('PERSONS [DN] : ' + data.split('/')[0])
            #for pal in aux_set:
                #print(pal)

print(dict_TLEST)
json = json.dumps(dict_TLEST)
f=open("TL_TLEST.json","w")
f.write(json)
f.close()"""
