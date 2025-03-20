def start_adventure():
    print("Welcome to the Adventure!")
    print("You wake up in a mysterious forest with no memory of how you got here.")
    print("You see two paths ahead of you:")
    print("1. A dark, winding path leading deeper into the forest.")
    print("2. A sunny trail that seems to head toward a village.")
    
    choice = input("Do you choose path 1 or 2? (enter 1 or 2): ").strip()
    
    if choice == "1":
        dark_forest()
    elif choice == "2":
        village_path()
    else:
        print("Invalid choice. Please try again.")
        start_adventure()


def dark_forest():
    print("\nYou venture down the dark, winding path. The forest grows thicker and darker.")
    print("After a while, you encounter a mysterious old man sitting by a fire.")
    print("He beckons you over and offers you a glowing potion.")
    
    choice = input("Do you accept the potion? (yes/no): ").strip().lower()
    
    if choice == "yes":
        print("\nYou drink the potion. Suddenly, your vision clears and you feel a surge of energy!")
        print("The old man smiles and disappears into the night. You now have the strength to face any challenge!")
        enchanted_path()
    elif choice == "no":
        print("\nYou politely decline the potion. The old man shrugs and warns you about dangers ahead.")
        print("You continue down the dark path, but soon find yourself lost in the maze-like forest.")
        lost_in_forest()
    else:
        print("Invalid choice. Please try again.")
        dark_forest()


def village_path():
    print("\nYou follow the sunny trail toward the village. The sound of chatter and laughter fills the air.")
    print("As you approach, you see a town in celebration. A festival is underway!")
    print("A kind villager invites you to join the festivities.")
    
    choice = input("Do you join the festival or explore the outskirts of the village? (festival/outskirts): ").strip().lower()
    
    if choice == "festival":
        print("\nYou join the lively festival, enjoying music, dancing, and delicious food.")
        print("While celebrating, you learn about a hidden treasure in the forest that might explain your mysterious past.")
        treasure_hunt()
    elif choice == "outskirts":
        print("\nYou decide to explore the outskirts of the village, seeking quiet and answers.")
        print("In a secluded meadow, you find ancient ruins and a cryptic inscription hinting at a forgotten legend.")
        ancient_ruins()
    else:
        print("Invalid choice. Please try again.")
        village_path()


def enchanted_path():
    print("\nEmpowered by the potion, you find that the dark forest is not as frightening as it once was.")
    print("You encounter a fork in the path:")
    print("1. One way leads to a shimmering lake with magical properties.")
    print("2. The other leads to an abandoned castle that seems to hide secrets.")
    
    choice = input("Do you choose path 1 or 2? (enter 1 or 2): ").strip()
    
    if choice == "1":
        print("\nAt the lake, you discover that its waters can heal wounds and reveal hidden truths.")
        print("You see your reflection and remember bits of your past, setting you on a journey to reclaim your identity.")
        print("Your adventure continues... (To be continued)")
    elif choice == "2":
        print("\nInside the castle, you uncover a diary detailing a lost royal lineage—you may be the heir to a forgotten kingdom!")
        print("Armed with new purpose, you prepare for a quest to restore the kingdom to its former glory.")
        print("Your adventure continues... (To be continued)")
    else:
        print("Invalid choice. Please try again.")
        enchanted_path()


def lost_in_forest():
    print("\nLost in the dark forest, you wander aimlessly under the canopy of ancient trees.")
    print("Eventually, you stumble upon a hidden clearing with a portal shimmering in the air.")
    
    choice = input("Do you step through the portal or try to find your way out of the forest? (portal/exit): ").strip().lower()
    
    if choice == "portal":
        print("\nYou step through the portal and find yourself in a world unlike any other—a realm of magic and wonder.")
        print("There, you discover that your destiny is intertwined with the fate of multiple worlds.")
        print("Your adventure continues... (To be continued)")
    elif choice == "exit":
        print("\nDetermined, you try to find a way out of the forest. After days of wandering, you finally reach the edge of the forest.")
        print("Freedom at last—but with freedom comes new challenges and mysteries waiting to be solved.")
        print("Your adventure continues... (To be continued)")
    else:
        print("Invalid choice. Please try again.")
        lost_in_forest()


def treasure_hunt():
    print("\nInspired by the festival tales, you decide to embark on a treasure hunt.")
    print("You follow clues that lead you into a deep cave beneath the forest.")
    
    choice = input("Do you light a torch or proceed in the dark? (torch/dark): ").strip().lower()
    
    if choice == "torch":
        print("\nWith the torch, you safely navigate the cave and uncover a chest filled with ancient artifacts.")
        print("Among them is a mysterious map that hints at a great legacy waiting to be discovered.")
        print("Your adventure continues... (To be continued)")
    elif choice == "dark":
        print("\nYou choose to rely on your instincts and proceed in the dark. Suddenly, you slip and fall into a hidden pit.")
        print("In the darkness, you find an old friend who was lost long ago, and together you plan your next move.")
        print("Your adventure continues... (To be continued)")
    else:
        print("Invalid choice. Please try again.")
        treasure_hunt()


def ancient_ruins():
    print("\nExploring the ruins, you decipher an inscription that speaks of an ancient power hidden beneath the earth.")
    print("You feel compelled to uncover the secrets of the past.")
    
    choice = input("Do you search for the hidden power or report your findings to the village elders? (search/report): ").strip().lower()
    
    if choice == "search":
        print("\nDriven by curiosity, you search the ruins and discover a chamber glowing with an eerie light.")
        print("Within it lies a relic that might change the fate of the entire realm.")
        print("Your adventure continues... (To be continued)")
    elif choice == "report":
        print("\nYou decide to report your findings to the village elders. They are astonished and reveal long-held secrets about your past.")
        print("It turns out, you have a special destiny that could reshape the future of the land.")
        print("Your adventure continues... (To be continued)")
    else:
        print("Invalid choice. Please try again.")
        ancient_ruins()


if __name__ == "__main__":
    start_adventure()
