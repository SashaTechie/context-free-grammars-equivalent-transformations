import ContextFreeGrammar as cfg
import Example as ie
#Formatting
from colorama import Fore, Style

def print_blue_text(text):
    print(Fore.BLUE +
          "\n" +
          text +
          Style.RESET_ALL)

my_grammar = ie.example_table()

print_blue_text("Your grammar")
print(cfg.format_table(my_grammar))

print_blue_text("Dividing elements")
my_grammar = cfg.put_states_in_array(my_grammar)
print(cfg.format_table(my_grammar))

print_blue_text("Delete unused elements")
my_grammar = cfg.delete_unavailable_useless_terminals(my_grammar)
print(cfg.format_table(cfg.table_without_arrays(my_grammar)))

print_blue_text("Resolve epsilons")
my_grammar = cfg.resolve_epsilon_rules(my_grammar)
print(cfg.format_table(cfg.table_without_arrays(my_grammar)))

print_blue_text("Resolve chains")
my_grammar = cfg.resolve_chained_rules(my_grammar)
print(cfg.format_table(my_grammar))

print_blue_text("Resolve left factoring")
my_grammar = cfg.resolve_left_factoring_rules(my_grammar)
print(cfg.format_table(my_grammar))

print_blue_text("Resolve left recursion")
my_grammar = cfg.resolve_direct_left_recursion(my_grammar)
print(cfg.format_table(my_grammar))
