# Restauração das fotos ETFSP

Ferramenta em Python para restaurar e colorizar carômetros antigos com os modelos de imagem Nano Banana, pela Gemini Batch API.

Este documento contém tudo o que o operador precisa para preparar, executar e acompanhar o processamento. Objetivos, critérios históricos, limites de custo e demais regras de negócio estão em [REQUIREMENTS.md](REQUIREMENTS.md).

## O que o programa faz

O fluxo possui três comandos:

1. `plan`: mostra gratuitamente quais fotos seriam selecionadas.
2. `submit`: envia um job assíncrono e pago ao Batch API.
3. `collect`: consulta o job e salva os resultados quando estiverem prontos.

Para cada resultado, o programa cria localmente uma única imagem comparativa:

- original à esquerda;
- versão restaurada e colorizada à direita;
- divisor vertical discreto;
- legenda `Imagem colorizada por IA` sob a versão restaurada.

A montagem local não gera custo adicional de API. O arquivo final mantém o nome do original.

## Estrutura de diretórios

| Caminho | Finalidade | Versionado no Git |
|---|---|---|
| `fotos/melhorar/` | Entrada padrão: fotografias originais | Não |
| `fotos/melhorada/` | Saída padrão: comparações finais | Não |
| `fotos/melhorada/rejeitadas/` | Sugestão para arquivar resultados ruins | Não |
| `.batch_jobs/` | Registros locais dos jobs enviados | Não |
| `.env` | Chave da API e modelo padrão local | Não |
| `.env.example` | Exemplo seguro de configuração | Sim |
| `restaurar_fotos.py` | Programa principal | Sim |

Os diretórios de entrada e saída podem ser substituídos na linha de comando.

## Requisitos

- Python 3.10 ou mais recente.
- Chave válida da Gemini API.
- Dependências listadas em `requirements.txt`.
- Acesso à internet durante `submit` e `collect`.

Formatos de entrada aceitos: `.jpg`, `.jpeg`, `.png` e `.webp`. Somente arquivos diretamente dentro do diretório de entrada são considerados; subdiretórios não são percorridos.

## Instalação inicial

Execute na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Nas execuções futuras, basta entrar no projeto e ativar o ambiente:

```bash
source .venv/bin/activate
```

Os exemplos abaixo usam `.venv/bin/python`, que funciona sem ativar o ambiente virtual.

## Configuração da API

Abra `.env` e preencha:

```dotenv
GEMINI_API_KEY=SUA_CHAVE_AQUI
GEMINI_IMAGE_MODEL=gemini-3.1-flash-lite-image
```

Nunca coloque a chave em `.env.example`, no código ou no Git. O `.env` já está ignorado.

### Escolha do modelo

| Modelo | Identificador | Uso sugerido |
|---|---|---|
| Nano Banana 2 Lite | `gemini-3.1-flash-lite-image` | Menor custo; resultados menos consistentes em folhas complexas |
| Nano Banana 2 | `gemini-3.1-flash-image` | Equilíbrio recomendado entre qualidade e custo |
| Nano Banana Pro | `gemini-3-pro-image` | Maior qualidade para casos difíceis; custo superior |

A escolha segue esta precedência:

1. `--model` informado na linha de comando;
2. `GEMINI_IMAGE_MODEL` definido no `.env`;
3. padrão interno `gemini-3.1-flash-lite-image`.

Para este acervo, prefira o Nano Banana 2 normal quando fidelidade e qualidade forem mais importantes que o menor custo.

## Sintaxe geral

```text
restaurar_fotos.py [parâmetros globais] {plan,submit,collect} [parâmetros do comando]
```

Os parâmetros globais devem aparecer **antes** de `plan`, `submit` ou `collect`.

### Parâmetros globais

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `-h`, `--help` | — | Exibe a ajuda geral |
| `--input-dir CAMINHO` | `fotos/melhorar/` | Diretório que contém as imagens originais |
| `--output-dir CAMINHO` | `fotos/melhorada/` | Diretório onde serão gravadas as comparações |
| `--model MODELO` | valor do `.env` | Substitui o modelo apenas naquela execução |

Exemplo com diretórios alternativos:

```bash
.venv/bin/python restaurar_fotos.py \
  --input-dir /dados/entrada \
  --output-dir /dados/saida \
  plan --limit 5
```

## Comando `plan`

Lista as imagens que seriam enviadas, o modelo, os diretórios e o tamanho aproximado. Não exige chave e não acessa a API.

```bash
.venv/bin/python restaurar_fotos.py plan
```

### Parâmetros de `plan`

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--limit N` | `1` | Seleciona os primeiros `N` arquivos pendentes; aceita qualquer inteiro positivo |
| `--all` | desativado | Seleciona todos os arquivos pendentes |

`--limit` e `--all` são mutuamente exclusivos.

Exemplos:

```bash
.venv/bin/python restaurar_fotos.py plan --limit 20
.venv/bin/python restaurar_fotos.py plan --all
```

## Comando `submit`

Cria um job pago no Gemini Batch API. O processamento é assíncrono e pode levar até 24 horas, embora normalmente termine antes.

### Parâmetros de `submit`

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--limit N` | `1` | Envia os primeiros `N` arquivos pendentes |
| `--all` | desativado | Envia todos os arquivos pendentes |
| `--confirm-paid` | desativado | Confirma conscientemente a criação do job pago; obrigatório |
| `--confirm-all FRASE` | — | Com `--all`, exige a frase exata `PROCESSAR_TODAS_AS_FOTOS` |

`--limit` aceita qualquer inteiro positivo. Ainda existe um limite técnico: as imagens codificadas em base64 devem totalizar no máximo 18 MiB por job. Se o limite for ultrapassado, reduza `N`.

Enviar uma imagem com o modelo configurado no `.env`:

```bash
.venv/bin/python restaurar_fotos.py submit --limit 1 --confirm-paid
```

Enviar vinte imagens explicitamente com Nano Banana 2:

```bash
.venv/bin/python restaurar_fotos.py \
  --model gemini-3.1-flash-image \
  submit --limit 20 --confirm-paid
```

Enviar todas as imagens pendentes:

```bash
.venv/bin/python restaurar_fotos.py submit \
  --all \
  --confirm-paid \
  --confirm-all PROCESSAR_TODAS_AS_FOTOS
```

Ao concluir a submissão, o programa mostra:

- o identificador no formato `batches/ID`;
- o caminho do registro em `.batch_jobs/`;
- o comando sugerido para coleta.

A criação de um job não é idempotente: executar `submit` duas vezes cria dois jobs e pode cobrar duas vezes.

## Comando `collect`

Consulta o estado de um job. Se ele tiver terminado com sucesso, baixa os resultados e cria as composições finais.

### Parâmetros de `collect`

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `job` | Não | ID `batches/ID` ou caminho de um registro JSON; se omitido, usa o registro pendente mais recente |
| `-h`, `--help` | Não | Exibe a ajuda do comando |

Coletar automaticamente o job pendente mais recente:

```bash
.venv/bin/python restaurar_fotos.py collect
```

Coletar um job específico:

```bash
.venv/bin/python restaurar_fotos.py collect batches/ID_DO_JOB
```

Também é possível informar o registro:

```bash
.venv/bin/python restaurar_fotos.py collect .batch_jobs/batches_ID_DO_JOB.json
```

Se o job ainda estiver em andamento, nada é salvo; execute `collect` novamente mais tarde. Jobs já coletados, cancelados, expirados ou com falha não são escolhidos automaticamente.

## Como as fotos são selecionadas

1. Os arquivos de entrada são ordenados pelo nome.
2. Arquivos com extensão não suportada são ignorados.
3. Se o mesmo nome já existir no diretório de saída, a foto é considerada concluída.
4. Fotos concluídas são removidas **antes** de aplicar `--limit`.
5. O programa nunca sobrescreve um resultado existente.

Exemplo: se `foto01.jpg` já existe na saída, `--limit 10` seleciona dez outros arquivos pendentes; `foto01.jpg` não conta no limite.

A comparação é feita pelo nome exato. Um arquivo chamado `foto01_v1.jpg` não marca `foto01.jpg` como concluído.

## Validação e gravação dos resultados

Antes de salvar, o programa verifica:

- se a resposta contém exatamente uma imagem;
- se o original ainda existe;
- se o destino ainda não existe;
- se a proporção da imagem gerada difere no máximo 10% da original.

A validação de proporção rejeita respostas em que o modelo criou painéis, comparações ou páginas adicionais. Ela não detecta automaticamente alterações semânticas, como pessoas inventadas, cabelo modificado ou texto reinterpretado; por isso a revisão visual continua obrigatória.

Se as dimensões forem diferentes, mas a proporção for aceitável, a restauração é redimensionada para coincidir com o original antes da montagem.

## Revisão, rejeição e reprocessamento

Revise visualmente cada comparação antes de publicá-la.

Para reprocessar uma foto, o arquivo com aquele nome não pode permanecer diretamente no diretório de saída. Preserve o resultado anterior movendo-o para uma subpasta, por exemplo:

```bash
mkdir -p fotos/melhorada/rejeitadas
mv fotos/melhorada/ARQUIVO.jpg fotos/melhorada/rejeitadas/ARQUIVO.jpg
```

Depois confira a seleção com `plan` e envie novamente. Não apague o original de `fotos/melhorar/`.

## Fluxo operacional recomendado

```bash
# 1. Confira modelo, arquivos e tamanho sem custo.
.venv/bin/python restaurar_fotos.py \
  --model gemini-3.1-flash-image \
  plan --limit 10

# 2. Envie exatamente o lote conferido.
.venv/bin/python restaurar_fotos.py \
  --model gemini-3.1-flash-image \
  submit --limit 10 --confirm-paid

# 3. Consulte e colete quando estiver pronto.
.venv/bin/python restaurar_fotos.py collect

# 4. Revise visualmente todos os resultados.
```

Use o mesmo `--model`, `--input-dir`, `--output-dir` e limite em `plan` e `submit` para que o planejamento represente a submissão real.

## Solução de problemas

### `Preencha GEMINI_API_KEY no arquivo .env`

Preencha a chave em `.env`. Confirme que o arquivo está na raiz do projeto.

### `Dependências ausentes`

Execute:

```bash
.venv/bin/pip install -r requirements.txt
```

### `Nenhuma imagem pendente`

Todos os nomes encontrados na entrada já existem na saída. Para refazer uma imagem, mova o resultado atual para `rejeitadas/`.

### `Lote maior que o limite seguro de 18 MiB`

Reduza o valor de `--limit`. O tamanho relevante é o total depois da codificação base64, maior que a soma dos arquivos originais.

### `Nenhum job pendente encontrado`

Todos os registros locais foram coletados ou terminaram sem sucesso. Informe explicitamente um ID ou registro se quiser consultar um job específico.

### `Ainda não terminou`

O job continua na fila ou em processamento. Aguarde e execute `collect` novamente.

### `Resultado rejeitado: a resposta alterou a proporção`

O modelo produziu uma página ou painel incompatível. O arquivo não foi salvo. Reenvie a foto; prefira `gemini-3.1-flash-image` ou `gemini-3-pro-image` em casos difíceis.

### O modelo inventou ou alterou pessoas, roupas ou texto

Arquive o resultado em `rejeitadas/` e refaça com um modelo superior. A comparação lado a lado torna a intervenção transparente, mas não substitui a revisão humana.

## Ajuda incorporada

```bash
.venv/bin/python restaurar_fotos.py --help
.venv/bin/python restaurar_fotos.py plan --help
.venv/bin/python restaurar_fotos.py submit --help
.venv/bin/python restaurar_fotos.py collect --help
```

Documentação oficial: [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation) e [Gemini Batch API](https://ai.google.dev/gemini-api/docs/batch-api).
