import os

import pandas
import numpy as np
import psycopg2 as pg
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm

from llm import prompt


client = OpenAI()


class AdTheme(BaseModel):
    name: str


def classify_ad(title, tag):
    tag = tag or ""
    full_prompt = prompt.content.format(title=title, tag=tag)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.0,
        response_format=AdTheme,
    )

    return completion.choices[0].message.parsed.name


if __name__ == "__main__":
    engine = pg.connect(os.environ.get("DATABASE_URL"))
    df = pandas.read_sql("SELECT * FROM advertisement_mv WHERE internal_url=false", con=engine)

    for index, row in enumerate(tqdm(df.itertuples())):
        if row.llm_classification is not np.nan:
            continue
        result = classify_ad(row.title)
        df.loc[index, "llm_classification"] = result
