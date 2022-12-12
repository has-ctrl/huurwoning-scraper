BASE_PATH = "C:/Users/Dominique/Documents/GitHub/huurwoning-scraper/"


def log_homes(homes: list[str]) -> list[str]:
    """
    Locally log the list of filtered home urls; and return homes that are new.
    """
    with open(f"{BASE_PATH}/scraped_homes.txt", "r") as f:
        logged_homes = set(f.read().splitlines())

    new_homes = [home for home in homes if home not in logged_homes]
    all_homes = set(homes).union(logged_homes)

    with open(f"{BASE_PATH}/scraped_homes.txt", "w") as f:
        for home in all_homes:
            f.write(f"{home}\n")

    return new_homes
