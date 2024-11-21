async def calculate_value(skyblockCatacombs: dict, skyblockSkills: dict, skyblockHotm: dict, 
                          skyblockSlayers: dict, skyblockLiquideCoins: int, 
                          skyblockunsoulboundNetworth: int, skyblocksoulboundNetworth: int, 
                          profilemembers: int, gamemode: str) -> dict:
    
    level_data = {
        0: 0, 1: 50, 2: 175, 3: 375, 4: 675, 5: 1175, 6: 1925, 7: 2925, 8: 4425, 9: 6425,
        10: 9925, 11: 14925, 12: 22425, 13: 32425, 14: 47425, 15: 67425, 16: 97425,
        17: 147425, 18: 222425, 19: 322425, 20: 522425, 21: 822425, 22: 1222425,
        23: 1722425, 24: 2322425, 25: 3022425, 26: 3822425, 27: 4722425, 28: 5722425,
        29: 6822425, 30: 8022425, 31: 9322425, 32: 10722425, 33: 12222425, 34: 13822425,
        35: 15522425, 36: 17322425, 37: 19222425, 38: 21222425, 39: 23322425, 40: 25522425,
        41: 27822425, 42: 30222425, 43: 32722425, 44: 35322425, 45: 38072425, 46: 40972425,
        47: 44072425, 48: 47472425, 49: 51172425, 50: 55172425, 51: 59472425, 52: 64072425,
        53: 68972425, 54: 74172425, 55: 79672425, 56: 85472425, 57: 91572425, 58: 97972425,
        59: 104672425, 60: 111672425
    }
    
    skill_values = {
        "farming": 25,
        "mining": 30,
        "combat": 17,
        "foraging": 15,
        "fishing": 10,
        "enchanting": 5,
        "alchemy": 8,
        "taming": 3,
        "carpentry": 3,
        "runecrafting": 0,
        "social": 0,
        "avg": 0,
    }
    
    total_value = 0
    skill_values_details = []  
    embed = {}
    total_skill_value = 0
    # Calculate skill values
    for skill, level in skyblockSkills.items():
        exp_at_level = level_data[round(float(level))]
        try:
            skill_value_per_exp = skill_values[skill.lower()] / level_data[60] 
        except:
            continue
        skill_value = skill_value_per_exp * exp_at_level 
        skill_values_details.append(f"{skill_value:,.2f}")
        total_value = total_value + skill_value 
        total_skill_value += skill_value
        embed[skill] = f"{skill_value:,.2f}"
    embed['skill_value'] = f"{total_skill_value:,.2f}"
    # Calculate Catacombs value
    catacombs_value = 0
    catacombs_value = skyblockCatacombs['level'] * skyblockCatacombs['level'] * skyblockCatacombs['level'] / 2000
    total_value += catacombs_value
    embed["Catacombs Value"] = f"{catacombs_value:,.2f}"

    # Calculate HOTM value
    hotm_value = skyblockHotm['HotmLevel'] * skyblockHotm['HotmLevel'] * skyblockHotm['HotmLevel'] / 7
    embed['Hotm level value'] = f"{hotm_value:,.2f}"
    powder_value = skyblockHotm['gemstonePowder'] * 0.0000005
    mithril_value = skyblockHotm['mithrilPowder'] * 0.0000005
    embed['gemstone'] = f"{powder_value:,.2f}"
    embed['mithril'] = f"{mithril_value:,.2f}"
    hotm_value += powder_value + mithril_value
    total_value += hotm_value
    embed["HOTM Value"] = f"{hotm_value:,.2f}"

    # Calculate Slayer value
    slayer_value = sum(slayer_level * slayer_level / 15 for slayer_level in skyblockSlayers.values())  
    total_value += slayer_value
    embed["Slayer Value"] = f"{slayer_value:,.2f}"

    # Calculate Liquid Coins value
    liquid_coins_value = skyblockLiquideCoins * 0.000000025
    total_value += liquid_coins_value
    embed["Liquid Coins Value"] = f"{liquid_coins_value:,.2f}"

    # Store the net worth values (unchanged)
    unsoulbound_value = skyblockunsoulboundNetworth * 0.000000022
    soulbound_value = skyblocksoulboundNetworth * 0.000000003
    embed["Unsoulbound Networth"] = f"{unsoulbound_value:,.2f}"
    embed["Soulbound Networth"] = f"{soulbound_value:,.2f}"
    total_value += unsoulbound_value 
    total_value += soulbound_value
    # Apply profile members adjustment
    if profilemembers == 1:  # Solo
        embed['adjustment'] = "1"
        adjustment = 1.0
    elif profilemembers == 2:  # Duo
        embed['adjustment'] = "0.65"  
        adjustment = 0.65 
    else:  # Four or more
        embed['adjustment'] = "0.55"  
        adjustment = 0.55  
    if gamemode == "Normal":
        embed['gamemode adjustment'] = "1"
        gamemodeAjustment = 1.0
    elif gamemode == "ironman":
        embed['gamemode adjustment'] = "0.5"  
        gamemodeAjustment = 0.55  
    else:
        embed['gamemode adjustment'] = "0.35"
        gamemodeAjustment = 0.35
    total_value *= adjustment 
    total_value *= gamemodeAjustment
    embed['total value'] = f"{total_value:,.2f}"
    return embed

async def calculate_lowball(skyblockCatacombs: dict, skyblockSkills: dict, skyblockHotm: dict, 
                             skyblockSlayers: dict, skyblockLiquideCoins: int, 
                             skyblockunsoulboundNetworth: int, skyblocksoulboundNetworth: int, 
                             profilemembers: int, gamemode: str) -> dict:
    
    level_data = {
        0: 0, 1: 50, 2: 175, 3: 375, 4: 675, 5: 1175, 6: 1925, 7: 2925, 8: 4425, 9: 6425,
        10: 9925, 11: 14925, 12: 22425, 13: 32425, 14: 47425, 15: 67425, 16: 97425,
        17: 147425, 18: 222425, 19: 322425, 20: 522425, 21: 822425, 22: 1222425,
        23: 1722425, 24: 2322425, 25: 3022425, 26: 3822425, 27: 4722425, 28: 5722425,
        29: 6822425, 30: 8022425, 31: 9322425, 32: 10722425, 33: 12222425, 34: 13822425,
        35: 15522425, 36: 17322425, 37: 19222425, 38: 21222425, 39: 23322425, 40: 25522425,
        41: 27822425, 42: 30222425, 43: 32722425, 44: 35322425, 45: 38072425, 46: 40972425,
        47: 44072425, 48: 47472425, 49: 51172425, 50: 55172425, 51: 59472425, 52: 64072425,
        53: 68972425, 54: 74172425, 55: 79672425, 56: 85472425, 57: 91572425, 58: 97972425,
        59: 104672425, 60: 111672425
    }
    
    skill_values = {
        "farming": 20,
        "mining": 23,
        "combat": 12,
        "foraging": 12,
        "fishing": 7,
        "enchanting": 3,
        "alchemy": 5,
        "taming": 0,
        "carpentry": 0,
        "runecrafting": 0,
        "social": 0,
        "avg": 0,
    }
    total_value = 0
    skill_values_details = []  
    embed = {}
    total_skill_value = 0
    for skill, level in skyblockSkills.items():
        exp_at_level = level_data[round(float(level))]
        try:
            skill_value_per_exp = skill_values[skill.lower()] / level_data[60] 
        except:
            continue
        skill_value = skill_value_per_exp * exp_at_level 
        skill_values_details.append(f"{skill_value:,.2f}")
        total_value = total_value + skill_value 
        total_skill_value += skill_value
        embed[skill] = f"{skill_value:,.2f}"
    embed['skill_value'] = f"{total_skill_value:,.2f}"
    # Calculate Catacombs value
    catacombs_value = 0
    catacombs_value = skyblockCatacombs['level'] * skyblockCatacombs['level'] * skyblockCatacombs['level'] / 2000
    total_value += catacombs_value
    embed["Catacombs Value"] = f"{catacombs_value:,.2f}"

    # Calculate HOTM value
    hotm_value = skyblockHotm['HotmLevel'] * skyblockHotm['HotmLevel'] * skyblockHotm['HotmLevel'] / 12
    embed['Hotm level value'] = f"{hotm_value:,.2f}"
    powder_value = skyblockHotm['gemstonePowder'] * 0.0000015
    mithril_value = skyblockHotm['mithrilPowder'] * 0.0000015
    embed['gemstone'] = f"{powder_value:,.2f}"
    embed['mithril'] = f"{mithril_value:,.2f}"
    hotm_value += powder_value + mithril_value
    total_value += hotm_value
    embed["HOTM Value"] = f"{hotm_value:,.2f}"

    # Calculate Slayer value
    slayer_value = sum(slayer_level * slayer_level / 15 for slayer_level in skyblockSlayers.values())  
    total_value += slayer_value
    embed["Slayer Value"] = f"{slayer_value:,.2f}"

    # Calculate Liquid Coins value
    liquid_coins_value = skyblockLiquideCoins * 0.00000002
    total_value += liquid_coins_value
    embed["Liquid Coins Value"] = f"{liquid_coins_value:,.2f}"

    # Store the net worth values (unchanged)
    unsoulbound_value = skyblockunsoulboundNetworth * 0.000000013
    soulbound_value = skyblocksoulboundNetworth * 0.000000002
    embed["Unsoulbound Networth"] = f"{unsoulbound_value:,.2f}"
    embed["Soulbound Networth"] = f"{soulbound_value:,.2f}"
    total_value += unsoulbound_value 
    total_value += soulbound_value
    # Apply profile members adjustment
    if profilemembers == 1:  # Solo
        embed['adjustment'] = "1"
        adjustment = 1.0
    elif profilemembers == 2:  # Duo
        embed['adjustment'] = "0.65"  
        adjustment = 0.65 
    else:  # Four or more
        embed['adjustment'] = "0.55"  
        adjustment = 0.55  
    if gamemode == "Normal":
        embed['gamemode adjustment'] = "1"
        gamemodeAjustment = 1.0
    elif gamemode == "ironman":
        embed['gamemode adjustment'] = "0.45"  
        gamemodeAjustment = 0.55  
    else:
        embed['gamemode adjustment'] = "0.35"
        gamemodeAjustment = 0.35
    total_value *= adjustment 
    total_value *= gamemodeAjustment
    embed['total value'] = f"{total_value:,.2f}"
    return embed