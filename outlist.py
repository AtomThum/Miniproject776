from people import People

# Lists of people that are already out. Will not be updated when left elevator
class Outlist:
    def __init__(self, outlist: list = []):
        self.outlist = outlist

    # For adding people into outlist.
    def addOutlist(self, *args: People):
        for i in args:
            self.outlist.append(i)