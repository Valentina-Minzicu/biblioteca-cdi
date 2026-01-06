import pandas as pd

from app import create_app, db
from app.models import Book

EXCEL_PATH = "carti.xlsx"
SHEET_NAME = 0

def clean(s):
    # curățare minimă: string, strip, fără "nan"/"none"
    s = "" if s is None else str(s).strip()
    if s.lower() in ("nan", "none"):
        return ""
    return s

def main():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, header=None)

    # luăm doar primele 2 coloane (Autor, Titlu)
    df = df.iloc[:, :2]
    df.columns = ["author", "title"]

    df["author"] = df["author"].apply(clean)
    df["title"] = df["title"].apply(clean)

    # elimină rânduri goale
    df = df[(df["author"] != "") & (df["title"] != "")]

    # agregare: număr apariții = număr exemplare
    grouped = df.groupby(["author", "title"]).size().reset_index(name="copies")

    app = create_app()
    with app.app_context():
        inserted = 0
        for _, row in grouped.iterrows():
            author = row["author"]
            title = row["title"]
            copies = int(row["copies"])

            b = Book(
                author=author,
                title=title,
                total_copies=copies,
                available_copies=copies
            )
            db.session.add(b)
            inserted += 1

        db.session.commit()

    print(f"Import terminat. Titluri unice inserate: {inserted}")
    print(f"Total rânduri în Excel (după curățare): {len(df)}")
    print(f"Total exemplare (sumă apariții): {int(grouped['copies'].sum())}")

if __name__ == "__main__":
    main()
