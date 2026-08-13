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

Para trabalhar em etapas, informe qualquer quantidade positiva. Por exemplo:

```bash
python3 restaurar_fotos.py submit --limit 20 --confirm-paid
```

O limite seleciona somente fotos ainda ausentes no destino. O script pode solicitar que o lote seja reduzido caso as imagens ultrapassem juntas o limite técnico de 18 MiB após a codificação.

O comando informa o nome do job. Consulte e baixe o resultado posteriormente:

```bash
python3 restaurar_fotos.py collect batches/ID_DO_JOB
```

Se o ID for omitido, o registro pendente mais recente em `.batch_jobs/` será usado:

```bash
python3 restaurar_fotos.py collect
```

Os resultados são gravados em `fotos/melhorada/`, com os nomes originais. Cada arquivo final é uma composição com o original à esquerda e a versão restaurada à direita, identificada discretamente como `Imagem colorizada por IA`. A montagem e a legenda são produzidas localmente, sem uma chamada adicional à API.

Fotos cujo nome já exista no destino são removidas da seleção antes da aplicação de `--limit`; portanto, não são reenviadas nem contam no limite. Arquivos existentes nunca são sobrescritos.

O processamento completo exige `--all`, `--confirm-paid` e a confirmação adicional mostrada pela ajuda do programa. Não o execute sem autorização explícita.
