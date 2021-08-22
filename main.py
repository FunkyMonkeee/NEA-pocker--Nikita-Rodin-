class Table:
    def __init__(self, number_of_players = 2):
        self.table_deck = Deck
        self.number_of_seats = number_of_players
        self.middle_of_the_table= []
        self.pot = 0



class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value


    def get_suit(self):
        return self.suit


    def get_value(self):
        return self.value

class  Deck:
    def __init__(self):
        self.card_list  = []
        suits  = ('H', 'C', "S", "D")
        values = (2, 3, 4 , 5 , 6 , 7, 8 , 9, 10, 11, 12, 13, 14)
        for suit in suits:
            for  value in  values:
                self.card_list.append(Card(suit, value))

class Player:
    pass

def main():

if __name__ == "main":
    main()
