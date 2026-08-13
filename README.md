# Restauração das fotos ETFSP

Script para restaurar e colorizar fotografias antigas com o Nano Banana pelo Gemini Batch API.

## Preparação

1. Crie um ambiente virtual: `python3 -m venv .venv`
2. Ative-o: `source .venv/bin/activate`
3. Instale as dependências: `pip install -r requirements.txt`
4. Abra `.env` e preencha `GEMINI_API_KEY`.

O arquivo `.env` e todas as fotografias estão excluídos do Git.

## Uso seguro

Confira uma imagem sem custo:

```bash
python3 restaurar_fotos.py plan
```

Depois de obter autorização para o teste pago, envie uma imagem:

```bash
python3 restaurar_fotos.py submit --limit 1 --confirm-paid
```

O comando informa o nome do job. Consulte e baixe o resultado posteriormente:

```bash
python3 restaurar_fotos.py collect batches/ID_DO_JOB
```

Os resultados são gravados em `fotos/melhorada/`, com os nomes originais. Arquivos existentes nunca são sobrescritos.

O processamento completo exige `--all`, `--confirm-paid` e a confirmação adicional mostrada pela ajuda do programa. Não o execute sem autorização explícita.
