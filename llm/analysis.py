import pandas
import numpy as np
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
        response_format=AdTheme,
    )

    return completion.choices[0].message.parsed.name


if __name__ == "__main__":
    df = pandas.read_excel("stratified_sampling_31_07_2024_llm.xlsx")
    # df["llm_prompt"] = None
    # df["llm_classification"] = None
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
