"""
Seed the Supabase vector store with the PolliSync knowledge base.

Usage:
    py -3.12 scripts/seed_embeddings.py

Requires:
    SUPABASE_URL, SUPABASE_SERVICE_KEY, and GEMINI_API_KEY in backend/.env
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agent.embedder import SupabaseVectorStore, embed_text, split_document
from app.agent.prompts import get_embedding_doc


async def main() -> None:
    print("=" * 60)
    print("PolliSync Knowledge Base Embedding Seed")
    print("=" * 60)

    doc = get_embedding_doc()
    chunks = split_document(doc)
    print(f"\nSplit document into {len(chunks)} section chunks")

    all_chunks = []
    for chunk in chunks:
        text = chunk["content"]
        if len(text) > 900:
            sub_chunks = []
            words = text.split()
            for i in range(0, len(words), 600):
                sub = " ".join(words[i:i + 600])
                sub_chunks.append({"header": chunk["header"], "content": sub})
            all_chunks.extend(sub_chunks)
        else:
            all_chunks.append(chunk)

    print(f"Total chunks to embed: {len(all_chunks)}")

    store = SupabaseVectorStore()
    existing = await store.count()
    print(f"Existing embeddings in DB: {existing}")

    if existing > 0:
        answer = input("Delete existing embeddings and re-seed? (y/N): ")
        if answer.lower() == "y":
            await store.delete_all()
            print("Deleted existing embeddings")
        else:
            print("Skipping. Use --force to override.")
            return

    for i, chunk in enumerate(all_chunks):
        print(f"  Embedding chunk {i+1}/{len(all_chunks)}: {chunk['header'][:50]}...")
        vec = await embed_text(chunk["content"])
        chunk["embedding"] = vec
        chunk["metadata"] = {"source": chunk["header"]}

    await store.upsert_embeddings(all_chunks)

    count = await store.count()
    print(f"\nDone! {count} embeddings stored in Supabase.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
