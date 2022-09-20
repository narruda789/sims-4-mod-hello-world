import sims4.commands


# A cheat code to say, "Hello, world!"

# This tag says to register a command called 'hellow' that:
#  - can be executed from the cheat console (Ctrl + Shift + C)
#  - can be run from Live mode without testingcheats set
#  - executes the function
@sims4.commands.Command("hellow",
                        command_type=sims4.commands.CommandType.Live)
def say_hello(_connection=None):
    # get the function for printing output
    output = sims4.commands.CheatOutput(_connection)

    # ...and call it!
    output("Hello, world!")
