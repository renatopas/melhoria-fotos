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
Perform a conservative restoration and colorization of this exact scanned school composite. This is a restoration task, not a recreation. The input image is the sole source of truth.

Allowed changes only:
- reduce dust, scratches, stains, fading, uneven exposure, excessive grain, xerographic noise, and scanning artifacts;
- make modest global improvements to contrast and sharpness;
- add subtle, historically plausible color to regions that already exist.

Identity preservation is the highest priority. Keep every person's face, facial geometry, expression, gaze, skin texture, hair, ears, neck, clothing, pose, and body proportions exactly as shown. Do not beautify, retouch, symmetrize, redraw, replace, or reinterpret any person. Do not reconstruct details that are absent or uncertain. If a feature is blurry, damaged, overexposed, hidden, or ambiguous, leave it blurry or ambiguous rather than guessing.

Absolutely do not add face masks, surgical masks, respirators, bandages, glasses, facial hair, jewelry, hats, accessories, logos, or any other object unless that same object is clearly and unambiguously present in the input. Xerox marks, shadows, stains, pale areas, and lines across a face are damage or uncertainty; they must never be interpreted as masks or objects.

Preserve the complete sheet layout, crop, borders, portrait positions, printed numbers, labels, handwriting, and typography. Do not rewrite, correct, replace, or invent illegible text. Do not remove legitimate objects. Do not modernize clothing, hairstyles, photographic style, or historical context. Colorization must not alter shapes, edges, or content.

Before returning the image, verify person by person that no object was added and that each identity still matches the input. Return exactly one restored image with the same composition, without captions, new borders, or explanatory text.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
