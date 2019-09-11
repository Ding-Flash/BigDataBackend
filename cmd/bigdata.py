from colorama import init, Fore, Back, Style
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from tqdm import tqdm
import os

# from prompt_toolkit.lexers import PygmentsLexer
# from pygments.lexers.shell import BashLexer

completer = WordCompleter(['BigRoot', 'SparkTree', 'ASTracer'], ignore_case=True)


class fake():

    def __iter__(self):
        return (i for i in range(10))


def spark(session): 
    while True:
        print(Fore.YELLOW+"You are in SparkTree mode, please input task name:")
        task_name = session.prompt("SparkTree (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in SparkTree mode, please input cmd:")
        cmd = session.prompt("SparkTree (cmd)> ", auto_suggest=AutoSuggestFromHistory())
        print(Fore.BLUE+"Sampling Start".upper())
        os.system(cmd)
        print(Fore.BLUE+"Sampling stop".upper())
        print(Fore.BLUE+"Analysis Start...".upper())
        print(Fore.BLUE+"find 32 stragglers".upper())
        print(Fore.GREEN+"analysis success!".upper())
        print(Style.DIM+"please open your browser to look your report")
        break


def bigroot(session):
    while True:
        print(Fore.YELLOW+"You are in bigroot mode, please input task name:")
        task_name = session.prompt("BigRoot (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in bigroot mode, please input cmd:")
        cmd = session.prompt("BigRoot (cmd)> ", auto_suggest=AutoSuggestFromHistory())
        print(Fore.BLUE+"Sampling Start".upper())
        os.system(cmd)
        print(Fore.BLUE+"Sampling stop".upper())
        print(Fore.BLUE+"Analysis Start...".upper())
        print(Fore.BLUE+"initialize decode engine".upper())
        print(Fore.BLUE+"log analysis finished".upper())
        print(Fore.BLUE+"find 29 stragglers".upper())
        print(Fore.BLUE+"get Resource info".upper())
        print(Fore.GREEN+"analysis success!".upper())
        print(Style.DIM+"please open your browser to look your report")
        break 


def htrace(session):
    while True:
        print(Fore.YELLOW+"You are in ASTracer mode, please input task name:")
        task_name = session.prompt("ASTracer (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in bigroot mode, please input cmd:")
        cmd = session.prompt("ASTracer (cmd)> ", auto_suggest=AutoSuggestFromHistory())
        print(Fore.BLUE+"Sampling Start".upper())
        os.system(cmd)
        print(Fore.BLUE+"Sampling stop".upper())
        print(Fore.BLUE+"Analysis Start...".upper())
        print(Fore.GREEN+"analysis success!".upper())
        print(Style.DIM+"please open your browser to look your report")
        break 


def main():
    init(autoreset=True)
    soft_info = "BigData Analysis Software \nVersion: 1.0\n"
    print(Style.DIM + soft_info)

    introduce = "BigData Analysis Software can be used to analyze big data program performance and visualize the results through the web side.\nThis software has three functions for performance analysis of big data programs, they are:\n"
    
    print(Fore.CYAN + introduce)
    class_ = "1. BigRoot".center(120, " ") + "\n"
    class_ += "An Effective Approach for Root-cause Analysis of Stragglers in Big Data System".center(120, " ")+"\n\n"
    class_ += "2. SparkTree".center(120, " ") + "\n"
    class_ += "Data Mining Based Root-Cause Analysis of Performance Bottleneck for Big Data Workload".center(120, " ")+" \n\n"
    class_ += "3. ASTracer".center(120, " ") + "\n"
    class_ +="A Fine-grained Performance Bottleneck Analysis Method for HDFS".center(120, " ")+"\n"
    print(Fore.GREEN + class_)
    
    tourist = "please type the analysis mode you want e.g: BigRoot, SparkTree, ASTracer; type quit to EXIT"
    print(Style.DIM + tourist)
    session = PromptSession()

    while True:
        text = session.prompt("mode > ",completer=completer, auto_suggest=AutoSuggestFromHistory())
        if text == 'quit':
            break
        if text == 'BigRoot':
            bigroot(session)
        if text == 'SparkTree':
            spark(session)
        if text == 'ASTracer':
            htrace(session)
main()