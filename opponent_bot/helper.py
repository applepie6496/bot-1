import random
from itertools import combinations

RANK = {r: i for i, r in enumerate("23456789TJQKA", start=2)}
SUITS = "cdhs"
RANKS = "23456789TJQKA"

ALL_CARDS = [r + s for r in RANKS for s in SUITS]
IDX5_OF_8 = list(combinations(range(8), 5))

_rank_cache = {}
_equity_cache = {}

def rank_five(cards):
    ranks = [RANK[c[0]] for c in cards]
    suits = [c[1] for c in cards]
    ranks.sort(reverse=True)

    flush = (suits[0] == suits[1] == suits[2] == suits[3] == suits[4])

    uniq = sorted(set(ranks), reverse=True)
    straight = False
    high = None
    if len(uniq) == 5:
        if uniq[0] - uniq[4] == 4:
            straight = True
            high = uniq[0]
        elif uniq == [14, 5, 4, 3, 2]:
            straight = True
            high = 5

    freq = {}
    for r in ranks:
        freq[r] = freq.get(r, 0) + 1
    groups = sorted(((c, r) for r, c in freq.items()), reverse=True)

    if flush and straight:
        return (8, high)
    if groups[0][0] == 4:
        four = groups[0][1]
        kicker = max(r for r in ranks if r != four)
        return (7, four, kicker)
    if groups[0][0] == 3 and groups[1][0] == 2:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, ranks)
    if straight:
        return (4, high)
    if groups[0][0] == 3:
        trips = groups[0][1]
        kickers = sorted((r for r in ranks if r != trips), reverse=True)
        return (3, trips, kickers)
    if groups[0][0] == 2 and groups[1][0] == 2:
        p1, p2 = groups[0][1], groups[1][1]
        hi, lo = (p1, p2) if p1 > p2 else (p2, p1)
        kicker = max(r for r in ranks if r != hi and r != lo)
        return (2, hi, lo, kicker)
    if groups[0][0] == 2:
        pair = groups[0][1]
        kickers = sorted((r for r in ranks if r != pair), reverse=True)
        return (1, pair, kickers)
    return (0, ranks)

def filtered_deck(exclude_set):
    return [c for c in ALL_CARDS if c not in exclude_set]

def best_rank_8(cards8):
    best = None
    for idx in IDX5_OF_8:
        rk = rank_five([cards8[i] for i in idx])
        if best is None or rk > best:
            best = rk
    return best

def best_rank_cached(cards8):
    key = tuple(sorted(cards8))
    v = _rank_cache.get(key)
    if v is None:
        v = best_rank_8(cards8)
        _rank_cache[key] = v
    return v

def iters_for(game_clock, board_len):
    if game_clock < 2:
        return 4
    if game_clock < 5:
        return 6
    if board_len >= 5:
        return 10
    if board_len >= 4:
        return 14
    if board_len >= 2:
        return 18
    return 22

def estimate_winning_p(my_cards, board_cards, game_clock, iters=30):

    iters = iters_for(game_clock, len(board_cards))
    key = (tuple(sorted(my_cards)), tuple(sorted(board_cards)), iters)
    v = _equity_cache.get(key)
    if v is not None:
        return v

    if len(my_cards) == 3:
        best = (-1.0, 0)
        for d in range(3):
            keep = [c for i, c in enumerate(my_cards) if i != d]
            p, _ = estimate_winning_p(keep, board_cards + [my_cards[d]], iters)
            if p > best[0]:
                best = (p, d)
        _equity_cache[key] = best
        return best

    exclude = set(my_cards) | set(board_cards)
    deck = filtered_deck(exclude)
    missing_board = 6 - len(board_cards)

    wins = ties = 0
    for _ in range(iters):
        sample = random.sample(deck, 2 + missing_board)
        opp = sample[:2]
        board = board_cards + sample[2:]

        my_rank = best_rank_cached(my_cards + board)
        opp_rank = best_rank_cached(opp + board)

        if my_rank > opp_rank:
            wins += 1
        elif my_rank == opp_rank:
            ties += 1

    res = ((wins + 0.5 * ties) / iters, -1)
    _equity_cache[key] = res
    return res
