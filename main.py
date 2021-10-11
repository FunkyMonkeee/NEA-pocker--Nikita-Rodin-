from random import shuffle, randint
import matplotlib.pyplot as plt

class Table:
    def __init__(self, number_of_players=3, number_of_humans=3, min_bet=10):
        self.side_pots = [0 for i in range(number_of_players)]
        self.list_of_players_copy = []
        self.possibility_of_winning = [0 for i in range(number_of_players)]
        self.round_raises = [0 for i in range(number_of_players)]
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
        self.data = []
        self.min_bet = min_bet
        self.big_blind_amount = min_bet
        number_of_players_to_init = 0
        for i in range(number_of_humans):
            player = Human(number_of_players_to_init)
            self.players.append(player)
            number_of_players_to_init += 1

    def clean_the_table(self):
        self.table_deck = Deck()
        for player in self.players:
            player.fold_state = False
            player.all_in_state = False
            player.clean_hand()
        self.values_of_the_table = []
        self.suits_of_the_table = []
        self.middle_of_the_table = []
        self.side_pots = [0 for i in range(len(self.players))]
        self.possibility_of_winning = [0 for player in self.players]
        self.min_sum = 0

    def add_an_ai(self):
        choice = input("""what AI do you want to add?:
        1) random_AI
        2) customisable_AI
        Your choice: """)
        if choice == '1':
            agr = int(input('how agressive do you want AI to be on the scale from 1 to 10?'))
            rnd_ai = Random_AI(aggressiveness=agr, player_num=len(self.players))
            self.players.append(rnd_ai)
        elif choice == '2':
            agr = int(input('how aggressive do you want AI to be on the scale from 1 to 10?'))
            risk = int(input('how risky do you want AI to be on the scale from 1 to 10?'))
            bluff_frequency = int(input('how frequently do you want AI to bluff on the scale from 1 to 10?'))
            rnd_ai = Changable_AI(aggressiveness=agr, bluffing_frequency=bluff_frequency, riskiness=risk, player_num=len(self.players))
            self.players.append(rnd_ai)

    def reset_players(self):
        for player in self.list_of_players_copy:
            player.budget = 1000
            player.fold_state = False
            player.all_in_state = False
        self.players = self.list_of_players_copy[:]

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
            return self.full_house(player)
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
        return [1, max(hand_values)]

    def check_pair(self, player):
        """checks for a pair comb"""
        pair_val = 0
        hand_values = [card.get_value()for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 15):
            if local_val.count(value) == 2:
                pair_val = value
        if pair_val > 0:
            return [2, pair_val]
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
            return [3, 0]

    def check_triple(self, player):
        """checks for a triple combination"""
        pair_val = 0
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 14):
            if local_val.count(value) == 3:
                pair_val = value
        if pair_val > 0:
            return [4, pair_val]

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
            return [5, lowest_card]
        else:
            return False

    def check_flush(self, player):
        """checks for a flush combination"""
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        hand_suits = [card.get_suit() for card in player.hand]
        local_suits = self.suits_of_the_table + hand_suits
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
            return [6, highest, s]
        else:
            return False

    def full_house(self, player):
        """checks for a full house combination"""
        pair = self.check_pair(player)
        triple = self.check_triple(player)
        if pair and triple:
            return [7, 0]
        else:
            return False

    def four_of_a_kind(self, player):
        """checks for four of a kind cobination"""
        pair_val = 0
        hand_values = [card.get_value() for card in player.hand]
        local_val = self.values_of_the_table + hand_values
        for value in range(2, 14):
            if local_val.count(value) == 4:
                pair_val = value
        if pair_val > 0:
            return [8, pair_val]
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
            local_suits = self.suits_of_the_table + hand_suits
            straight_flush_instance = False
            for ind in range(len(local_val)):
                if local_suits[ind] == flush[2]:
                    loc_list.append(local_val[ind])
            local_val.sort()
            if local_val[-1] - local_val[-5] == 4:
                return [9, local_val[-1]]
            else:
                return False

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
        self.distribute_a_win(sum(self.side_pots))

    def betting(self):
        """makes a round of betting among all of the players"""
        raise_maker = -1
        player_num = 0
        all_fold = False
        while player_num < len(self.players):
            if self.players[player_num].fold_state or self.players[player_num].all_in_state or player_num == raise_maker:
                player_num += 1
            elif not self.players[player_num].fold_state:
                # what if everybody folds?
                folded = 0
                for player in self.players:
                    if player.fold_state:
                        folded += 1
                if folded + 1 == len(self.players):
                    self.side_pots[player_num] += self.players[player_num].get_all_the_money_from_budget()
                    all_fold = True
                    break
                else:
                    resp = self.players[player_num].place_a_bet(money_to_play=self.min_sum, table=self, player_num=player_num)
                    if resp is False:
                        # fold event
                        player_num += 1
                    elif self.side_pots[player_num] + resp > self.min_sum:
                        # raise event
                        raise_maker = player_num
                        self.round_raises[player_num] += resp
                        self.min_sum = resp + self.side_pots[player_num]
                        add = resp + self.side_pots[player_num]
                        self.side_pots[player_num] = add
                        if player_num != 0:
                            player_num = 0
                        else:
                            player_num += 1
                    elif self.side_pots[player_num] + resp < self.min_sum and self.players[player_num].budget == 0:
                        # all_in_event
                        add = resp + self.side_pots[player_num]
                        self.side_pots[player_num] = add
                        self.round_raises[player_num] += resp
                        self.players[player_num].all_in_state = True
                        player_num += 1

                    elif self.side_pots[player_num] + resp == self.min_sum:
                        # call_event
                        add = resp + self.side_pots[player_num]
                        self.side_pots[player_num] = add
                        self.round_raises[player_num] += resp
                        player_num += 1

        if not all_fold:
            not_raise_num = self.round_raises.count(0)
            raise_num = self.number_of_seats - not_raise_num
            for ind in range(self.number_of_seats):
                self.possibility_of_winning[ind] += self.round_raises[ind]*raise_num
            self.round_raises = [0 for i in range(len(self.players))]

    def pre_flop(self):
        """deals cards and makes preflop bets"""
        self.clean_the_table()
        self.deal_cards()
        self.betting()

    def check_win(self):
        """after river betting determines a winner"""
        comb_list = []
        for ind in range(len(self.players)):
            if self.players[ind].fold_state:
                comb_list.append([-1, -1])
            else:
                comb_list.append(self.comb_check(self.players[ind]))
        return comb_list

    def distribute_a_win(self, total):
        """after a round of poker it distributes win to players"""
        # create a list of winners
        winners = []
        total = total
        winner_comb = -1
        winner_high_card = -1
        win_list = self.check_win()
        copy_of_bets = self.side_pots[:]
        for ind in range(len(self.players)):
            if not self.players[ind].fold_state:
                if win_list[ind][0] > winner_comb:
                    winner_comb = win_list[ind][0]
                    winner_high_card = win_list[ind][1]
                    winners = [ind]
                elif win_list[ind][0] == winner_comb:
                    if winner_high_card < win_list[ind][1]:
                        winner_high_card = win_list[ind][1]
                        winners = [ind]
                    elif winner_high_card == win_list[ind][1]:
                        winners.append(ind)
        number_of_winners = len(winners)
        each_winners_win = total//number_of_winners
        if each_winners_win <= 1:
            return 0
        else:
            for player in winners:
                if self.possibility_of_winning[player] > each_winners_win:
                    self.players[player].get_a_win(each_winners_win)
                    self.possibility_of_winning[player] -= each_winners_win
                    total -= each_winners_win
                elif self.possibility_of_winning[player] == each_winners_win:
                    self.players[player].get_a_win(each_winners_win)
                    self.players[player].fold_state = True
                    total -= each_winners_win
                else:
                    self.players[player].get_a_win(self.possibility_of_winning[player])
                    self.players[player].fold_state = True
                    total -= self.possibility_of_winning[player]
            if total > 0:
                self.distribute_a_win(total)

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
        self.pre_flop()
        abs_winner = self.check_for_absolute_winner()
        if not abs_winner:
            self.flop()
            abs_winner = self.check_for_absolute_winner()
        else:
            abs_winner.get_a_win(sum(self.side_pots))
            return 0
        if not abs_winner:
            self.turn()
            abs_winner = self.check_for_absolute_winner()
        else:
            abs_winner.get_a_win(sum(self.side_pots))
            return 0
        if not abs_winner:
            self.river()
        else:
            abs_winner.get_a_win(sum(self.side_pots))
            return 0

    def check_for_absolute_winner(self):
        folds = 0
        player_to_ret = 0
        for player in self.players:
            if player.fold_state:
                folds += 1
            else:
                player_to_ret = player
        if len(self.players) == folds + 1:
            return player_to_ret
        else:
            return False

    def play_and_record(self, num_of_games):
        dict_of_budgets = {}
        for player in self.list_of_players_copy:
            dict_of_budgets[player.player_num] = [player.budget]
        for game in range(num_of_games):
            self.one_game()
            for player in self.list_of_players_copy:
                dict_of_budgets[player.player_num].append(player.budget)
                if player.budget <= 0 and player in self.players:
                    self.players.remove(player)
                    self.number_of_seats -= 1
            if len(self.players) == 1:
                break
        return dict_of_budgets

    def plot_graphs(self):
        pass


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
        self.card_list = []
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
    def __init__(self, player_num ,budget=1000):
        self.hand = []
        self.budget = budget
        self.fold_state = False
        self.all_in_state = False
        self.player_num = player_num

    def get_hand(self, cards):
        self.hand = cards

    def ret_hand(self):
        return self.hand

    def get_a_win(self, value):
        self.budget += value

    def clean_hand(self):
        self.hand = []

    def get_all_the_money_from_budget(self):
        budg = self.budget
        self.budget = 0
        return budg

class Human(Player):
    def __init__(self, player_num,  budget=1000):
        Player.__init__(self,player_num=player_num, budget = budget)

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


class Changable_AI(Player):
    def __init__(self, player_num, budget=1000, aggressiveness=5, riskiness=5, bluffing_frequency=5,):
        Player.__init__(self, budget)
        self.aggressiveness = aggressiveness
        self.player_num = player_num
        self.riskiness = riskiness
        self.bluffing_frequency = bluffing_frequency

    def place_a_bet(self, money_to_play, table, player_num):
        pass


class Random_AI(Player):
    def __init__(self, aggressiveness, player_num,  budget=1000):
        Player.__init__(self, player_num=player_num, budget=budget)
        self.aggressiveness = aggressiveness

    def place_a_bet(self, table, money_to_play, player_num):
        to_fold_or_not_to_fold = randint(1, self.aggressiveness)
        if to_fold_or_not_to_fold == 1:
            if money_to_play - table.side_pots[player_num] == 0:
                return 0
            else:
                self.fold_state = True
                return False
        elif randint(1, 2) == 1:
            ret = table.min_sum - table.side_pots[player_num]
            if ret > self.budget:
                ret = self.budget
                self.budget = 0
                return ret
            else:
                self.budget -= ret
                return ret
        else:
            if table.min_sum - table.side_pots[player_num] <= self.budget:
                ret = randint(table.min_sum - table.side_pots[player_num], self.budget)
                self.budget -= ret
                return ret
            else:
                ret = self.budget
                self.budget -= ret
                return ret


def main():
    main_table = create_a_table()
    menu(main_table)


def menu(table):
    while True:
        choice = input("""
        1) play in a current state
        2) test
        3) remake state
        4) quit
        your choice: """)
        if choice == "1":
            table.one_game()
        elif choice == "2":
            num_of_games = int(input("how many games do you want to play?"))
            table.data = table.play_and_record(num_of_games)
            print(table.data)
        elif choice == "3":
            table.reset_players()
        elif choice == "4":
            break


def create_a_table():
    number_of_players = int(input('how many players do you want in a simulation'))
    number_of_humans = int(input('how many humans do you want in a simulation: '))
    big_blind = int(input('what is the big blind in a simulation: '))
    table = Table(number_of_players=number_of_players, number_of_humans=number_of_humans, min_bet=big_blind)
    for count in range(number_of_players-number_of_humans):
        table.add_an_ai()
    table.list_of_players_copy = table.players[:]
    return table

main()