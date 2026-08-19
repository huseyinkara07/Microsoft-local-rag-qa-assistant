"""
foundry.py - Foundry Local SDK ortak altyapisi
===============================================

FoundryLocalManager bir singleton'dir; bir kez baslatilir. Hem embedding
(Layer 3) hem chat (Layer 5) modelleri ayni manager'i paylasir. Bu modul o
paylasilan baslatmayi ve model yuklemeyi tek yerde toplar; boylece manager
iki kez baslatilmaya calisilmaz.

Not: SDK yalnizca bu fonksiyonlar cagrildiginda ithal edilir (lazy import),
boylece SDK kurulu olmadan da diger katmanlar import edilebilir.
"""

from __future__ import annotations

from . import config

_manager = None            # FoundryLocalManager singleton
_eps_registered = False    # Execution provider'lar bir kez kaydedilir


def get_manager():
    """FoundryLocalManager'i (gerekirse baslatarak) dondurur.

    FoundryLocalManager bir singleton'dir. Streamlit'in yeniden yuklemesi gibi
    durumlarda bizim modul global'imiz sifirlanabilir ama SDK'nin singleton'i
    hafizada baslatilmis kalir. Bu yuzden initialize() 'zaten baslatildi' hatasi
    verirse bunu yutup mevcut instance'i kullaniriz.
    """
    global _manager
    if _manager is not None:
        return _manager

    from foundry_local_sdk import Configuration, FoundryLocalManager

    try:
        cfg = Configuration(app_name=config.APP_NAME)
        FoundryLocalManager.initialize(cfg)
    except Exception:
        # Zaten baslatilmis olabilir; instance yoksa gercek bir hata demektir.
        if FoundryLocalManager.instance is None:
            raise

    _manager = FoundryLocalManager.instance
    return _manager


def _ensure_eps_registered() -> None:
    """Donanim hizlandirma saglayicilarini (CPU/GPU/NPU) bir kez indirip kaydeder.

    Windows (WinML) uzerinde en iyi performans icin onerilir. Idempotent'tir;
    yeni bir EP surumu cikmadikca tekrar indirme yapmaz.
    """
    global _eps_registered
    if _eps_registered:
        return

    manager = get_manager()
    state = {"current": ""}

    def _progress(ep_name: str, percent: float) -> None:
        if ep_name != state["current"]:
            if state["current"]:
                print()
            state["current"] = ep_name
        print(f"\r  EP {ep_name:<28} {percent:5.1f}%", end="", flush=True)

    manager.download_and_register_eps(progress_callback=_progress)
    if state["current"]:
        print()
    _eps_registered = True


def load_model(alias: str):
    """Verilen alias'li modeli (gerekirse indirip) yukler ve dondurur.

    Model ilk kez yuklenirken cihaza indirilir; sonraki cagrilarda onbellekten
    gelir. Cagiran taraf donen modeli onbelleklemeli (tekrar yuklememek icin).
    """
    _ensure_eps_registered()
    manager = get_manager()

    print(f"Model hazirlaniyor: {alias}")
    model = manager.catalog.get_model(alias)
    model.download(
        lambda progress: print(f"\r  indiriliyor: {progress:.1f}%", end="", flush=True)
    )
    print()
    model.load()
    print(f"  '{alias}' yuklendi.")
    return model
