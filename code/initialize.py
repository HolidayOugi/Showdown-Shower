from battles import load_battle
from pokemon import load_pokemon
from players import load_players
from tiers import load_matches
from precalculate import precalculate

load_battle("../input/parquet", "../output/tiers")
load_pokemon("../input/parquet", "../output")
load_players("../output/tiers", "../output/players")
load_matches("../output/tiers", "../output/matches")
precalculate("../output", "../graphs")