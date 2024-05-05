from pokemontcgsdk import Set
from pokemontcgsdk import RestClient


def get_all_sets(tcg_api_key):
    RestClient.configure(tcg_api_key)
    sets = Set.all()
    all_sets_data = []

    for card_set in sets:
        all_sets_data.append({"image_URL": card_set.images.logo, "name": card_set.name, "series": card_set.series,
                              "release_date": card_set.releaseDate, "id": card_set.id})

    all_sets_data = list(sorted(all_sets_data, key=lambda item: item["release_date"], reverse=True))
    return all_sets_data
