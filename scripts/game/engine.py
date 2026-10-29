"""Motor del tres en raya: reglas, IA (minimax) y lectura de los títulos de issue.

Sin entrada/salida: solo funciones puras sobre un tablero de 9 caracteres
("X", "O" o "-"), numerado de 0 a 8 por filas. Para las personas las casillas van
de 1 a 9 y se nombran como en una hoja de cálculo: columnas A–C y filas 1–3
(A1 arriba a la izquierda, C3 abajo a la derecha).

    A1 B1 C1        0 1 2
    A2 B2 C2   =    3 4 5
    A3 B3 C3        6 7 8
"""
from __future__ import annotations

import random
import re
from functools import lru_cache

X, O, EMPTY = "X", "O", "-"
EMPTY_BOARD = EMPTY * 9
CELLS = ("A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3")
LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8),      # filas
         (0, 3, 6), (1, 4, 7), (2, 5, 8),      # columnas
         (0, 4, 8), (2, 4, 6))                 # diagonales

# Probabilidad de que la CPU juegue al azar en vez de la mejor jugada: con minimax puro
# es imbatible, y un tres en raya al que no se puede ganar no tiene gracia.
RANDOM_RATE = 0.2

# Títulos válidos: "ttt|move|1" … "ttt|move|9" y "ttt|new". Nada más (ni espacios,
# ni mayúsculas, ni dígitos que no sean ASCII).
TITLE_RE = re.compile(r"^ttt\|(move\|[1-9]|new)$", re.ASCII)
MAX_TITLE = 16


def parse_title(title) -> tuple[str, int | None] | None:
    """'ttt|move|5' → ('move', 4) (índice 0–8) · 'ttt|new' → ('new', None) · cualquier otra cosa → None."""
    if not isinstance(title, str) or len(title) > MAX_TITLE:
        return None
    m = TITLE_RE.fullmatch(title)
    if not m:
        return None
    if m.group(1) == "new":
        return ("new", None)
    return ("move", int(m.group(1)[-1]) - 1)


# --------------------------------------------------------------------------- reglas
def other(player: str) -> str:
    return O if player == X else X


def is_valid_board(board) -> bool:
    """9 casillas con X/O/-, empieza X y nadie mueve dos veces seguidas."""
    if not isinstance(board, str) or len(board) != 9 or set(board) - {X, O, EMPTY}:
        return False
    return board.count(X) - board.count(O) in (0, 1)


def winner(board: str) -> tuple[str, tuple[int, int, int]] | None:
    """(jugador, línea) si alguien tiene tres en raya; si no, None."""
    for line in LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], line
    return None


def is_full(board: str) -> bool:
    return EMPTY not in board


def outcome(board: str) -> str | None:
    """'X' u 'O' si hay ganador, 'draw' si el tablero está lleno, None si se sigue jugando."""
    w = winner(board)
    if w:
        return w[0]
    return "draw" if is_full(board) else None


def to_move(board: str) -> str:
    """Siempre empiezan las X (los visitantes)."""
    return X if board.count(X) == board.count(O) else O


def legal_moves(board: str) -> list[int]:
    if outcome(board):
        return []
    return [i for i, c in enumerate(board) if c == EMPTY]


def play(board: str, cell: int, player: str) -> str:
    if not 0 <= cell < 9 or board[cell] != EMPTY:
        raise ValueError(f"la casilla {cell} no está libre")
    return board[:cell] + player + board[cell + 1:]


# ------------------------------------------------------------------------------- IA
@lru_cache(maxsize=None)
def _negamax(board: str, player: str) -> int:
    """Valor de la posición para `player`, que es quien mueve (negamax con memoria).

    Ganar vale 10 − casillas ocupadas (cuanto antes, mejor), perder lo mismo en
    negativo (cuanto más tarde, mejor) y el empate 0.
    """
    if winner(board):                        # acaba de ganar el rival
        return -(10 - (9 - board.count(EMPTY)))
    if is_full(board):
        return 0
    return max(-_negamax(play(board, i, player), other(player))
               for i, c in enumerate(board) if c == EMPTY)


def move_scores(board: str, player: str) -> dict[int, int]:
    """Valor de cada jugada legal para `player`."""
    return {i: -_negamax(play(board, i, player), other(player)) for i in legal_moves(board)}


def best_moves(board: str, player: str) -> list[int]:
    """Todas las jugadas óptimas (empatadas en valor) para `player`."""
    scores = move_scores(board, player)
    if not scores:
        return []
    top = max(scores.values())
    return [i for i, s in scores.items() if s == top]


def cpu_move(board: str, player: str = O, rng: random.Random | None = None,
             random_rate: float = RANDOM_RATE) -> int:
    """Jugada de la CPU: casi siempre óptima (desempata al azar), a veces al azar."""
    rng = rng or random.Random()
    moves = legal_moves(board)
    if not moves:
        raise ValueError("la partida ya ha terminado")
    if random_rate > 0 and rng.random() < random_rate:
        return rng.choice(moves)
    return rng.choice(best_moves(board, player))
