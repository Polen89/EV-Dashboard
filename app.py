from flask import Flask, render_template, jsonify, request, Response
import sqlite3
import pandas as pd
from io import StringIO
import os

app = Flask(__name__)
DB = "electric_vehicles.db"
ALLOWED_VIEWS = {"model", "city", "year"}
ALLOWED_LIMITS = {5, 10, 25, 50}

if not os.path.exists(DB):
    import csv_loader

def query_db(sql: str, params=None):
    conn = sqlite3.connect(DB)
    try:
        df = pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()
    return df


def get_filters():
    make = request.args.get("make", "").strip()
    view = request.args.get("view", "model").strip().lower()

    try:
        row_limit = int(request.args.get("limit", 10))
    except (TypeError, ValueError):
        row_limit = 10

    if row_limit not in ALLOWED_LIMITS:
        row_limit = 10

    if view not in ALLOWED_VIEWS:
        view = "model"

    where = "WHERE Make = ?" if make else ""
    params = [make] if make else []
    return make, view, row_limit, where, params


def get_summary_data(make, where, params):
    total_df = query_db(f"SELECT COUNT(*) AS total FROM vehicles {where}", params=params)
    top_make_df = query_db(
        f"""
        SELECT Make, COUNT(*) AS total
        FROM vehicles {where}
        GROUP BY Make
        ORDER BY total DESC
        LIMIT 1
        """,
        params=params,
    )
    top_model_df = query_db(
        f"""
        SELECT Model, COUNT(*) AS total
        FROM vehicles {where}
        GROUP BY Model
        ORDER BY total DESC
        LIMIT 1
        """,
        params=params,
    )

    total = int(total_df.iloc[0]["total"]) if not total_df.empty else 0
    top_make_count = int(top_make_df.iloc[0]["total"]) if not top_make_df.empty else 0
    top_model_count = int(top_model_df.iloc[0]["total"]) if not top_model_df.empty else 0

    return {
        "total": total,
        "top_make": top_make_df.iloc[0]["Make"] if not top_make_df.empty else "-",
        "top_make_pct": round((top_make_count / total) * 100, 1) if total else 0,
        "top_model": top_model_df.iloc[0]["Model"] if not top_model_df.empty else "-",
        "top_model_pct": round((top_model_count / total) * 100, 1) if total else 0,
    }


def get_chart_data(view, where, params, row_limit):
    if view == "city":
        df = query_db(
            f"""
            SELECT City, COUNT(*) AS total
            FROM vehicles {where}
            GROUP BY City
            ORDER BY total DESC
            LIMIT {row_limit}
            """,
            params=params,
        )
        return {
            "labels": df["City"].fillna("Unknown").tolist(),
            "values": df["total"].tolist(),
            "makes": [""] * len(df),
        }

    if view == "year":
        df = query_db(
            f"""
            SELECT [Model Year] AS Year, COUNT(*) AS total
            FROM vehicles {where}
            GROUP BY [Model Year]
            ORDER BY [Model Year] ASC
            LIMIT {row_limit}
            """,
            params=params,
        )
        return {
            "labels": df["Year"].fillna(0).astype(int).astype(str).tolist(),
            "values": df["total"].tolist(),
            "makes": [""] * len(df),
        }

    df = query_db(
        f"""
        SELECT Make, Model, COUNT(*) AS total
        FROM vehicles {where}
        GROUP BY Make, Model
        ORDER BY total DESC
        LIMIT {row_limit}
        """,
        params=params,
    )
    return {
        "labels": (df["Model"].fillna("Unknown") + " (" + df["Make"].fillna("Unknown") + ")").tolist(),
        "values": df["total"].tolist(),
        "makes": df["Make"].fillna("").tolist(),
    }


def get_table_data(view, where, params, row_limit):
    if view == "city":
        df = query_db(
            f"""
            SELECT City, COUNT(*) AS total
            FROM vehicles {where}
            GROUP BY City
            ORDER BY total DESC
            LIMIT {row_limit}
            """,
            params=params,
        )
        return df.fillna("Unknown")

    if view == "year":
        df = query_db(
            f"""
            SELECT [Model Year] AS Year, COUNT(*) AS total
            FROM vehicles {where}
            GROUP BY [Model Year]
            ORDER BY [Model Year] ASC
            LIMIT {row_limit}
            """,
            params=params,
        )
        return df

    df = query_db(
        f"""
        SELECT Make, Model, COUNT(*) AS total
        FROM vehicles {where}
        GROUP BY Make, Model
        ORDER BY total DESC
        LIMIT {row_limit}
        """,
        params=params,
    )
    return df.fillna("Unknown")


@app.route("/")
def index():
    makes = query_db("SELECT DISTINCT Make FROM vehicles ORDER BY Make")
    return render_template("index.html", makes=makes["Make"].dropna().tolist())


@app.route("/api/summary")
def summary():
    make, _, _, where, params = get_filters()
    data = get_summary_data(make, where, params)
    return jsonify(data)


@app.route("/api/chart")
def chart():
    _, view, row_limit, where, params = get_filters()
    data = get_chart_data(view, where, params, row_limit)
    return jsonify(data)


@app.route("/api/table")
def table():
    _, view, row_limit, where, params = get_filters()
    df = get_table_data(view, where, params, row_limit)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/export")
def export_csv():
    _, view, row_limit, where, params = get_filters()
    df = get_table_data(view, where, params, row_limit)
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    csv_data = buffer.getvalue()
    filename = f"ev_dashboard_{view}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


if __name__ == "__main__":
    app.run(debug=True)