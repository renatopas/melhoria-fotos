Projeto de melhoria de foto tipo "carômetro" do site etfsp

## Objetivo

Melhorar a qualidade de fotos antigas que na verdade são imagens digitalizadas de diversas cópias xerográficas de pequenas fotos de todos os alunos de cada sala de aula. Ou seja, são fotos de fotos

## Onde estão a fotos a serem melhoradas

No diretório fotos/melhorar

## Ferramentas que serão utilizadas

Modelo Nano Banana (ou sub tipo adequado) que será utilizado via fornecimento de api key

## Como deve ser feito

Pode ser criado script em Python

As fotos melhoradas devem ser criada em um subditerório tipo "melhorada". Os arquivos melhorados devem preservar os nomes originais.

## Cuidados

Cuidados que devem ser tomados / requisitos diversos

### Custo

O modelo deve ser utilizado com parcimônia pois tem custo.

Utilize o modo "batch", que é duas vezes mais barato.

Fazer testes com poucas imagens. No máximo 5 e sempre solicitando confirmação.

Para testes do script, por exemplo, uma imagem é suficiente

Somente executar para todas as fotos mediante confirmação

### Com as melhorias

Garantir que as fotos sejam apenas melhoradas, com colorização e redução de ruído.

Segue sugestão de prompt:

```
Restore this old black-and-white photograph while preserving
the original photographic content as faithfully as possible.

Correct:
- scratches
- dust
- stains
- fading
- uneven exposure
- contrast problems
- minor blur
- film grain and scanning artifacts

Improve facial clarity and fine details conservatively.

Do NOT:
- change facial features
- change expressions
- change hairstyle
- change clothing
- add objects
- remove legitimate objects
- invent missing facial details
- change body proportions
- modernize the scene

Apply realistic, historically plausible colorization conservatively.

The result should look like a professionally restored version
of the original photograph, not like an AI-generated recreation.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
