from random import getrandbits, random, shuffle, randrange
from math import exp, sqrt, pow
from typing import List, Tuple
from consts import *
import argparse

clamp = lambda x, l, u: l if x < l else u if x > u else x
kbd_print = lambda kbd: print('\t\t', *kbd[:13], "\n\t\t ", *kbd[13:25], "\n\t\t  ", *kbd[25:36], "\n\t\t   ", *kbd[36:], sep=" ")

parser = argparse.ArgumentParser(description="Simulated Annealing based keyboard layout generator")
parser.add_argument("-c", "--clamp", dest="clamp", default=200, type=int, help="number of swaps n; n=clamp(T/clamp_scale, 1, 26)")
parser.add_argument("-m", "--max-iter", dest="max_iter", default=250000, type=int, help="maximum number of iterations")
parser.add_argument("-d", "--decay", dest="decay", default=0.99, type=float, help="T*=decay")
parser.add_argument("-e", "--epoch", dest="epoch", default=20, type=int, help="number of iters before T decays")
parser.add_argument("-f", "--file", dest="file", default='main.py', type=str, help="file to use as example input")
args = parser.parse_args()

CLAMP_SCALE = args.clamp
FILE = args.file

with open(FILE, 'r') as f:
    blob = f.read()

def shuffle_genome(genome_seq:List[str], T:float):
    new_seq = genome_seq[:]
    n = clamp(int(T//CLAMP_SCALE), 1, 26)
    c = lambda : randrange(0, len(new_seq))
    for _ in range(n):
        i, j = c(), c()
        new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
    return new_seq 

def objective_function(layout:List[Tuple[float, float, int, int, int]], genome_seq:List[str])->float:
    finger_block = [ [0.0]*6 for _ in range(8) ]
    for i in range(0, 46):
        x, y, _, finger, home = layout[i]
        if home == 1:
            finger_block[finger-1][0:4] = [x, y, x, y]
    hand_prev, finger_prev = 0, 0
    key_from_char = lambda c: layout[genome_seq.index(letter_seq[key_map_dict[c][0]-1])]
    for c in blob:
        if c in key_map_dict:
            k = key_from_char(c)
            finger_prev, hand_prev = run_key(k, finger_block, finger_prev, hand_prev)
    return sum([finger_row[5] for finger_row in finger_block])

def objective_normalised(layout:List[Tuple[float, float, int, int, int]], genome_seq:List[str], qwerty_baseline:float)->float:
    return (objective_function(layout, genome_seq)/qwerty_baseline - 1)*100

def run_key(k: Tuple[float, float, int, int, int], finger_block:List[List[float]], finger_prev:int, hand_prev:int):
    x, y, row, finger, _ = k
    hand = hand_list[finger-1]
    
    for finger_idx in range(0, 8):
        home_x, home_y, current_x, current_y, dist_counter, objective_counter = finger_block[finger_idx]
        if (finger_idx+1) == finger:
            dist = sqrt(pow((x - current_x), 2) + pow((y - current_y), 2))

            dist_penalty = pow(dist, dist_effort)
            new_dist = dist_counter + dist

            double_finger_penalty = double_fingle_effort if finger != finger_prev and finger_prev != 0 and dist != 0 else 0
            doubleHandPenalty = double_hand_effort if hand != hand_prev and hand_prev != 0 else 0

            fingerPenalty = finger_effort[finger_idx]
            row = row_effort[row-1]

            penalties = (dist_penalty, double_finger_penalty, doubleHandPenalty, fingerPenalty, row)
            penalty = sum(penalties[i]*effortWeighting[i] for i in range(len(effortWeighting)))
            new_objective = objective_counter + penalty

            finger_block[finger_idx][2] = x
            finger_block[finger_idx][3] = y
            finger_block[finger_idx][4] = new_dist
            finger_block[finger_idx][5] = new_objective
        else:
            finger_block[finger_idx][2] = home_x
            finger_block[finger_idx][3] = home_y

    return finger, hand

def simulated_annealing(layout:List[Tuple[float, float, int, int, int]], seed_seq:List[str], epoch:int, max_iter:int, T:float, decay:float) -> List[str]:
    iteration = 0
    genome_prev = seed_seq
    shuffle(genome_prev)
    baseline_objective = objective_function(layout, qwerty_seq)
    objective_prev = objective_normalised(layout, genome_prev, baseline_objective)

    genome_best = genome_prev
    objective_best = objective_prev

    while iteration <= max_iter and T>1.0:
        iteration+=1

        genome_new = shuffle_genome(genome_prev, T)
        objective_new = objective_normalised(layout, genome_new, baseline_objective)
        delta = objective_new - objective_prev

        if delta < 0:
            genome_prev = genome_new
            objective_prev = objective_new
            if objective_new < objective_best:
                genome_best = genome_new
                objective_best = objective_new
        elif exp(-delta/T) > random():
            genome_prev = genome_new
            objective_prev = objective_new

        if iteration%epoch == 0:
            T*=decay
            if getrandbits(1):
                genome_prev = genome_best
                objective_prev = objective_best

    return genome_best

annealed = (simulated_annealing(
    trad_layout_map,
    letter_seq,
    args.epoch,
    args.max_iter,
    26*CLAMP_SCALE,
    args.decay))
kbd_print(annealed)
print('\n', objective_function(trad_layout_map, annealed))
