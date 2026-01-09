from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction


def card_value(card):
    rank = card[0]
    value = {
        'A': 14,
        'K': 13,
        'Q': 12,
        'J': 11,
        'T': 10,
        '9': 9,
        '8': 8,
    }
    if rank in value:
        return value[rank]
    else:
        return int(rank)


def get_hand_strength(hand, board):
    all_cards = hand + board

    if not all_cards:
        return 0

    ranks = [card[0] for card in all_cards]
    suits = [card[1] for card in all_cards]

    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    suit_counts = {}
    for suit in suits:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    counts = sorted(rank_counts.values(), reverse=True)
    max_suit_count = max(suit_counts.values()) if suit_counts else 0

    if counts[0] >= 4:
        return 95

    if len(counts) >= 2 and counts[0] >= 3 and counts[1] >= 2:
        return 90

    if max_suit_count >= 5:
        return 85

    if counts[0] >= 3:
        return 75

    if len(counts) >= 2 and counts[0] >= 2 and counts[1] >= 2:
        return 65

    if counts[0] >= 2:
        return 55

    if hand:
        max_card_value = max(card_value(card) for card in hand)
        return max(0, (max_card_value - 2) * 4)

    return 0


def choose_discard(hand):
    if not hand:
        return 0

    min_value = float('inf')
    min_index = 0

    for i, card in enumerate(hand):
        value = card_value(card)
        if value < min_value:
            min_value = value
            min_index = i

    return min_index


def get_betting_action(hand, board, street, continue_cost, stack, legal_actions):
    strength = get_hand_strength(hand, board)

    if continue_cost == 0:
        if strength >= 55 and RaiseAction in legal_actions:
            return 'raise'
        if CheckAction in legal_actions:
            return 'check'
        return 'fold'

    if stack > 0 and continue_cost > 0 and continue_cost < stack * 0.05:
        if CallAction in legal_actions:
            return 'call'
        return 'fold'

    if street == 0:
        if strength >= 55 and RaiseAction in legal_actions:
            return 'raise'
        elif strength >= 32 and RaiseAction in legal_actions:
            return 'raise'
        elif strength >= 24:
            if CallAction in legal_actions:
                return 'call'
            return 'fold'
        else:
            return 'fold'

    if strength >= 55 and RaiseAction in legal_actions:
        return 'raise'
    elif strength >= 40:
        if CallAction in legal_actions:
            return 'call'
        return 'fold'
    else:
        return 'fold'
