"""Transformersを使うローカルVLM adapter。"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ModelRunner:
    """Transformers経路を遅延ロードし、モデル未取得時はnot_runにする。"""

    def __init__(self, model_id: str, max_new_tokens: int = 4096) -> None:
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.processor = None
        self.model = None
        self.reason: str | None = None

    def load(self) -> bool:
        """モデルとprocessorをロードする。"""
        try:
            from transformers import AutoModelForMultimodalLM, AutoProcessor

            self.processor = AutoProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForMultimodalLM.from_pretrained(
                self.model_id,
                dtype="auto",
                device_map="auto",
            )
            return True
        except Exception as exc:  # noqa: BLE001 - 失敗理由をartifactへ記録する
            self.reason = f"{type(exc).__name__}: {exc}"
            return False

    def generate(self, instruction: str, image_path: Path | None = None) -> str:
        """instructionと任意画像からMarkdown出力を生成する。"""
        if self.processor is None or self.model is None:
            raise RuntimeError("model is not loaded")
        content: list[dict[str, Any]] = [{"type": "text", "text": instruction}]
        if image_path is not None:
            content.insert(0, {"type": "image", "url": str(image_path)})
        messages = [{"role": "user", "content": content}]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)
        input_length = inputs["input_ids"].shape[-1]
        output = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False)
        return self.processor.decode(output[0][input_length:], skip_special_tokens=True)
