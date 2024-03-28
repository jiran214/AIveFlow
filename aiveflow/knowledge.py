#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Any

from embedchain import App
from embedchain.config import ChromaDbConfig
from embedchain.models.data_type import DataType
from embedchain.vectordb.chroma import ChromaDB

from aiveflow import settings


class KnowledgeBase(App):

    @classmethod
    def get(cls, collection):
        return cls(db=ChromaDB(ChromaDbConfig(collection_name=collection, dir=settings.VECTOR_DB_DIR, allow_reset=True)))

    def add(
        self,
        source: Any,
        data_type: Optional[DataType] = None,
        auto_update: bool = False,
        dry_run=False,
        # metadata: Optional[dict[str, Any]] = None,
        # config: Optional[AddConfig] = None,
        # loader: Optional[BaseLoader] = None,
        # chunker: Optional[BaseChunker] = None,
        **kwargs: Optional[dict[str, Any]]
    ):
        return super().add(
            source=source,
            data_type=data_type,
            dry_run=dry_run,
            **kwargs
        )

