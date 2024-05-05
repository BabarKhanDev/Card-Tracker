from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
from scripts.database import cache_set


def get_all_sets(tcg_api_key: str, conn):
    RestClient.configure(tcg_api_key)
    sets = Set.all()
    all_sets_data = []

    for set in sets:
        all_sets_data.append({"image_URL": set.images.logo, "name": set.name, "series": set.series,
                              "release_date": set.releaseDate, "id": set.id})
        cache_set(conn, set)

    all_sets_data = list(sorted(all_sets_data, key=lambda item: item["release_date"], reverse=True))
    return all_sets_data
