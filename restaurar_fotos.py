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
MAX_TEST_IMAGES = 5
MAX_INLINE_BYTES = 18 * 1024 * 1024  # margem abaixo do limite oficial de 20 MB
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

PROMPT = """Restore and realistically colorize this old black-and-white school photograph while preserving the original photographic content as faithfully as possible.

Correct scratches, dust, stains, fading, uneven exposure, contrast problems, minor blur, film grain, xerographic degradation, and scanning artifacts. Improve facial clarity and fine details conservatively.

Do not change facial features, expressions, hairstyle, clothing, objects, body proportions, pose, framing, background, or historical context. Do not invent missing facial details or modernize the scene. Apply subtle, historically plausible colors with natural skin tones. Preserve the original composition and photographic character.

The result must look like a professionally restored and carefully colorized version of the original photograph, not an AI-generated recreation. Return one restored image without captions, borders, or explanatory text."""


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
    collect.add_argument("job", help="Nome do job, por exemplo batches/123, ou arquivo .json")
    return result


def add_selection_args(command: argparse.ArgumentParser) -> None:
    group = command.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, default=1, help="Quantidade (1 a 5; padrão: 1)")
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
    images = discover(args.input_dir)
    if args.all:
        return images
    if args.limit < 1 or args.limit > MAX_TEST_IMAGES:
        raise SystemExit(f"--limit deve estar entre 1 e {MAX_TEST_IMAGES}")
    return images[: args.limit]


def describe_plan(images: list[Path], args: argparse.Namespace) -> None:
    total = sum(path.stat().st_size for path in images)
    model = args.model or os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    print(f"Entrada: {args.input_dir}")
    print(f"Saída:  {args.output_dir}")
    print(f"Modelo:  {model}")
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
    if not args.all and len(images) > MAX_TEST_IMAGES:
        raise SystemExit(f"Um teste não pode exceder {MAX_TEST_IMAGES} imagens.")


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


def load_record(job_arg: str) -> tuple[Path, dict]:
    supplied = Path(job_arg)
    candidates = [supplied, JOBS_DIR / f"{safe_job_name(job_arg)}.json"]
    for path in candidates:
        if path.is_file():
            return path, json.loads(path.read_text(encoding="utf-8"))
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


def collect_job(job_arg: str) -> None:
    record_path, record = load_record(job_arg)
    client = api_client()
    job = client.batches.get(name=record["job"])
    state = job.state.name
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
        raise SystemExit("Nenhuma imagem compatível encontrada.")
    describe_plan(images, args)
    if args.command == "plan":
        print("Modo de planejamento: nenhuma chamada à API foi feita.")
        return
    require_paid_confirmation(args, images)
    submit_job(images, args)


if __name__ == "__main__":
    main()
