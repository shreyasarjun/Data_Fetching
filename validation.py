import os
import pandas as pd

FOLDER_PATH = "./csv_files"  # update this


def validate_strike_prices_by_option(csv_file):
    try:
        df = pd.read_csv(csv_file)

        required_cols = {"strike_price", "option_type"}
        if not required_cols.issubset(df.columns):
            print(f"❌ {os.path.basename(csv_file)} → Missing required columns")
            return

        for opt_type in ["CE", "PE"]:
            opt_df = df[df["option_type"] == opt_type]

            if opt_df.empty:
                print(f"⚠️ {os.path.basename(csv_file)} → No data for {opt_type}")
                continue

            strikes = sorted(opt_df["strike_price"].dropna().unique())

            if len(strikes) < 2:
                print(f"⚠️ {os.path.basename(csv_file)} → {opt_type}: Not enough strikes")
                continue

            invalid_gaps = []

            for i in range(1, len(strikes)):
                gap = strikes[i] - strikes[i - 1]
                if gap != 50:
                    invalid_gaps.append((strikes[i - 1], strikes[i], gap))

            if not invalid_gaps:
                print(f"✅ {os.path.basename(csv_file)} → {opt_type}: Strike prices valid")
            else:
                print(f"❌ {os.path.basename(csv_file)} → {opt_type}: Invalid strike gaps")
                for prev, curr, gap in invalid_gaps:
                    print(f"   {prev} → {curr} | gap = {gap}")

    except Exception as e:
        print(f"❌ {os.path.basename(csv_file)} → Error: {e}")


def process_all_files(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    print(f"📂 Total CSV files found: {len(csv_files)}\n")

    for idx, file in enumerate(csv_files, start=1):
        print(f"🔄 Processing ({idx}/{len(csv_files)}): {file}")
        validate_strike_prices_by_option(os.path.join(folder_path, file))
        print("-" * 60)


if __name__ == "__main__":
    process_all_files(FOLDER_PATH)
