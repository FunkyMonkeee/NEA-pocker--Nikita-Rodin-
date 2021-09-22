from random import shuffle


class Table:
    def __init__(self, number_of_players=3, number_of_ai=0, number_of_humans=3, min_bet=10):
        self.side_pots = [0 for i in range(number_of_players)]
        self.min_sum = 0
        self.table_deck = Deck()
        self.number_of_seats = number_of_players
        self.combination_value = []
        for player in range(number_of_players):
            self.combination_value.append(-1)
        self.middle_of_the_table = []
        self.suits_of_the_table = []
        self.values_of_the_table = []
        self.players = []
        self.small_blind = 0
        self.min_bet = min_bet
        self.big_blind_amount = min_bet
        for i in range(number_of_ai):
            self.players.append(AI())

        for i in range(number_of_humans):
            self.players.append(Human())

    def deal_cards(self):
        """deals cards to all players from a table_deck"""
        for player in self.players:
            hand = [self.table_deck.deal_a_card(), self.table_deck.deal_a_card()]
            player.get_hand(hand)

    def comb_check(self, player):
        if self.straight_flush(player):
            return self.straight_flush(player)
        elif self.four_of_a_kind(player):
            return self.four_of_a_kind(player)
        elif self.full_house(player):
            return self.four_of_a_kind(player)
        elif self.check_flush(player):
            return self.check_flush(player)
        elif self.check_straight(player):
            return self.check_straight(player)
        elif self.check_triple(player):
            return self.check_triple(player)
        elif self.check_two_pairs(player):
            return self.check_two_pairs(player)
        elif self.check_pair(player):
            return self.check_pair(player)
        else:
            return self.check_high_card(player)

    def check_high_card(self, player):
        hand_values = [card.get_value() for card in player.hand]
        return [0, max(hand_values)]

    def check_pair(self, player):
        """checks for a pair comb"""
        pair_val = 0
        hand_values = [card.get_value()for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 14):
            if local_val.count(value) == 2:
                pair_val =value
        if pair_val > 0:
            return [1, pair_val]
        else:
            return False

    def check_two_pairs(self, player):
        """checks for two-pair combination"""
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        pair_val = []
        for value in range(2, 14):
            if local_val.count(value) == 2:
                pair_val.append(value)
        if len(pair_val) > 1:
            return [2, 0]
        else:
            return False

    def check_triple(self, player):
        """checks for a triple combination"""
        pair_val = 0
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 14):
            if local_val.count(value) == 3:
                pair_val = value
        if pair_val > 0:
            return [3, pair_val]
        else:
            return False

    def check_straight(self, player):
        """checks for a straight combination"""
        lowest_card = 0
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        local_val.sort()
        cards_in_a_row = 1
        for ind in range(1, len(local_val)):
            if local_val[ind] == local_val[ind-1] + 1:
                cards_in_a_row += 1
            else:
                cards_in_a_row = 1
            if cards_in_a_row >= 5:
                lowest_card = local_val[ind-4]
        if cards_in_a_row >= 5:
            return [4, lowest_card]

    def check_flush(self, player):
        """checks for a flush combination"""
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        hand_suits = [card.get_suit() for card in player.hand]
        local_suits = self.values_of_the_table + hand_suits
        flush_instance = False
        highest = 0
        suit = ''
        for s in ('H', 'C', "S", "D"):
            if local_suits.count(s) >= 5:
                suit = s
                flush_instance = True
                for card in zip(local_val, local_suits):
                    if card[1] == s and card[0] > highest:
                        highest = card[0]
        if flush_instance:
            return [5, highest, s]

    def full_house(self, player):
        """checks for a full house combination"""
        pair = self.check_pair(player)
        triple = self.check_triple(player)
        if pair and triple:
            return [6, 0]

    def four_of_a_kind(self, player):
        """checks for four of a kind cobination"""
        pair_val = 0
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 14):
            if local_val.count(value) == 4:
                pair_val = value
        if pair_val > 0:
            return [7, pair_val]
        else:
            return False

    def straight_flush(self, player):
        """checks for a straight-flush"""
        straight = self.check_straight(player)
        flush = self.check_flush(player)
        if flush and straight:
            loc_list = []
            hand_values = [card.get_value() for card in player.hand]
            local_val = self.values_of_the_table + hand_values
            hand_suits = [card.get_suit() for card in player.hand]
            local_suits = self.values_of_the_table + hand_suits
            straight_flush_instance = False
            for ind in range(len(local_val)):
                if local_suits[ind] == flush[3]:
                    loc_list.append(local_val[ind])
            local_val.sort()
            if local_val[-1] - local_val[-5] == 4:
                return [9, local_val[-1]]

    def flop(self):
        """puts three cards in the middle of the table and adds values and suits to separate lists for access of bots"""
        for i in range(3):
            card = self.table_deck.deal_a_card()
            self.middle_of_the_table.append(card)
            self.suits_of_the_table.append(card.get_suit())
            self.values_of_the_table.append(card.get_value())
        self.betting()

    def turn(self):
        """puts one card in the middle of the table and adds value and suit to separate lists for access of bots"""
        card = self.table_deck.deal_a_card()
        self.middle_of_the_table.append(card)
        self.suits_of_the_table.append(card.get_suit())
        self.values_of_the_table.append(card.get_value())
        self.betting()

    def river(self):
        card = self.table_deck.deal_a_card()
        self.middle_of_the_table.append(card)
        self.suits_of_the_table.append(card.get_suit())
        self.values_of_the_table.append(card.get_value())
        self.betting()
        self.distribute_a_win()

    def betting(self):
        """makes a round of betting among all of the players"""
        raise_maker = -1
        player_num = 0
        while player_num < self.number_of_seats:
            if self.players[player_num].fold_state or self.players[player_num].all_in_state or player_num == raise_maker:
                player_num += 1
            else:
                resp = self.players[player_num].place_a_bet(self.min_sum, self, player_num)
                if resp is False:
                    #fold event
                    player_num += 1
                elif resp > self.min_sum:
                    #raise event
                    raise_maker = player_num
                    self.min_sum = resp
                    add = resp + self.side_pots[player_num]
                    self.side_pots[player_num] = add
                    if player_num != 0:
                        player_num = 0
                    else:
                        player_num += 1
                elif self.side_pots[player_num] + resp < self.min_sum and self.players[player_num].budget == 0:
                    #all_in_event
                    add = resp + self.side_pots[player_num]
                    self.side_pots[player_num] = add
                    player_num += 1
                elif self.side_pots[player_num] + resp == self.min_sum:
                    #call_event
                    add = resp + self.side_pots[player_num]
                    self.side_pots[player_num] = add
                    player_num += 1



    def pre_flop(self):
        """deals cards and makes preflop bets"""
        self.deal_cards()
        self.betting()

    def check_win(self):
        """after river betting determines a winner"""
        comb_list = []
        for ind in range(len(self.players)):
            if self.players[ind].fold_state:
                comb_list.append([-1])
            else:
                comb_list.append(self.comb_check(self.players[ind]))
        return comb_list

    def distribute_a_win(self):
        """after a round of poker it distributes win to players"""
        #create a list of winners
        winner = 0
        winner_comb = -1
        winner_high_card = -1
        win_list = self.check_win()
        copy_of_bets = self.side_pots[:]
        while sum(self.side_pots) > 0:
            print(self.side_pots)
            winner_num = 1
            for obj in range(len(win_list)):
                if win_list[obj][0] > winner_comb:
                    winner_comb = win_list[obj][0]
                    winner = obj
                    winner_high_card = win_list[obj][1]
                elif win_list[obj][0] == winner_comb:
                    if win_list[obj][1] > winner_high_card:
                        winner = obj
                        winner_high_card = win_list[obj][1]
                    elif win_list[obj][1] == winner_high_card:
                        var = self.kicker(player_1=self.players[winner], player_2=self.players[obj])
                        if var == 2:
                            winner = obj
                        elif var == 0:
                            winner_num += 1
            # This part is going to be reworked
            val = self.side_pots[winner]//winner_num
            win = 0
            for ind in range(len(self.side_pots)):
                if val >= self.side_pots[ind]:
                    win += self.side_pots[ind]
                    self.side_pots[ind] = 0
                else:
                    win += val
                    self.side_pots[ind] -= val
            self.players[winner].get_a_win(win)
            win_list[winner] = [-1, -1]

    def kicker(self, player_1, player_2):
        max_1 = max([card_val.get_value() for card_val in player_1.ret_hand()])
        max_2 = max([card_val.get_value() for card_val in player_2.ret_hand()])
        if max_1 == max_2:
            return 0
        if max_1 > max_2:
            return 1
        else:
            return 2

    def one_game(self):
        """a round of poker"""
        round_continues = True
        self.pre_flop()
        abs_winner = self.check_for_absolute_winner()
        if not abs_winner:
            self.flop()
        else:
            self.get_everything(abs_winner)
        if not abs_winner:
            self.turn()
        else:
            self.get_everything(abs_winner)
        if not abs_winner:
            self.river()
        else:
            self.get_everything(abs_winner)

    def check_for_absolute_winner(self):
        not_folded = []
        for ind in range(len(self.players)):
            if not self.players[ind].fold_state:
                not_folded.append(ind)
        if len(not_folded) == 1:
            return not_folded[0]
        else:
            return False

    def get_everything(self, player_num):
        summm = 0
        for val in self.side_pots:
            summm+=val
        self.side_pots = [0 for i in range(self.number_of_seats)]
        self.players[player_num].get_a_win(summm)


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def get_suit(self):
        return self.suit

    def get_value(self):
        return self.value


class Deck:
    def __init__(self):
        self.card_list  = []
        suits = ('H', 'C', "S", "D")
        values = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
        for suit in suits:
            for value in values:
                self.card_list.append(Card(suit, value))

    def deal_a_card(self):
       shuffle(self.card_list)
       card = self.card_list.pop()
       return card


class Player:
    def __init__(self, budget=1000):
        self.hand = []
        self.budget = budget
        self.fold_state = False
        self.all_in_state = False

    def get_hand(self, cards):
        self.hand = cards

    def ret_hand(self):
        return self.hand

    def get_a_win(self, value):
        self.budget += value


class Human(Player):
    def __init__(self, budget=1000):
        Player.__init__(self, budget)

    def place_a_bet(self, money_to_play, table, player_num):
        choice = input(f"""      Money to play: {money_to_play}
        You have: {self.budget} chips
        hand: {[[card_val.get_value(), card_val.get_suit()] for card_val in self.ret_hand()]}
        table: {table.suits_of_the_table, table.values_of_the_table}
        your side_pot: {table.side_pots[player_num]}
        your number = {player_num}
        1) fold
        2) check/call
        3) raise/bet
        4) all in
        """)
        if choice == "1":
            self.fold_state = True
            return False
        if choice == "2":
            self.budget = self.budget - (money_to_play - table.side_pots[player_num])
            if self.budget <= 0:
                self.all_in_state = True
            return money_to_play - table.side_pots[player_num]
        if choice == "3":
            rais_e = int(input('enter the amount you want to raise'))
            self.budget -= (money_to_play - table.side_pots[player_num] + rais_e)
            return money_to_play - table.side_pots[player_num] + rais_e
        if choice == '4':
            self.all_in_state = True
            ret = self.budget
            self.budget = 0
            return ret

    def show_hand(self):
        hand = []
        for card in self.hand:
            hand.append([card.get_value(), card.get_suit])

    def show_table(self):
        pass

    def show_budget(self):
        pass


class AI(Player):
    def __init__(self, budget=1000, agressiveness=5, riskiness=5, bluffing_frequency=5):
        Player.__init__(self, budget)
        self.agressiveness = agressiveness
        self.riskiness = riskiness
        self.bluffing_frequency = bluffing_frequency
    def place_a_bet(self):
        pass


def main():
    main_table = Table()
    main_table.one_game()
    print([player.budget for player in main_table.players])

main()
