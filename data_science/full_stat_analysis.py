from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def load_merged_csv():
    merged_file = Path("/home/p89n90/mtg-python-engine/results/merged.csv")
    if not merged_file.exists():
        raise FileNotFoundError(f"Merged CSV not found: {merged_file}")
    return pd.read_csv(merged_file)


def prepare_long_player_stats(df):
    p0 = df[[c for c in df.columns if c.startswith('p0_')]].copy()
    p1 = df[[c for c in df.columns if c.startswith('p1_')]].copy()
    p0.columns = [c.replace('p0_', '') for c in p0.columns]
    p1.columns = [c.replace('p1_', '') for c in p1.columns]
    p0['agent'] = df['agent0']
    p1['agent'] = df['agent1']
    long = pd.concat([p0.assign(player_idx=0), p1.assign(player_idx=1)], ignore_index=True)
    long = long.reset_index(drop=True)
    long['game_idx'] = long.index // 2
    long['won'] = long.apply(lambda r: 1 if int(df.loc[r['game_idx'], 'winner']) == r['player_idx'] else 0, axis=1)
    long['util_per_land'] = long['approx_mana_spent'] / (long.get('land_plays', 0) + 1)
    return long


def plot_win_rates(df, out_dir, tag):
    wins, games = {}, {}
    for _, row in df.iterrows():
        a0 = row['agent0']
        a1 = row['agent1']
        games[a0] = games.get(a0, 0) + 1
        games[a1] = games.get(a1, 0) + 1
        winner_idx = int(row['winner'])
        winner_agent = row['agent0'] if winner_idx == 0 else row['agent1']
        wins[winner_agent] = wins.get(winner_agent, 0) + 1
    stats = pd.DataFrame([{'agent': k, 'games': games[k], 'wins': wins.get(k, 0)} for k in games])
    stats['win_rate'] = stats['wins'] / stats['games']

    plt.figure(figsize=(8, 4))
    sns.barplot(data=stats.sort_values('win_rate', ascending=False), x='agent', y='win_rate')
    plt.xticks(rotation=45, ha='right')
    plt.title('Win rate by agent class')
    plt.tight_layout()
    out = Path(out_dir) / f'win_rate_by_agent_{tag}.png'
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")


def plot_resource_utilization(long_df, out_dir, tag):
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=long_df, x='agent', y='approx_mana_spent')
    plt.xticks(rotation=45, ha='right')
    plt.title('Distribution of approx_mana_spent by agent')
    plt.tight_layout()
    out1 = Path(out_dir) / f'mana_spent_by_agent_{tag}.png'
    plt.savefig(out1)
    plt.close()
    print(f"Saved: {out1}")

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=long_df, x='agent', y='util_per_land')
    plt.xticks(rotation=45, ha='right')
    plt.title('Approx mana spent per land (proxy) by agent')
    plt.tight_layout()
    out2 = Path(out_dir) / f'util_per_land_by_agent_{tag}.png'
    plt.savefig(out2)
    plt.close()
    print(f"Saved: {out2}")


def plot_mana_waste_proxies(long_df, out_dir, tag):
    if 'main_phase_passes' in long_df.columns:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=long_df, x='main_phase_passes', y='approx_mana_spent', hue='agent', alpha=0.7)
        plt.title('Main phase passes vs approx mana spent')
        plt.tight_layout()
        out = Path(out_dir) / f'passes_vs_mana_spent_{tag}.png'
        plt.savefig(out)
        plt.close()
        print(f"Saved: {out}")

    if 'land_plays' in long_df.columns and 'main_phase_passes' in long_df.columns:
        agg = long_df.groupby('agent').agg({'land_plays': 'mean', 'main_phase_passes': 'mean'}).reset_index()
        plt.figure(figsize=(8, 5))
        sns.barplot(data=agg.melt(id_vars='agent'), x='agent', y='value', hue='variable')
        plt.title('Avg land plays and main phase passes per agent')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        out2 = Path(out_dir) / f'landplays_passes_by_agent_{tag}.png'
        plt.savefig(out2)
        plt.close()
        print(f"Saved: {out2}")


def main():
    results_dir = Path("/home/p89n90/mtg-python-engine/results")
    out_dir = results_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    tag = datetime.now().strftime("%Y%m%d_%H%M%S")

    df = load_merged_csv()
    print(f"Loaded {len(df)} games from: {results_dir}/merged.csv")

    plot_win_rates(df, out_dir, tag)
    long = prepare_long_player_stats(df)
    plot_resource_utilization(long, out_dir, tag)
    plot_mana_waste_proxies(long, out_dir, tag)


if __name__ == '__main__':
    main()
