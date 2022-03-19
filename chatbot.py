import discord
import random
import json
import pickle
from unittest import result
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
riddles = json.loads(open('tebak.json').read())

words = pickle.load(open('words.pk1', 'rb'))
classes = pickle.load(open('classes.pk1', 'rb'))
model = load_model('chatbotmodel.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.99
    results = [[i, r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

def request(message):
    ints = predict_class(message)
    res = ""
    if ints:
        res = get_response(ints, intents)
    
    return res

def flipping_coin(message):
    coin = random.randint(0, 1)
    if coin == 0 and message == "head":
        response = "Congrats it's a head."
    elif coin == 1 and message == "tail":
        response = "Congrats it's a tail."
    else:
        response = "Unlucky, you got it wrong"
    return response

client = discord.Client()

isFlipping = False
index = 0
isAnswering = False

questions = []
answers = []
for riddle in riddles['riddles']:
    questions.append(riddle['question'])
    answers.append(riddle['answer'])

@client.event
async def on_message(message):
    global isFlipping
    global isAnswering
    global index
    if message.author == client.user:
        return
    if isFlipping and (message.content.lower() == 'head' or message.content.lower() == 'tail'):
        response = flipping_coin(message.content.lower())
        isFlipping = False
        await message.channel.send(response)
        return
    else:
        isFlipping = False

    if isAnswering:
        response = answers[index]
        index = index + 1
        isAnswering = False
        await message.channel.send(response)
        return
    
    if message.content.startswith("$about"):
        response = "Assalamualaikum, scuffed discord chat bot." + "\n" + "Mohon maaf, budi masih punya banyak salah, tolong jangan bully budi ya guys." + "\n" + "Nanti budi bakal gantung diri kalo di bully terus." + "\n" + \
            "commend:" + "\n" + "-> budi soal" + \
            "\n" + "-> budi flip"
        await message.channel.send(response)
    if message.content.lower().startswith("budi"):
        if message.content[5:].lower() == "soal":
            response = questions[index]
            isAnswering = True
            await message.channel.send(response)
        if message.content[5:].lower() == "flip":
            response = "Pilih salah satu:" + "\n" + "head" + "\n" + "tail"
            isFlipping = True
            await message.channel.send(response)
    else:
        response = request(message.content[:])
        if response:
            await message.channel.send(response)

client.run('OTUzNTE3Mzc5MjczNTIzMjAx.YjFuQg.e321caWAlk7KtYs65MvGa8CggnE')
