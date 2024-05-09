from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
from scripts.database import cache_set


def cache_all_sets(tcg_api_key: str, conn) -> None:
    RestClient.configure(tcg_api_key)
    for s in Set.all():
        cache_set(conn, s)
