import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Timestamped output directory
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = f"/home/p89n90/mtg-python-engine/results/stats_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Load merged result data
merged_csv_path = "/home/p89n90/mtg-python-engine/results/merged.csv"
df = pd.read_csv(merged_csv_path)
df = df.dropna(subset=["winner", "agent0", "agent1"])

# Add winning agent and deck
df["winner_agent"] = df.apply(lambda row: row["agent0"] if int(row["winner"]) == 0 else row["agent1"], axis=1)
df["winner_deck"] = df.apply(lambda row: row["deck0_name"] if int(row["winner"]) == 0 else row["deck1_name"], axis=1)

# === WIN RATES PER AGENT ===
agent_games = pd.concat([
    df[["agent0"]].rename(columns={"agent0": "agent"}),
    df[["agent1"]].rename(columns={"agent1": "agent"})
])
agent_games["games"] = 1
games_per_agent = agent_games.groupby("agent").sum()

wins_per_agent = df["winner_agent"].value_counts().rename("wins")
agent_stats = pd.concat([games_per_agent, wins_per_agent], axis=1).fillna(0)
agent_stats["win_rate"] = agent_stats["wins"] / agent_stats["games"]
agent_stats = agent_stats.sort_values("win_rate", ascending=False)

agent_stats.to_csv(f"{output_dir}/win_rates_per_agent.csv")

# === WIN RATES PER MATCHUP ===
def sorted_matchup(row):
    return tuple(sorted([row["agent0"], row["agent1"]]))

df["matchup"] = df.apply(sorted_matchup, axis=1)
df["winner_idx"] = df["winner"].astype(int)

matchup_stats = df.groupby("matchup").agg(
    games=("winner", "count"),
    wins_agent0=("winner_idx", lambda x: (x == 0).sum()),
    wins_agent1=("winner_idx", lambda x: (x == 1).sum())
)
matchup_stats["win_rate_agent0"] = matchup_stats["wins_agent0"] / matchup_stats["games"]
matchup_stats["win_rate_agent1"] = matchup_stats["wins_agent1"] / matchup_stats["games"]

matchup_stats.to_csv(f"{output_dir}/win_rates_per_matchup.csv")

# === WIN RATES PER DECK ===
deck_games = pd.concat([
    df[["deck0_name"]].rename(columns={"deck0_name": "deck"}),
    df[["deck1_name"]].rename(columns={"deck1_name": "deck"})
])
deck_games["games"] = 1
games_per_deck = deck_games.groupby("deck").sum()

wins_per_deck = df["winner_deck"].value_counts().rename("wins")
deck_stats = pd.concat([games_per_deck, wins_per_deck], axis=1).fillna(0)
deck_stats["win_rate"] = deck_stats["wins"] / deck_stats["games"]
deck_stats = deck_stats.sort_values("win_rate", ascending=False)

deck_stats.to_csv(f"{output_dir}/win_rates_per_deck.csv")

# === PLOTTING ===

# FIXED: Agent win rate plotting
agent_plot_df = agent_stats.reset_index().rename(columns={"index": "agent"})

plt.figure(figsize=(8, 4))
sns.barplot(data=agent_plot_df, x="agent", y="win_rate")
plt.title("Win Rate by Agent")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{output_dir}/win_rate_by_agent.png")
plt.close()

# Matchup heatmap
agent_list = sorted(set(df["agent0"]).union(set(df["agent1"])))
matchup_matrix = pd.DataFrame(index=agent_list, columns=agent_list, data=float("nan"))

for (a1, a2), row in matchup_stats.iterrows():
    matchup_matrix.loc[a1, a2] = row["win_rate_agent0"]
    matchup_matrix.loc[a2, a1] = row["win_rate_agent1"]

plt.figure(figsize=(8, 6))
sns.heatmap(matchup_matrix, annot=True, cmap="Blues", fmt=".2f", cbar=True)
plt.title("Win Rate Matrix (Agent vs Agent)")
plt.tight_layout()
plt.savefig(f"{output_dir}/win_rate_matrix.png")
plt.close()
