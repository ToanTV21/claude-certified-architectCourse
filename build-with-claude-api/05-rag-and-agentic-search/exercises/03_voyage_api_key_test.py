"""
Exercise 03: Test VOYAGE_API_KEY
Session: RAG and Agentic Search
Objective: Kiem tra VOYAGE_API_KEY trong .env con hoat dong khong, bang cach
goi thu 1 request embedding don gian toi VoyageAI API.
"""

from dotenv import load_dotenv  # doc bien moi truong tu file .env
import voyageai  # SDK chinh thuc cua VoyageAI
import os

load_dotenv()  # nap VOYAGE_API_KEY tu .env vao os.environ

EMBED_MODEL = "voyage-3.5-lite"  # model embedding re, du de test connectivity


def main():
    api_key = os.environ.get("VOYAGE_API_KEY")
    print(f"[CHECK] VOYAGE_API_KEY co ton tai trong .env khong: {bool(api_key)}")

    if not api_key:
        print("[CHECK] Khong tim thay VOYAGE_API_KEY -> dung lai, kiem tra file .env")
        return

    print(f"[CHECK] Key preview: {api_key[:6]}...{api_key[-4:]}")

    client = voyageai.Client()  # tu doc VOYAGE_API_KEY tu os.environ
    print(f"[TEST] Goi thu VoyageAI embedding API voi model={EMBED_MODEL} ...")

    sample_text = ["Hello, this is a test to verify the Voyage API key."]

    try:
        result = client.embed(sample_text, model=EMBED_MODEL, input_type="document")
        embedding = result.embeddings[0]  # lay vector embedding dau tien
        print("[TEST] Goi API thanh cong! Key hoat dong binh thuong.")
        print(f"[TEST] So chieu (dimensions) cua embedding vector: {len(embedding)}")
        print(f"[TEST] 5 gia tri dau tien cua vector: {embedding[:5]}")
        print(f"[TEST] Token usage: {result.total_tokens}")
    except Exception as exc:
        # bat moi loi (sai key, het quota, network...) de bao ro rang thay vi crash
        print(f"[TEST] Goi API that bai: {exc}")


if __name__ == "__main__":
    main()
