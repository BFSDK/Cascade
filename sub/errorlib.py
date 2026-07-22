import colorama

colorama.init()

def showError(errType, errText, hint, errString, errLine):
    """Shows error

    Args:
        errType (_type_): Error type
        errText (_type_): Error text
        hint (_type_): Error hint
    """

    print(f"""{colorama.Fore.RED}[!] {errType} error
          
{colorama.Fore.RESET} {errLine} | {colorama.Fore.RED}{errString}

{colorama.Fore.RESET}Error: {errText}
{colorama.Fore.CYAN}Hint: {hint}       

""")
    
def showFastError(errType, errText, hint):
    """Shows error

    Args:
        errType (_type_): Error type
        errText (_type_): Error text
        hint (_type_): Error hint
    """

    print(f"""{colorama.Fore.RED}[!] {errType} error

{colorama.Fore.RESET}Error: {errText}
{colorama.Fore.CYAN}Hint: {hint}       

""")