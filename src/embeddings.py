"""
embeddings.py - Layer 3 (Bolum A): Foundry Local ile embedding uretimi
======================================================================

Metni sayisal vektorlere cevirir. Foundry Local'in native embedding
client'ini kullanir (paket: foundry-local-sdk-winml).

Model cihaza YALNIZCA BIR KEZ yuklenir (lazy singleton): ilk cagriada
indirilir/yuklenir, sonraki cagriada hazir modeli tekrar kullanir. Bu,
tekrar tekrar yukleme maliyetinden kacinmak icin onemlidir.

Not: Bu modul, foundry_local_sdk kurulu olmadan da import edilebilir;
SDK yalnizca embedding fonksiyonlari ilk cagrildiginda ithal edilir.
Boylece SDK'ya ihtiyac duymayan katmanlar (ingestion vb.) etkilenmez.
"""

from __future__ import annotations

from . import config

# Lazy singleton durumu - modul seviyesinde tutulur
_model = None            # Yuklenmis Foundry Local embedding modeli
_embedding_client = None  # Modelden alinan embedding client


def _get_model():
    """Embedding modelini (gerekirse indirip) yukler ve onbellekler."""
    global _model
    if _model is not None:
        return _model

    # SDK'yi burada ithal ediyoruz ki modul import'u SDK'ya bagli olmasin.
    from foundry_local_sdk import Configuration, FoundryLocalManager

    cfg = Configuration(app_name=config.APP_NAME)
    FoundryLocalManager.initialize(cfg)
    manager = FoundryLocalManager.instance

    print(f"Embedding modeli hazirlaniyor: {config.EMBEDDING_MODEL}")
    model = manager.catalog.get_model(config.EMBEDDING_MODEL)

    # Ilk calistirmada model indirilir (sonrakilerde onbellekten gelir).
    model.download(
        lambda progress: print(f"\r  indiriliyor: {progress:.1f}%", end="", flush=True)
    )
    print()  # ilerleme satirini kapat
    model.load()
    print("  model yuklendi.")

    _model = model
    return _model


def _get_client():
    """Embedding client'ini (onbellekli) dondurur."""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = _get_model().get_embedding_client()
    return _embedding_client


def embed_text(text: str) -> list[float]:
    """Tek bir metni embedding vektorune cevirir."""
    client = _get_client()
    response = client.generate_embedding(text)
    return list(response.data[0].embedding)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Birden fazla metni tek seferde (batch) embed eder.

    Ingestion sirasinda tum chunk'lari verimli sekilde vektorlestirmek icin
    kullanilir. Donen listenin sirasi girdi sirasiyla ayindir.
    """
    if not texts:
        return []
    client = _get_client()
    response = client.generate_embeddings(texts)
    return [list(item.embedding) for item in response.data]


def unload() -> None:
    """Modeli bellekten bosaltir (program sonunda cagrilabilir)."""
    global _model, _embedding_client
    if _model is not None:
        _model.unload()
        _model = None
        _embedding_client = None
