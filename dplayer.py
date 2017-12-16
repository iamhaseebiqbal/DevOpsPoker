#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
gregister_url='http://192.168.8.100:5001'
glocalip_adr='192.168.8.105'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys

from requests import put
import json

app = Flask(__name__)
api = Api(app)

# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):

    diamonds = 0
    spades = 0
    hearts = 0
    clubs = 0

    # check the suits of a card
    def __check_suits(self, card):
        if card[1] == 'd':
            self.diamonds = self.diamonds + 1
        elif card[1] == 's':
            self.spades = self.spades + 1
        elif card[1] == 'h':
            self.hearts = self.hearts + 1
        elif card[1] == 'c':
            self.clubs = self.clubs + 1

    # check the pairs in the card
    def __check_pair(self, hand, board):
        if hand[0][0] == hand[1][0]:
            return 1
        for card1 in hand:
            for card2 in board:
                if card1[0] == card2[0]:
                    return 1
        return 0

    def __check_royal_flush(self, cards):
        print('Royal Flush')
        currentSuit = cards[0][0]
        mismatchedCards = 0
        for card in cards:
            if currentSuit != card[1]:
                mismatchedCards += 1
        if mismatchedCards > 2:
            return -1
        royal_flush_cards = ['A', 'K', 'Q', 'J', '10'];
        allCardsInHand = ''
        for card in cards:
            allCardsInHand += card[0]
        for royal_card in royal_flush_cards:
            if royal_card not in allCardsInHand:
                return -1
        return 1

    def __bet_double(self, min_bid, max_bid):
        if 2*min_bid < max_bid :
            return 2*min_bid
        else :
            return max_bid

    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @return a dictionary containing the following values
    #         bid  : a number between 0 and max_bid
    def __get_bid(self, data):
        print('hand',data['hand'])
        # print('hand first card rank', data['hand'][0][0])
        # print('hand first card suits', data['hand'][0][1])

        round = len(data['board'])
        bidToReturn = data['min_bid']

        if round == 0:
            print("We are in the round", round)
            return bidToReturn
        elif round == 3:
            print("We are in the round", round)
            return bidToReturn
        elif round == 4:
            print("We are in the round", round)
            return bidToReturn
        elif round == 5:
            print("We are in the round", round)
            cards = data['hand'] + data['board']
            print('cards :',cards)
            # if we have 5 suits (flush)
            for card in cards:
                self.__check_suits(card)
            if self.diamonds == 5 or self.spades == 5 or self.hearts == 5 or self.clubs == 5:
                bidToReturn = self.__bet_double(data['min_bid'], data['max_bid'])

            # if we have pair
            pair = self.__check_pair(data['hand'], data['board'])
            print('pair', pair),
            if pair == 1:
                bidToReturn = self.__bet_double(data['min_bid'], data['max_bid'])

            #
            royal_flash = self.__check_royal_flush(cards)
            print(royal_flash)
            if royal_flash == 1 :
                bidToReturn = data['max_bid']
            print("test royal flush")
            self.__check_royal_flush(['A', 'K', 'Q', 'J', '10','2','2'])
            print(royal_flash)
        return bidToReturn

    # dispatch incoming get commands
    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)

        if command_id == 'get_bid':
            return {'bid': self.__get_bid(data)}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')

# main function
def main():

    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python3 dplayer bazinga 40001 x407
        """)
        return 0


    # register player
    r = put("%s/dpoker/v1/enter_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass':api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name or password')

    else:
        print('registration successful')

    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass': api_pass}).json()
# run the main function
if __name__ == '__main__':
    main()


