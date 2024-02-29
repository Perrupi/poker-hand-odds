from poker.hand import Hand, Range
from treys import Evaluator, Card
from itertools import combinations
import math
from concurrent.futures import ThreadPoolExecutor


# Function to calculate the strength of a poker hand
def get_hand_rank(hand, verbose=1):
    """
    Calculate the strength of a poker hand.

    Parameters:
    hand (list): A list representing a poker hand.
    verbose (int): A flag for printing additional information.

    Returns:
    tuple: A tuple containing the calculated hand rank and the total number of possible hands.
    """
    all_hands = list(Hand)
    hanD = Range("".join(hand))
    hanD = hanD.hands[0]
    try:
        rank = len(all_hands)-all_hands.index((hanD)), len(all_hands)
        if verbose > 0:
            print(f"Hand {Range(''.join(hand))} has a rank {rank[0]}/{rank[1]} => {int(rank[0]/rank[1]*100)}%")
        return rank, len(all_hands)
    except:
        if verbose > 0:
            print(f"Hand {Range(''.join(hand))} does not exist therefore has rank: {999}/{169}")
        return 999, len(all_hands)


# Function to calculate the strength of a poker hand with a given board
def get_hand_rank_board(hand, board, verbose=1):
    """
    Calculate the strength of a poker hand with a given board.

    Parameters:
    hand (list): A list representing a poker hand.
    board (list): A list representing the community cards on the board.
    verbose (int): A flag for printing additional information.

    Returns:
    tuple: A tuple containing the calculated hand rank and the total possible ranks.
    """
    if len(board) == 0 : return get_hand_rank(hand)
    if len(board)>5:
        return 999, 7642
    phand = [
        Card.new(hand[0]),
        Card.new(hand[1])
    ]
    pboard=[]
    for card in board:
        pboard.append(Card.new(card))
    evaluator = Evaluator()
    if verbose > 0:
        print(f"The board-hand combination: ")
        Card.print_pretty_cards(phand + pboard)
        print(f"has a rank {evaluator.evaluate(pboard, phand)}/7642 => {int(evaluator.evaluate(pboard, phand)/7642*100)}%")
    return evaluator.evaluate(pboard, phand), 7642


# Function to calculate combinations of n elements taken r at a time
def combinations_n_r(n, r):
    """
    Calculate combinations of n elements taken r at a time.

    Parameters:
    n (int): Total number of elements.
    r (int): Number of elements to choose.

    Returns:
    int: Number of combinations.
    """
    return int(math.factorial(n)/(math.factorial(n-r)*math.factorial(r)))


# Function to process a new hand and compare its rank with the current hand
def process_hand(new_hand, board, current_hand_rank):
    """
    Process a new hand and compare its rank with the current hand.

    Parameters:
    new_hand (tuple): A tuple representing a new poker hand.
    board (list): A list representing the community cards on the board.
    current_hand_rank (int): The rank of the current hand.

    Returns:
    tuple: A tuple containing flags indicating whether the new hand is better, equal, or worse.
    """
    tmp_hand_rank = get_hand_rank_board(new_hand, board, verbose=0)
    if tmp_hand_rank[0] < current_hand_rank:
        return 1, 0
    elif tmp_hand_rank[0] == current_hand_rank:
        return 0, 1
    else:
        return 0, 0


# Function to calculate hypergeometric probability
def hypergeometric(pN, qN, k, n, N):
    """
    Calculate hypergeometric probability.

    Parameters:
    pN (int): Population size of the first type.
    qN (int): Population size of the second type.
    k (int): Number of successful draws.
    n (int): Number of draws.
    N (int): Total number of items in the population.

    Returns:
    float: Hypergeometric probability.
    """
    numerator = math.comb(pN, k) * math.comb(qN, n-k)
    denominator = math.comb(N, n)

    return numerator / denominator


# Function to get poker odds using threads for parallel processing
def get_poker_odds_threads(hand, board, number_of_players, verbose=1):
    """
    Get poker odds using threads for parallel processing.

    Parameters:
    hand (list): A list representing a poker hand.
    board (list): A list representing the community cards on the board.
    number_of_players (int): Total number of players.
    verbose (int): A flag for printing additional information.

    Returns:
    tuple: A tuple containing the count of better hands, count of equal hands, and calculated odds.
    """
    current_hand_rank = get_hand_rank_board(hand, board, verbose=verbose)[0]
    deck = [
    "Ac", "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc",
    "Ad", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd",
    "Ah", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh",
    "As", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks"
    ]
    for card in hand + board:
        deck.remove(card)
    total_count = combinations_n_r(len(deck), 2)
    count_better = 0
    count_equal = 0  
    num_threads = 5
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Using list comprehension to generate the list of futures
        futures = [executor.submit(process_hand, new_hand, board, current_hand_rank) for new_hand in combinations(deck, 2)]

        # Extracting results from futures
        for future in futures:
            better, equal = future.result()
            count_better += better
            count_equal += equal

    n_players = number_of_players-1  # Number of players
    K_interesting_population = count_better  # Interesting population
    N_total_population = total_count  # Total population size
    odds = 1-hypergeometric(pN=K_interesting_population, qN=N_total_population-K_interesting_population, k=0, n=n_players, N=N_total_population)
    if verbose > 0:
            phand = [
            Card.new(hand[0]),
            Card.new(hand[1])
            ]
            pboard=[]
            for card in board:
                pboard.append(Card.new(card))
            print(f"For the board-hand combination: ")
            Card.print_pretty_cards(phand + pboard)
            print(f"there are {count_better} possible hands that are better", end="")
            if count_equal>0:
                print(f", and {count_equal} possible hands that are just as good.")
            else:
                print(f".")
            print(f"For {number_of_players} players this equals to {odds:.3f}% of chances of winning this round.")
    odds_5f = round(odds % 1, 5) + math.floor(odds)
    return (count_better), (count_equal), odds_5f


# Function to get poker odds without threads
def get_poker_odds(hand, board, number_of_players, verbose=1):
    """
    Get poker odds without using threads.

    Parameters:
    hand (list): A list representing a poker hand.
    board (list): A list representing the community cards on the board.
    number_of_players (int): Total number of players.
    verbose (int): A flag for printing additional information.

    Returns:
    tuple: A tuple containing the count of better hands, count of equal hands, and calculated odds.
    """
    current_hand_rank = get_hand_rank_board(hand, board, verbose=verbose)[0]
    deck = [
    "Ac", "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc",
    "Ad", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd",
    "Ah", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh",
    "As", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks"
    ]
    for card in hand + board:
        deck.remove(card)
    total_count = combinations_n_r(len(deck), 2)
    count_better = 0
    count_equal = 0
    for new_hand in combinations(deck, 2):
        tmp_hand_rank = get_hand_rank_board(new_hand, board, verbose=0)
        if tmp_hand_rank[0] < current_hand_rank:
            count_better += 1
        elif tmp_hand_rank[0] == current_hand_rank:
            count_equal += 1

    n_players = number_of_players-1  # Number of players
    K_interesting_population = count_better  # Interesting population
    N_total_population = total_count  # Total population size
    odds = hypergeometric(pN=K_interesting_population, qN=N_total_population-K_interesting_population, k=0, n=n_players, N=N_total_population) * 100
    if verbose > 0:
            phand = [
            Card.new(hand[0]),
            Card.new(hand[1])
            ]
            pboard=[]
            for card in board:
                pboard.append(Card.new(card))
            print(f"For the board-hand combination: ")
            Card.print_pretty_cards(phand + pboard)
            print(f"there are {count_better} possible hands that are better", end="")
            if count_equal>0:
                print(f", and {count_equal} possible hands that are just as good.")
            else:
                print(f".")
            print(f"For {number_of_players} players this equals to {odds:.5f}% of chances of winning this round.")
    odds_5f = round(odds % 1, 5) + math.floor(odds)
    
    return (count_better), (count_equal), odds_5f