import argparse
import sqlite3
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="EV Report", style="cyan", header_style="bold magenta")

parser = argparse.ArgumentParser(description="SQL Report Generator")
parser.add_argument("--database", required=True, help="Path to SQLite database")
parser.add_argument("--limit", type=int, default=10, help="Number of rows to return")
parser.add_argument("--make", help="Filter by vehicle make (e.g. TESLA)")
parser.add_argument("--query", help="Custom SQL query to run")
parser.add_argument("--output", help="Save results to a CSV file")
parser.add_argument("--chart", help="Save a bar char as a PNG file")

args = parser.parse_args()
conn = sqlite3.connect(args.database)

if args.query:
    query = args.query
else:
    where_clause = f"WHERE Make = '{args.make.upper()}'" if args.make else ""

    query = f"""
        SELECT Make, Model, COUNT(*) as total
        FROM vehicles
        {where_clause}
         GROUP BY Make, Model 
         ORDER BY total DESC 
         LIMIT {args.limit}
    """

result = pd.read_sql(query, conn)

if args.output:
    result.to_csv(args.output, index=False)
    console.print(f"\n[bold green]✓ Saved to {args.output}[/bold green]")

if args.chart:
    if "total" not in result.columns:
        console.print("[bold red]⚠ Chart requires a query with a 'total' column[/bold red]")
    else:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker

        fig, ax = plt.subplots(figsize=(10,6))
        label_col = result.columns[0]

        if "Make" in result.columns:
            make_colors = {
                "TESLA": "#e31937",
                "NISSAN": "#c3002f",
                "CHEVROLET": "#ffd700",
                "FORD": "#003476",
                "VOLKSWAGEN": "#001e50",
                "HYUNDAI": "#002c5f",
                "KIA": "#bb162b",
                "BMW": "#0066b1",
                "AUDI": "#bb0a14",
            }
            default_color = "#4f98a3"
            colors = [make_colors.get(make, default_color) for make in result["Make"]]
        else:
            palette = [
                "#4f98a3",
                "#e31937",
                "#003476",
                "#ffd700",
                "#437a22",
                "#7a39bb",
                "#da7101",
                "#006494",
                "#a12c7b",
                "#bb162b",
            ]
            colors = [palette[i % len(palette)] for i in range(len(result))]

        labels = result["Model"] + " (" + result["Make"] + ")" if "Make" in result.columns \
        else result[label_col].astype(str)
        ax.barh(labels, result["total"], color=colors)
        ax.invert_yaxis()
        ax.set_xlabel("Total Vehicles")
        ax.set_title("EV Report")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        plt.savefig(args.chart, dpi=150)
        console.print(f"\n[bold green]✓ Chart saved to {args.chart}[/bold green]")

for col in result.columns:
    justify = "right" if col == "total" else "left"
    table.add_column(col, justify=justify)

for _, row in result.iterrows():
    table.add_row(*[str(v) for v in row])

console.print(table)

if "total" in result.columns:
    total_sum = result["total"].sum()
    label = f"Total {args.make.upper()} vehicles shown" if args.make else "Total vehicles shown"
    console.print(f"\n[bold]{label}:[/bold] [cyan]{total_sum:,}[/cyan]")

conn.close()