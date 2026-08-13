#!/usr/bin/env python3
"""Restaura e coloriza fotografias usando o Gemini Batch API."""

from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "fotos" / "melhorar"
DEFAULT_OUTPUT = ROOT / "fotos" / "melhorada"
JOBS_DIR = ROOT / ".batch_jobs"
DEFAULT_MODEL = "gemini-3.1-flash-lite-image"
MAX_INLINE_BYTES = 18 * 1024 * 1024  # margem abaixo do limite oficial de 20 MB
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

PROMPT = """Restore and fully colorize this entire scanned 1994 school composite.

Two requirements are equally important:

1. COMPLETE COLORIZATION
Colorize every portrait on the page, including every person's skin, lips, eyes, hair, and clothing, as well as each portrait background. No person or portrait may remain black-and-white, grayscale, monochrome, or sepia. Use natural skin tones and restrained, realistic, historically plausible colors. When the original color is unknown, choose a plausible color consistently; color uncertainty is not a reason to leave an area uncolored. Keep the paper, printed grid, and text neutral unless a faint natural paper tone is appropriate.

2. CONTENT AND IDENTITY PRESERVATION
Use the input as the sole source for shapes and content. Preserve each person's identity, facial geometry, expression, gaze, hairstyle, clothing shape, pose, and proportions. For every hairstyle, preserve the exact outer silhouette, hairline, parting, length, volume, smoothness, and direction in which the hair is combed. Color the existing hair without restyling it. Do not add individual strands, spikes, extra volume, curls, bangs, or a punk/spiky appearance that is not clearly visible in the input. Xerox grain and edge noise around the head are not hair. Preserve the sheet layout, crop, portrait positions, borders, numbers, labels, handwriting, and typography. Do not beautify or redesign faces. If a facial detail is unclear, keep its shape soft rather than inventing a sharper feature.

Remove or reduce scratches, dust, stains, fading, uneven exposure, xerographic noise, excessive grain, and scanning artifacts. Improve contrast and clarity moderately.

Do not add or reinterpret any object, accessory, garment detail, or modern element. Reproduce the area from each person's nose through mouth and chin using only the facial anatomy and tones supported by the source. Keep the nose, mouth, chin, cheeks, and jaw visually unobstructed wherever they are visible in the input. Pale patches, white circles, shadows, stains, lines, and missing xerographic information across a face are flat print or paper damage, never a three-dimensional or wearable item. Reduce such damage conservatively; where facial information is missing, use a soft continuation of nearby facial tone without adding seams, folds, straps, hard edges, or a recognizable object. Do not rewrite illegible text or modernize the scene.

Return exactly one restored image with the same composition. Before returning it, verify that every portrait is colorized, that visible noses, mouths, and chins remain unobstructed, and that no new object appears on any person."""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    result.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--model", default=None, help="Sobrescreve GEMINI_IMAGE_MODEL")
    sub = result.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Lista o que seria enviado, sem acessar a API")
    add_selection_args(plan)

    submit = sub.add_parser("submit", help="Envia um job pago ao Batch API")
    add_selection_args(submit)
    submit.add_argument(
        "--confirm-paid",
        action="store_true",
        help="Confirma que a submissão paga foi autorizada",
    )
    submit.add_argument(
        "--confirm-all",
        metavar="FRASE",
        help='Para --all, use exatamente "PROCESSAR_TODAS_AS_FOTOS"',
    )

    collect = sub.add_parser("collect", help="Consulta um job e salva resultados prontos")
    collect.add_argument(
        "job",
        nargs="?",
        help="Nome do job ou arquivo .json; se omitido, usa o pendente mais recente",
    )
    return result


def add_selection_args(command: argparse.ArgumentParser) -> None:
    group = command.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, default=1, help="Quantidade positiva (padrão: 1)")
    group.add_argument("--all", action="store_true", help="Seleciona todas as fotos")


def load_environment() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT / ".env")


def discover(input_dir: Path) -> list[Path]:
    if not input_dir.is_dir():
        raise SystemExit(f"Diretório de entrada inexistente: {input_dir}")
    return sorted(
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def select_images(args: argparse.Namespace) -> list[Path]:
    discovered = discover(args.input_dir)
    images = [path for path in discovered if not (args.output_dir / path.name).exists()]
    args.skipped_existing = len(discovered) - len(images)
    if args.all:
        return images
    if args.limit < 1:
        raise SystemExit("--limit deve ser um inteiro positivo")
    return images[: args.limit]


def describe_plan(images: list[Path], args: argparse.Namespace) -> None:
    total = sum(path.stat().st_size for path in images)
    model = args.model or os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    print(f"Entrada: {args.input_dir}")
    print(f"Saída:  {args.output_dir}")
    print(f"Modelo:  {model}")
    print(f"Já existentes no destino: {args.skipped_existing}")
    print(f"Imagens: {len(images)} ({total / 1024 / 1024:.2f} MiB antes do base64)")
    for path in images:
        print(f"  - {path.name}")


def require_paid_confirmation(args: argparse.Namespace, images: list[Path]) -> None:
    if not args.confirm_paid:
        raise SystemExit("Envio cancelado: acrescente --confirm-paid após autorização do custo.")
    if args.all and args.confirm_all != "PROCESSAR_TODAS_AS_FOTOS":
        raise SystemExit(
            'Envio total cancelado: use --confirm-all "PROCESSAR_TODAS_AS_FOTOS".'
        )


def api_client():
    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit("Dependências ausentes. Execute: pip install -r requirements.txt") from exc
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("Preencha GEMINI_API_KEY no arquivo .env antes de enviar ou coletar.")
    return genai.Client(api_key=key)


def image_part(path: Path) -> dict:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def submit_job(images: list[Path], args: argparse.Namespace) -> None:
    encoded_size = sum(((path.stat().st_size + 2) // 3) * 4 for path in images)
    if encoded_size > MAX_INLINE_BYTES:
        raise SystemExit(
            "Lote maior que o limite seguro de 18 MiB após base64. "
            "Divida-o em lotes menores antes de enviar."
        )
    requests = [
        {
            "contents": [{"role": "user", "parts": [image_part(path), {"text": PROMPT}]}],
            "config": {"response_modalities": ["TEXT", "IMAGE"]},
        }
        for path in images
    ]
    client = api_client()
    model = args.model or os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    job = client.batches.create(
        model=model,
        src=requests,
        config={"display_name": f"restauracao-etfsp-{datetime.now():%Y%m%d-%H%M%S}"},
    )
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "job": job.name,
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(args.input_dir.resolve()),
        "output_dir": str(args.output_dir.resolve()),
        "files": [path.name for path in images],
    }
    record_path = JOBS_DIR / f"{safe_job_name(job.name)}.json"
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Job enviado: {job.name}")
    print(f"Registro local: {record_path}")
    print(f"Quando terminar, execute: python3 restaurar_fotos.py collect {job.name}")


def safe_job_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def read_record(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Registro de job inválido: {path}: {exc}") from exc


def load_record(job_arg: str | None) -> tuple[Path, dict]:
    if job_arg is None:
        terminal_states = {
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
        }
        pending: list[tuple[float, Path, dict]] = []
        for path in JOBS_DIR.glob("*.json") if JOBS_DIR.is_dir() else []:
            record = read_record(path)
            if record.get("collected_at") or record.get("last_state") in terminal_states:
                continue
            pending.append((path.stat().st_mtime, path, record))
        if not pending:
            raise SystemExit("Nenhum job pendente encontrado em .batch_jobs.")
        _, path, record = max(pending, key=lambda item: item[0])
        print(f"Job omitido; usando o pendente mais recente: {record['job']}")
        return path, record

    supplied = Path(job_arg)
    candidates = [supplied, JOBS_DIR / f"{safe_job_name(job_arg)}.json"]
    for path in candidates:
        if path.is_file():
            return path, read_record(path)
    raise SystemExit(f"Registro do job não encontrado para: {job_arg}")


def save_image(data: bytes, destination: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Dependências ausentes. Execute: pip install -r requirements.txt") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(data)) as image:
        if destination.suffix.lower() in {".jpg", ".jpeg"}:
            image.convert("RGB").save(destination, format="JPEG", quality=95)
        elif destination.suffix.lower() == ".webp":
            image.save(destination, format="WEBP", quality=95)
        else:
            image.save(destination, format="PNG")


def collect_job(job_arg: str | None) -> None:
    record_path, record = load_record(job_arg)
    client = api_client()
    job = client.batches.get(name=record["job"])
    state = job.state.name
    record["last_state"] = state
    record["checked_at"] = datetime.now(timezone.utc).isoformat()
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Job: {record['job']}")
    print(f"Estado: {state}")
    if state != "JOB_STATE_SUCCEEDED":
        if state in {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}:
            raise SystemExit(f"O job terminou sem sucesso: {getattr(job, 'error', '')}")
        print("Ainda não terminou; tente novamente mais tarde.")
        return

    responses = job.dest.inlined_responses or []
    if len(responses) != len(record["files"]):
        raise SystemExit("Quantidade de respostas diferente da quantidade de arquivos; nada foi salvo.")
    output_dir = Path(record["output_dir"])
    saved = 0
    for filename, inline_response in zip(record["files"], responses, strict=True):
        if inline_response.error:
            print(f"ERRO {filename}: {inline_response.error}", file=sys.stderr)
            continue
        parts = inline_response.response.candidates[0].content.parts
        image_parts = [part for part in parts if part.inline_data]
        if len(image_parts) != 1:
            print(f"ERRO {filename}: resposta não contém exatamente uma imagem", file=sys.stderr)
            continue
        destination = output_dir / filename
        if destination.exists():
            print(f"PULADO {filename}: destino já existe", file=sys.stderr)
            continue
        save_image(image_parts[0].inline_data.data, destination)
        print(f"SALVO {destination}")
        saved += 1
    record["collected_at"] = datetime.now(timezone.utc).isoformat()
    record["saved"] = saved
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Concluído: {saved} imagem(ns) salva(s).")


def main() -> None:
    load_environment()
    args = parser().parse_args()
    if args.command == "collect":
        collect_job(args.job)
        return
    images = select_images(args)
    if not images:
        if args.skipped_existing:
            raise SystemExit(
                f"Nenhuma imagem pendente: {args.skipped_existing} arquivo(s) "
                "já existem no destino."
            )
        raise SystemExit("Nenhuma imagem compatível encontrada.")
    describe_plan(images, args)
    if args.command == "plan":
        print("Modo de planejamento: nenhuma chamada à API foi feita.")
        return
    require_paid_confirmation(args, images)
    submit_job(images, args)


if __name__ == "__main__":
    main()
