import os

import pandas
import numpy as np
import psycopg2 as pg
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm


client = OpenAI()


class AdTheme(BaseModel):
    name: str


def classify(prompt):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format=AdTheme,
    )

    return completion.choices[0].message.parsed.name


if __name__ == "__main__":
    engine = pg.connect(os.environ.get("DATABASE_URL"))
    df = pandas.read_sql("SELECT * FROM advertisement_mv WHERE internal_url=false", con=engine)
    prompt = """
    Classifique o anúncio abaixo em um seguintes temas: Automotivo, Casa e Jardim, Culinária e
    Gastronomia, Educação, Moda, Família e Relacionamentos, Finanças e Negócios, Saúde e Estética,
    Tecnologia, Viagem e Turismo, Esportes, Política, Meio Ambiente, Cultura e Arte, Outros.
    Responda apenas com o tema

    {context}
    """

    for index, row in enumerate(tqdm(df.itertuples())):
        if row.llm_classification is not np.nan:
            continue
        full_prompt = prompt.format(context=row.title)
        result = classify(full_prompt)
        df.loc[index, "llm_prompt"] = full_prompt
        df.loc[index, "llm_classification"] = result
