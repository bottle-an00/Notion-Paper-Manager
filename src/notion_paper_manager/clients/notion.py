import requests
import mimetypes

from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

from ..config import settings

class NotionClient:
    def __init__(self, Notion_api_token: str | None = None ,token: str | None = None):
        self.client = Client(auth=token or settings.notion_token)

    # ---------- Notion 블록 유틸 ----------
    @staticmethod
    def _make_paragraph(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
            },
        }

    @staticmethod
    def _make_bulleted(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
            },
        }

    @staticmethod
    def _make_divider() -> Dict[str, Any]:
        return {"object": "block", "type": "divider", "divider": {}}

    @staticmethod
    def _make_heading_toggle(level: int, title: str) -> Dict[str, Any]:
        key = f"heading_{level}"
        return {
            "object": "block",
            "type": key,
            key: {
                "rich_text": [{"type": "text", "text": {"content": title}}],
                "is_toggleable": True,
            },
        }

    def _make_image_block(self, file_path: Path) -> Dict[str, Any]:
        upload_id = self._upload_local_file(file_path)
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "file_upload",
                "file_upload": {"id": upload_id}
            }
        }

    def _guess_mime(self, file_path: Path) -> str:
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime or "application/octet-stream"

    # 간단한 재시도 래퍼 (레이트리밋 등 대비)
    def _with_retry(self, fn, *args, **kwargs):
        for i in range(5):
            try:
                return fn(*args, **kwargs)
            except (APIResponseError, HTTPResponseError) as e:
                status = getattr(e, "status", None)
                if status in (429, 500, 502, 503):
                    time.sleep(1.5 * (i + 1))
                    continue
                raise
        raise RuntimeError("Notion API 재시도 초과")

    def add_paper(
        self,
        database_id: str,
        title: str,
        authors: List[str],
        year: int,
        url: str | None = None,
        file_local_path: Optional[Path] = None,
        figure_dir: Optional[Path] = None,
        table_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        #------------------------------------------properties setting------------------------------------------
        props: Dict[str, Any] = {
            "Title": {"title": [{"text": {"content": title}}]},
            "Year": {"number": year},
            "Inbox": {"checkbox": True},
            "Authors": {
                "rich_text": [
                    {"type": "text", "text": {"content": ", ".join(authors or [])}}
                ]
            },
            "Status": {"select": {"name": "Future"}},
        }

        if url:
            print(url)
            print(file_local_path)
            props["URL"] = {"url": url}

        if file_local_path:
            if file_local_path.stat().st_size < 5 * 1024 * 1024:
                upload_id = self._upload_local_file(Path(file_local_path))
                props["PDF"] = {"files": [{
                    "type": "file_upload",
                    "name": Path(file_local_path).name,
                    "file_upload": {"id": upload_id}
                }]}

        #------------------------------------------------page 구성 설정------------------------------------------
        #------------------------------Figure들을 저장(toggle)---------------------------------------------------
        page = self._with_retry(
            self.client.pages.create,
            parent={"database_id": database_id},
            properties=props
        )
        page_id = page["id"]

        figure_resp = self._with_retry(
            self.client.blocks.children.append,
            block_id=page_id,
            children=[ self._make_heading_toggle(2, "Figures") ]
        )

        figure_block_id = figure_resp["results"][0]["id"]

        figure_children: List[Dict[str, Any]] = []
        if figure_dir and figure_dir.exists():
            for p in sorted(figure_dir.glob("*")):
                if not p.is_file():
                    continue
                mime = self._guess_mime(p)
                if mime.startswith("image/"):               # 이미지만 추가
                    figure_children.append(self._make_image_block(p))

        self._with_retry(
            self.client.blocks.children.append,
            block_id=figure_block_id,
            children=figure_children
        )

        #------------------------------Table들을 저장(toggle)-----------------------------------------------------
        table_resp = self._with_retry(
            self.client.blocks.children.append,
            block_id=page_id,
            children=[ self._make_heading_toggle(2, "Tables") ]
        )

        table_block_id = table_resp["results"][0]["id"]
        table_children: List[Dict[str, Any]] = []

        if table_dir and table_dir.exists():
            for p in sorted(table_dir.glob("*")):
                if not p.is_file():
                    continue
                mime = self._guess_mime(p)
                if mime.startswith("image/"):
                    table_children.append(self._make_image_block(p))  # 이미지면 image 블록

        self._with_retry(
            self.client.blocks.children.append,
            block_id=table_block_id,
            children=table_children
        )
        return page

    def _upload_local_file(self, file_path: Path) -> str:
        NOTION_VERSION = "2022-06-28"
        file_path = Path(file_path)
        mime = self._guess_mime(file_path)

        create = requests.post(
            "https://api.notion.com/v1/file_uploads",
            headers={
                "Authorization": f"Bearer {settings.notion_token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            json={"mode": "single_part", "filename": file_path.name},
            timeout=60
        )
        #print("CREATE RESPONSE:", create.status_code, create.text)
        create.raise_for_status()
        meta = create.json()

        upload_id = meta["id"]
        upload_url = meta["upload_url"]

        with open(file_path, "rb") as f:
            send = requests.post(
                upload_url,
                headers={
                    "Authorization": f"Bearer {settings.notion_token}",
                    "Notion-Version": NOTION_VERSION,
                },
                files={"file": (file_path.name, f, mime)},
                timeout=300
            )
        #print("SEND RESPONSE:", send.status_code, send.text)
        send.raise_for_status()

        return upload_id
