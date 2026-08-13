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

PROMPT = """Create a high-quality, fully colorized restoration of this severely degraded scanned school composite. The restored version will be displayed beside the original and should prioritize visual clarity and photographic quality.

Perform an intensive restoration, not simple tinting. Strongly remove xerox noise, grain, dust, stains, fading, blur and scanning artifacts. Correct exposure, contrast and tonal range. Reconstruct plausible natural detail in faces, skin, eyes, hair and clothing wherever degradation has destroyed fine detail. Produce sharp, clean, realistic portraits with natural skin tones, convincing texture and historically plausible colors. Aim for the quality of well-preserved original portrait photographs rather than the appearance of a cleaned photocopy.

Keep each person recognizably the same: retain their basic facial geometry, expression, pose, hairstyle type and clothing type. Do not beautify, modernize or deliberately change identity. Reasonable AI reconstruction of lost fine detail is allowed, but it must remain consistent with the visible evidence.

Treat every text region as part of the original photograph, not as text to transcribe. Do not perform OCR, rewrite, correct, autocomplete or invent letters. Preserve clearly readable text; leave uncertain text visually uncertain.

Before editing, identify and count only the clearly visible original portrait photographs. The output must contain exactly that same number of portraits, in exactly the same cells and positions. Every cell that is empty in the source must remain empty. Do not turn faint show-through, paper shadows or barely visible reversed images into portraits, anywhere on the page. Do not create a new row, move a portrait to another cell or repeat a person or label.

Return one polished restored image with the same page composition."""


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


def save_comparison(data: bytes, original_path: Path, destination: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError as exc:
        raise SystemExit("Dependências ausentes. Execute: pip install -r requirements.txt") from exc

    label = "Imagem colorizada por IA"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(original_path) as original_image, Image.open(io.BytesIO(data)) as improved_image:
        original = ImageOps.exif_transpose(original_image).convert("RGB")
        improved = ImageOps.exif_transpose(improved_image).convert("RGB")
        if improved.size != original.size:
            improved = improved.resize(original.size, Image.Resampling.LANCZOS)

        width, height = original.size
        footer_height = max(36, round(height * 0.035))
        separator_width = max(2, round(width * 0.002))
        canvas = Image.new("RGB", (width * 2 + separator_width, height + footer_height), "white")
        canvas.paste(original, (0, 0))
        canvas.paste(improved, (width + separator_width, 0))

        draw = ImageDraw.Draw(canvas)
        draw.rectangle((width, 0, width + separator_width - 1, height - 1), fill=(205, 205, 205))
        font_size = max(14, round(footer_height * 0.42))
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()
        box = draw.textbbox((0, 0), label, font=font)
        text_width = box[2] - box[0]
        text_height = box[3] - box[1]
        text_x = width + separator_width + (width - text_width) // 2
        text_y = height + (footer_height - text_height) // 2 - box[1]
        draw.text((text_x, text_y), label, fill=(90, 90, 90), font=font)

        if destination.suffix.lower() in {".jpg", ".jpeg"}:
            canvas.save(destination, format="JPEG", quality=95, subsampling=0)
        elif destination.suffix.lower() == ".webp":
            canvas.save(destination, format="WEBP", quality=95)
        else:
            canvas.save(destination, format="PNG")


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
    input_dir = Path(record["input_dir"])
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
        original_path = input_dir / filename
        if not original_path.is_file():
            print(f"ERRO {filename}: original não encontrado", file=sys.stderr)
            continue
        save_comparison(image_parts[0].inline_data.data, original_path, destination)
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
