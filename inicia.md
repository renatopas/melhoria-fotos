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

Fazer o teste inicial com poucas imagens e sempre solicitar confirmação. Depois, permitir processamento gradual em lotes de tamanho escolhido pelo usuário.

Para testes do script, por exemplo, uma imagem é suficiente

Somente executar para todas as fotos mediante confirmação

### Com as melhorias

Garantir que as fotos sejam apenas melhoradas, com colorização e redução de ruído.

Segue sugestão de prompt:

```
Professionally restore and fully colorize this scanned school composite.

Substantially improve photographic quality: remove xerox and scanning noise, dust, stains and grain; correct fading, exposure and contrast; reduce minor blur; and recover natural facial and clothing detail where that detail is supported by visible evidence in the source. Produce clear, realistic portraits rather than merely tinting the scan. Use natural, historically plausible color throughout every portrait.

Preserve the source exactly as to identity and structure. Keep each face, expression, hairstyle, garment, printed marking, portrait boundary, text and page layout unchanged. Restoration may clarify existing features, but must not redesign shapes, invent missing detail or add content. Preserve readable text and existing clothing graphics. Keep genuinely uncertain areas soft.

Treat very faint ghost images or show-through outside the bordered portrait cells as paper/scanning artifacts; remove them rather than developing them into people or objects.

Return one restored image with the same composition.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
