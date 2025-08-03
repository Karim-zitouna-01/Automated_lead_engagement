


# from personal.fusion_search import search_all
# from personal.tavily import get_enriched_personnel_profiles


#lancer la recherche pour un lead


#on a la liste de key personal
#on a l icp
#on a une liste de usernames linkedin, twitter, instagram de chaque key personal
#et on a le company name



# personnel_list = [
#         {"name": "Thierry Millet", "title": "CEO, Orange Tunisie", "linkedin_profile": None},
#         {"name": "Siwar Farhat", "title": "Former Director Sofrecom Tunisia", "linkedin_profile": None}
#     ]
# company_name = "Orange Tunisie"
# icp = {
#     "industry": {"tier1_core_focus": ["digital transformation", "telecom services"]},
#     "pain_points": ["digital adoption among SMEs", "cybersecurity services uptake", "start-up acceleration"]
# }

# usernames_list=[{"name": "Thierry Millet", "linkedin_profile": "l_id_linkedin",
#                 "twitter_profile": "l_id_twitter",
#                 "instagram_profile": "l_id_instagram"},
#                {"name": "Siwar Farhat", "linkedin_profile": "s_id_linkedin",
#                 "twitter_profile": "s_id_twitter",
#                 "instagram_profile": "s_id_instagram"}]




import json
import os

from Automated_lead_engagement.Lead_Engagement.personal_research.social_media import search_all
from tavily import get_enriched_personnel_profiles

def write_profiles_to_files(profiles, output_dir="profiles"):
    """
    Wraps each profile in a 'tavily' dictionary and writes it to a separate JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)

    for profile in profiles:
        name = profile.get("name", "unknown").replace(" ", "_")
        filename = f"{name}.json"
        filepath = os.path.join(output_dir, filename)

        wrapped_profile = {"tavily": profile}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(wrapped_profile, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(profiles)} profiles written (wrapped in 'tavily') to '{output_dir}/'")


import os
import json

def append_social_search_to_file(name, social_data, output_dir="profiles"):
    filename = f"{name.replace(' ', '_')}.json"
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        print(f"⚠️ File not found for {name}")
        return

    # Load existing data
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Merge the social_data at root level
    data.update(social_data)

    # Save it back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Appended social data to {filename}")





def engagement_01(personnel_list, company_name, icp, usernames_list):

    enriched = get_enriched_personnel_profiles(personnel_list, company_name, icp)
    tavvy_personal_data = json.dumps(enriched, indent=2, ensure_ascii=False)

    write_profiles_to_files(tavvy_personal_data)


    for person in usernames_list:
        name = person.get("name")
        if not name:
            continue
        linkedin_id = person.get("linkedin_profile", "").strip()
        twitter_id = person.get("twitter_profile", "").strip()
        insta_id = person.get("instagram_profile", "").strip()

        # Assuming search_all is defined in fusion_search.py
        print("linkedin_id , twitter_id , insta_id")
        print(linkedin_id, twitter_id, insta_id)

        for person in usernames_list:
            name = person.get("name")
            if not name:
                continue
            linkedin_id = person.get("linkedin_profile", "").strip()
            twitter_id = person.get("twitter_profile", "").strip()  
            insta_id = person.get("instagram_profile", "").strip()


            # social_data = search_all(linkedin_id, twitter_id, insta_id)
            social_data = " "
            append_social_search_to_file(name, social_data)




# if __name__ == "__main__":
#     engagement_01(personnel_list, company_name, icp, usernames_list)
