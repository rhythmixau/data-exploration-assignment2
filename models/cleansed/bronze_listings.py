def set_special_property(listing_id) -> bool:
    special_properties = [3928833, 2953058, 15455305, 17537893, 18051877, 18616208, 22296097, 24535740, 22296197,
                          30035166, 33998396, 27629043, 33007610, 2952861, 25018204, 2276383, 23373090, 34592851,
                          22295960, 23372850, 8736827, 4823682]
    if listing_id in special_properties:
        return True
    else:
        return False


def model(dbt, session):
    cleansed_listings = dbt.ref("cleansed_listings")
    # Create a new column called 'is_special_property' with a default value of 'False'
    print(f"Cleansed listings type: {type(cleansed_listings)}")
    bronze_listings = cleansed_listings.df()
    bronze_listings["is_special_property"] = bronze_listings["listing_id"].apply(set_special_property)
    # These are filming locations, not accommodations

    return bronze_listings
