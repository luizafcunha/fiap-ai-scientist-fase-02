"""
Regras de validação de qualidade de dados.

Cobre as quatro dimensões exigidas pelo desafio:
- duplicidade
- valores ausentes
- validade de chaves de relacionamento
- consistência entre tabelas
"""
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ResultadoValidacao:
    regra: str
    tabela: str
    passou: bool
    detalhes: dict = field(default_factory=dict)


def checar_duplicidade(df: pd.DataFrame, tabela: str, colunas_chave: list[str]) -> ResultadoValidacao:
    duplicados = df.duplicated(subset=colunas_chave, keep=False)
    qtd_duplicados = int(duplicados.sum())
    return ResultadoValidacao(
        regra="duplicidade",
        tabela=tabela,
        passou=qtd_duplicados == 0,
        detalhes={"linhas_duplicadas": qtd_duplicados, "chave": colunas_chave},
    )


def checar_valores_ausentes(df: pd.DataFrame, tabela: str, colunas_obrigatorias: list[str]) -> ResultadoValidacao:
    ausentes = {
        col: int(df[col].isna().sum())
        for col in colunas_obrigatorias
        if col in df.columns and df[col].isna().sum() > 0
    }
    faltando_colunas = [col for col in colunas_obrigatorias if col not in df.columns]
    return ResultadoValidacao(
        regra="valores_ausentes",
        tabela=tabela,
        passou=len(ausentes) == 0 and len(faltando_colunas) == 0,
        detalhes={"colunas_com_nulos": ausentes, "colunas_inexistentes": faltando_colunas},
    )


def checar_chave_relacionamento(
    df_filho: pd.DataFrame,
    tabela_filho: str,
    coluna_fk: str,
    df_pai: pd.DataFrame,
    coluna_pk: str,
) -> ResultadoValidacao:
    ids_pai = set(df_pai[coluna_pk].astype(str))
    ids_filho = set(df_filho[coluna_fk].astype(str))
    orfaos = ids_filho - ids_pai
    return ResultadoValidacao(
        regra="chave_relacionamento",
        tabela=tabela_filho,
        passou=len(orfaos) == 0,
        detalhes={"registros_orfaos": len(orfaos), "exemplos": list(orfaos)[:5]},
    )


def checar_consistencia_intervalo(
    df: pd.DataFrame, tabela: str, coluna: str, minimo: float, maximo: float
) -> ResultadoValidacao:
    fora_do_intervalo = df[(df[coluna] < minimo) | (df[coluna] > maximo)]
    return ResultadoValidacao(
        regra="consistencia_intervalo",
        tabela=tabela,
        passou=len(fora_do_intervalo) == 0,
        detalhes={
            "coluna": coluna,
            "intervalo_esperado": [minimo, maximo],
            "registros_fora": len(fora_do_intervalo),
        },
    )