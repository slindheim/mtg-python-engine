"""Basic full-stat analysis and first visualizations for match results CSVs.

Usage:
    pip install pandas matplotlib seaborn
    python data_science/full_stat_analysis.py --results results --out results/figures

This script loads CSV files like the attached `*_random_vs_heuristic.csv`,
computes simple summary statistics and saves three starter plots:
  - Win rate by agent class
  - Resource utilization (approx_mana_spent and a simple proxy per land play)
  - Mana-waste proxies (main phase passes vs land plays)

Heuristic mappings (quick simple lines):
- Resource utilization: use `p0_approx_mana_spent` / `p1_approx_mana_spent` and
  proxy `approx_mana_spent / (land_plays + 1)` to estimate "uses available mana".
- Suboptimal/mana-waste decisions: use `p?_main_phase_passes`, `p?_land_plays`,
  and `p?_approx_mana_spent` — high `main_phase_passes` with low `approx_mana_spent`
  suggests wasted opportunities or poor targeting.
- Performance of heuristic vs heuristic: use `winner`, `agent0`, `agent1`, and
  aggregated win rates per agent class to measure policy quality.

The columns expected in the CSVs (examples seen in provided file):
`game_id,agent0,agent1,deck0_name,deck1_name,winner,...,p0_land_plays,p0_creature_casts,p0_approx_mana_spent,p0_main_phase_actions,p0_main_phase_passes,...`
"""

from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_results(results_dir):
    p = Path(results_dir)
    files = sorted(p.glob("*_random_vs_*.csv"))
    if not files:
        files = sorted(p.glob("*.csv"))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Failed to read {f}: {e}")
    if not dfs:
        raise FileNotFoundError(f"No CSVs found in {results_dir}")
    return pd.concat(dfs, ignore_index=True)


def prepare_long_player_stats(df):
    # Create long-format dataframe with one row per player per game
    p0 = df[[c for c in df.columns if c.startswith('p0_')]].copy()
    p1 = df[[c for c in df.columns if c.startswith('p1_')]].copy()
    p0.columns = [c.replace('p0_', '') for c in p0.columns]
    p1.columns = [c.replace('p1_', '') for c in p1.columns]
    p0['agent'] = df['agent0']
    p1['agent'] = df['agent1']
    long = pd.concat([p0.assign(player_idx=0), p1.assign(player_idx=1)], ignore_index=True)
    # Map each long row back to game index: stacked p0,p1 -> game_idx = index // 2
    long = long.reset_index(drop=True)
    long['game_idx'] = (long.index // 2)
    long['won'] = long.apply(lambda r: 1 if int(df.loc[r['game_idx'], 'winner']) == r['player_idx'] else 0, axis=1)
    # simple utilization proxy
    long['util_per_land'] = long['approx_mana_spent'] / (long.get('land_plays', 0) + 1)
    return long


def plot_win_rates(df, out_dir):
    wins = {}
    games = {}
    for _, row in df.iterrows():
        a0 = row['agent0']
        a1 = row['agent1']
        games[a0] = games.get(a0, 0) + 1
        games[a1] = games.get(a1, 0) + 1
        winner_idx = int(row['winner'])
        winner_agent = row['agent0'] if winner_idx == 0 else row['agent1']
        wins[winner_agent] = wins.get(winner_agent, 0) + 1
    stats = pd.DataFrame([{'agent': k, 'games': games.get(k, 0), 'wins': wins.get(k, 0)} for k in games.keys()])
    stats['win_rate'] = stats['wins'] / stats['games']

    plt.figure(figsize=(8,4))
    sns.barplot(data=stats.sort_values('win_rate', ascending=False), x='agent', y='win_rate')
    plt.xticks(rotation=45, ha='right')
    plt.title('Win rate by agent class')
    plt.tight_layout()
    out = Path(out_dir)/'win_rate_by_agent.png'
    plt.savefig(out)
    plt.close()
    print(f"Saved {out}")


def plot_resource_utilization(long_df, out_dir):
    plt.figure(figsize=(8,5))
    sns.boxplot(data=long_df, x='agent', y='approx_mana_spent')
    plt.xticks(rotation=45, ha='right')
    plt.title('Distribution of approx_mana_spent by agent')
    plt.tight_layout()
    out1 = Path(out_dir)/'mana_spent_by_agent.png'
    plt.savefig(out1)
    plt.close()
    print(f"Saved {out1}")

    plt.figure(figsize=(8,5))
    sns.boxplot(data=long_df, x='agent', y='util_per_land')
    plt.xticks(rotation=45, ha='right')
    plt.title('Approx mana spent per land (proxy) by agent')
    plt.tight_layout()
    out2 = Path(out_dir)/'util_per_land_by_agent.png'
    plt.savefig(out2)
    plt.close()
    print(f"Saved {out2}")


def plot_mana_waste_proxies(long_df, out_dir):
    # main_phase_passes vs approx_mana_spent scatter per agent
    if 'main_phase_passes' in long_df.columns:
        plt.figure(figsize=(8,6))
        sns.scatterplot(data=long_df, x='main_phase_passes', y='approx_mana_spent', hue='agent', alpha=0.7)
        plt.title('Main phase passes vs approx mana spent (higher passes + low mana suggests waste)')
        plt.tight_layout()
        out = Path(out_dir)/'passes_vs_mana_spent.png'
        plt.savefig(out)
        plt.close()
        print(f"Saved {out}")

    # land plays vs main phase passes aggregated
    agg = long_df.groupby('agent').agg({'land_plays':'mean','main_phase_passes':'mean'}).reset_index()
    plt.figure(figsize=(8,5))
    sns.barplot(data=agg.melt(id_vars='agent'), x='agent', y='value', hue='variable')
    plt.title('Avg land plays and main phase passes per agent (proxies for mana availability & passiveness)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    out2 = Path(out_dir)/'landplays_passes_by_agent.png'
    plt.savefig(out2)
    plt.close()
    print(f"Saved {out2}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results', help='Directory with CSV result files')
    parser.add_argument('--out', default='results/figures', help='Directory to save figures')
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_results(args.results)
    print(f"Loaded {len(df)} games from {args.results}")

    # Simple win-rate plot
    plot_win_rates(df, out_dir)

    # Prepare per-player long stats and plots
    long = prepare_long_player_stats(df)
    plot_resource_utilization(long, out_dir)
    plot_mana_waste_proxies(long, out_dir)

    print('Finished basic analysis. Next: add more targeted metrics and interactive plots.')


if __name__ == '__main__':
    main()
