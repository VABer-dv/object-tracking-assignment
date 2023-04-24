import pandas as pd


def julia_accuracy(created_track):
    df = pd.DataFrame([{o["cb_id"]: o["track_id"] for o in i["data"]} for i in created_track])
    return df.apply(lambda x: len(set([i for i in x if pd.notna(i)])), axis=0).mean()
