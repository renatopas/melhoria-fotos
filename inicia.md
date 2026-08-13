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
Create a high-quality, fully colorized restoration of this severely degraded scanned school composite. Prioritize visual clarity and photographic quality.

Perform an intensive restoration, not simple tinting. Strongly remove xerox noise, grain, dust, stains, fading, blur and scanning artifacts. Correct exposure, contrast and tonal range. Reconstruct plausible natural detail in faces, skin, eyes, hair and clothing wherever degradation has destroyed fine detail. Produce sharp, clean, realistic portraits with natural skin tones, convincing texture and historically plausible colors. Aim for the quality of well-preserved original portrait photographs rather than the appearance of a cleaned photocopy.

Keep each person recognizably the same: retain their basic facial geometry, expression, pose, hairstyle type and clothing type. Do not beautify, modernize or deliberately change identity. Reasonable AI reconstruction of lost fine detail is allowed, but it must remain consistent with the visible evidence.

Treat every text region as part of the original photograph, not as text to transcribe. Do not perform OCR, rewrite, correct, autocomplete or invent letters. Preserve clearly readable text; leave uncertain text visually uncertain.

Before editing, identify and count only the clearly visible original portrait photographs. Restore only those photographs. The output must contain exactly that same number of portraits, in exactly the same cells and positions. Copy the occupancy pattern of the source exactly: every cell that is empty in the source must remain blank paper. Faint show-through, paper shadows, reversed images and barely visible faces are printing artifacts, not people to restore. Do not create, remove, duplicate, move or replace any portrait, row, cell, person or label.

Return only one polished restored page. Do not create a comparison, split view, before-and-after layout, duplicate page or additional panel. The output must have the same single-page composition as the input.

```

### Outros cuidados

Sempre pergunte em caso de dúvida
