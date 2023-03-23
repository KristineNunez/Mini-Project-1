import smartpy as sp

class Lottery(sp.Contract):
    #Modified: Operator can be specified
    def __init__(self, op):
        self.init(
            players = sp.map(l={}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost = sp.tez(1),
            tickets_available = sp.nat(5),
            max_tickets = sp.nat(5),
            operator = op,
        )

    #Added: Allows operator to change ticket cost when no game is on
    @sp.entry_point
    def change_ticket_cost(self, new_ticket_cost):
        sp.set_type(new_ticket_cost, sp.TMutez)
        
        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "CANNOT CHANGE TICKET COST DURING ONGOING GAME")

        #Change ticket cost
        self.data.ticket_cost = new_ticket_cost

    #Added: Allows operator to change maximum number of available tickets when no game is on
    @sp.entry_point
    def change_max_tickets(self, new_max_tickets):
        sp.set_type(new_max_tickets, sp.TNat)
        
        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "CANNOT CHANGE MAX TICKETS DURING ONGOING GAME")

        #Change maximum number of available tickets
        self.data.max_tickets = new_max_tickets
        self.data.tickets_available = new_max_tickets

    #Modified: Allows players to buy nultiple tickets
    @sp.entry_point
    def buy_ticket(self, num_tickets):
        sp.set_type(num_tickets, sp.TNat)
        
        # Sanity checks
        sp.verify(self.data.tickets_available > 0, "NO TICKETS AVAILABLE")

        # If requested tickets exceeds remaining tickets, just give remaining tickets
        actual_tickets = sp.local("actual_tickets", sp.min(num_tickets, self.data.tickets_available))
        sp.verify(sp.amount >= sp.mul(actual_tickets.value, self.data.ticket_cost), "INVALID AMOUNT")
        
        # Storage updates
        sp.for i in sp.range(0, actual_tickets.value, 1):
            self.data.players[sp.len(self.data.players)] = sp.sender
            self.data.tickets_available = sp.as_nat(self.data.tickets_available - 1)

        # Return extra tez balance to the sender
        extra_balance = sp.amount - sp.mul(actual_tickets.value, self.data.ticket_cost)
        sp.if extra_balance > sp.mutez(0):
            sp.send(sp.sender, extra_balance)

    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == 0, "GAME IS YET TO END")

        # Pick a winner
        winner_id = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_id]

        # Send the reward to the winner
        sp.send(winner_address, sp.balance)

        # Reset the game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")

@sp.add_test(name = "main")
def test():
    scenario = sp.test_scenario()

    # Test accounts
    admin = sp.address("tz1cftYcJt2rQydsbCDCP19zTpqeztLauFBM") #sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")
    john = sp.test_account("john")

    # Contract instance
    lottery = Lottery(admin)
    scenario += lottery

    # buy_ticket
    scenario.h2("buy_ticket (valid test)")
    scenario += lottery.buy_ticket(6).run(amount = sp.tez(6), sender = alice)

    '''
    scenario += lottery.buy_ticket().run(amount = sp.tez(1), sender = alice)
    scenario += lottery.buy_ticket().run(amount = sp.tez(2), sender = bob)
    scenario += lottery.buy_ticket().run(amount = sp.tez(3), sender = john)
    scenario += lottery.buy_ticket().run(amount = sp.tez(1), sender = charles)
    scenario += lottery.buy_ticket().run(amount = sp.tez(1), sender = mike)

    scenario.h2("buy_ticket (failure test)")
    scenario += lottery.buy_ticket().run(amount = sp.tez(1), sender = alice, valid = False)
    '''
    
    #Invalid tests: Changing ticket cost and max tickets during ongoing game
    scenario.h2("change_ticket_cost (invalid test)")
    lottery.change_ticket_cost(sp.tez(2)).run(sender = admin, valid = False)
    
    scenario.h2("change_max_tickets (invalid test)")
    lottery.change_max_tickets(1).run(sender = admin, valid = False)
    
    # end_game
    scenario.h2("end_game (valid test)")
    scenario += lottery.end_game(21).run(sender = admin)

    #Valid tests: Changing ticket cost and max tickets
    scenario.h2("change_ticket_cost (valid test)")
    lottery.change_ticket_cost(sp.tez(2)).run(sender = admin)
    
    scenario.h2("change_max_tickets (valid test)")
    lottery.change_max_tickets(1).run(sender = admin)

    #Invalid tests: Non-operator user tries changing ticket cost and max tickets
    scenario.h2("change_ticket_cost (invalid test)")
    lottery.change_ticket_cost(sp.tez(3)).run(sender = alice, valid = False)
    
    scenario.h2("change_max_tickets (invalid test)")
    lottery.change_max_tickets(2).run(sender = alice, valid = False)
