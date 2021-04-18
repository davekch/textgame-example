from textgame.parser import Parser, EnterYesNoLoop
from textgame.player import Player, register
from textgame.game import Game
from textgame.world import World
import yaml

import logging
logging.basicConfig(level="INFO", format='%(levelname)-8s %(name)-16s %(funcName)-18s: %(message)s')


class MyPlayer(Player):

    # map this method to the command "wave"
    @register("wave")
    def do_magic(self, noun):
        # what should happen if the user just types "wave"?
        if not noun:
            return "What?"
        # what if the item the user wants to use is not in our inventory?
        if noun not in self.inventory:
            return "You don't have it!"
        if noun == "wand":
            if not self.status.get("magician"):
                self.status["magician"] = True
                return "Wowzers, you are now a magician!"
            # check where the player is waving the wand
            if self.location.id in ["field_1", "hidden_place"]:
                # relocate the player
                if self.location.id == "field_1":
                    self.location = self.world.room("hidden_place")
                else:
                    self.location = self.world.room("field_1")
                # add the room's value to the score
                if not self.location.visited:
                    self.score += self.location.visit()
                # construct a message for display
                msg = "You fly through the air!\n"
                msg += self.look()  # describe the new room
                return msg
            else:
                return "Blue sparks fly through the air! Magic!"
        # what if the user tries to wave something other than a wand?
        else:
            return "I don't know how to wave a {}".format(noun)

    @register("trade")
    def trade(self, noun):
        if not noun:
            return "Trade what?"
        if noun not in self.inventory:
            return f"You don't have a {noun}"
        # check if (or which) the dealer is present
        if "dealer" in self.location.monsters:
            # check if the bow is still available
            if not "bow" in self.world.storage_room.items:
                return "Apparently the dealer ran out of bows!"
            # get the bow from the storage room
            bow = self.world.storage_room.get_item("bow")
            # compare values
            if self.inventory[noun].value >= bow.value:
                # move the actual trade inside a helper function
                def trade_bow():
                    # remove noun-item from player's inventory
                    thing = self.inventory.pop(noun)
                    # put it inside the storage room (optional)
                    self.world.storage_room.add_item(thing)
                    # add bow to inventory and remove it from storage room
                    self.inventory["bow"] = self.world.storage_room.pop_item("bow")
                    return f"You traded your {noun} for a wooden bow."

                return EnterYesNoLoop(
                    question=f"Do you want to trade your {noun} for a wooden bow?",
                    yes=trade_bow,
                    no=f"Ok, keep your {noun} then."
                )
            else:
                return f"Your {noun} is not valuable enough!"
        else:
            return f"There is no one to trade your {noun} with."


class MyWorld(World):

    def update(self, player):
        msg = World.update(self, player)
        if self.time == 42:
            grail = self.storage_room.get_item("grail")
            player.location.add_item(grail)
            msg += "\nA golden grail appears out of nowhere!"

        return msg


world = MyWorld()
world.load_resources("resources", loader=yaml.safe_load)
# create a player and place it in the first room
player = MyPlayer(world, world.room("field_0"))
parser = Parser()
# define some synonyms
parser.update_verb_synonyms({
    "wave": ["swing", "shake"]
})
# link player methods to commands
parser.set_actionmap(player.get_registered_methods())
# put everything together
game = Game(player, parser)


if __name__ == "__main__":
    while not game.over():
        command = input("→ ")
        reply = game.play(command)
        print(reply)
