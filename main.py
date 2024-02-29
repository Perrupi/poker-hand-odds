from back import get_poker_odds, get_poker_odds

def main():
    hand = ["Kc", "6c"]
    board = ["Ts", "2c", "Tc", "2d", "Jc"]
    number_of_players = 3
    # time0 = time.time()
    odds = get_poker_odds(hand, board, number_of_players, verbose = 0)
    # print(f"Program took {time.time()-time0}s to execute.")
    print(odds)
    
    hand = ["Ac", "Ad"]
    board = ["As", "Ah", "Tc", "2d", "Jc"]
    number_of_players = 3
    # time0 = time.time()
    odds = get_poker_odds(hand, board, number_of_players, verbose = 0)
    # print(f"Program took {time.time()-time0}s to execute.")
    print(odds)

if __name__ == '__main__':
    main()