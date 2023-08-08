import curses
import ctypes
import random
from time import sleep
from operator import itemgetter
import unidecode

global translate_signal
translate_signal = {}
translate_signal = {
    '+':'mais',
    '-':'menos',
    'x':'vezes',
    '/':'dividido por'
}

def str_to_function(str):
    str_sem_acentos = unidecode.unidecode(str.lower())

    replacer = {
        ' ': '_',
        '-': '_',
        '/': '_',
        '.': ''
    }

    for char, replace_char in replacer.items():
        str_func = str_sem_acentos.replace(char, replace_char)

    return str_func

def get_nvda():
    nvda_dll = ctypes.CDLL("./nvda.dll")
    speak = nvda_dll.nvdaController_speakText
    nvda_silence = nvda_dll.nvdaController_cancelSpeech
    
    return nvda_silence, speak

def print_menu(stdscr, selected_row_idx, options, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    if message:
        title_x = width//2 - len(message)//2
        title_y = y = height//2 - len(options)//2 - 1
        stdscr.addstr(title_y, title_x, message)

    NVDA_SPEAK(options[selected_row_idx])

    for idx, option in enumerate(options):
        x = width//2 - len(option)//2
        y = height//2 - len(options)//2 + idx + 1
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.insstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)

    stdscr.refresh()

def newMenu(stdscr, options, message = False, nvda_message = False):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row_idx = 0
    if nvda_message:
        NVDA_SPEAK(nvda_message)
    elif message != False and nvda_message == False:
        NVDA_SPEAK(message)
    print_menu(stdscr, current_row_idx, options, message)

    while True:
        key = stdscr.getch()
        stdscr.clear()
        NVDA_SILENCE()
        if key == curses.KEY_UP:
            if current_row_idx > 0:
                current_row_idx -= 1
            else:
                current_row_idx = len(options) - 1
        elif key == curses.KEY_DOWN: 
            if current_row_idx < len(options)-1:
                current_row_idx += 1
            else:
                current_row_idx = 0
        elif key == ord('\n'):
            return options[current_row_idx]
        elif key == ord('q'):
            break
        
        # NVDA_SPEAK(options[current_row_idx])
        print_menu(stdscr, current_row_idx, options, message)

def get_max_window(stdscr):
    height, width = stdscr.getmaxyx()
    win = curses.newwin(height, width, 0, 0)
    win.clear()

    return win

def win_center_message(win, message, time_sleep = 3, y_ajust = 0, nvda_message = False):
    if nvda_message == False:
        nvda_message = message
    win.clear()
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    win.addstr(y, x, message)
    NVDA_SPEAK(nvda_message)
    win.refresh()
    sleep(time_sleep)

def center_message(stdscr, message, y_ajust = 0, nvda_message = False):
    if nvda_message == False:
        nvda_message = message
    height, width = stdscr.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2 - y_ajust
    stdscr.addstr(y, x, message)
    NVDA_SPEAK(nvda_message)
    stdscr.refresh()

def insert_user_input(win, message, only_num = False, nvda_message = False):
    height, width = win.getmaxyx()
    x = width//2 - len(message)//2
    y = height//2
    if nvda_message == False:
        win.addstr(y-1, x, message)
    else:
        win_center_message(win, message, 0.5, nvda_message = nvda_message)
        win.clear()
    curses.curs_set(1)
    win.refresh()
    win.keypad(True)
    curses.echo()
    if only_num == True:
        while True:
            win.clear()
            win.addstr(y-1, x, message)
            win.refresh()
            curses.echo()
            input_str = win.getstr(y, x, 20).decode('utf-8')
            if input_str.isdigit():  # Verifica se a entrada é composta apenas de dígitos
                break
            else:
                curses.beep()
                win_center_message(win, 'Digite apenas números')
    else:
        input_str = win.getstr(y, x, 20).decode('utf-8')
    curses.noecho()
    curses.curs_set(0)

    return input_str

def get_result(n1, n2, symbol):
    if symbol == '+':
        result = n1 + n2
    elif symbol == '-':
        result = n1 - n2
    elif symbol == 'x':
        result = n1 * n2
    elif symbol == '/':
        result = n1 / n2
    
    return result

def generate_list(x1, x2, y1, y2, qtd):
    operations = []

    while True:
        num_1 = random.randint(x1, x2)
        num_2 = random.randint(y1, y2)
        operations.append(f'{num_1} {num_2}')
        if len(operations) == qtd:
            break

    return operations

def n2_lesson(main_win, operations, signal, points, total_points, shuffle = True):
    global translate_signal
    for op in operations:
        main_win.clear()
        numbers = []
        numbers.append(op.split(' ')[0])
        numbers.append(op.split(' ')[1])
        if shuffle == True:
            random.shuffle(numbers)
        nvda_message = f'{numbers[0]} {translate_signal[signal]} {numbers[1]}'
        answer = insert_user_input(main_win, f'{numbers[0]} {signal} {numbers[1]}', nvda_message=nvda_message)
        result = get_result(int(numbers[0]), int(numbers[1]), signal)
        if int(answer) == result:
            win_center_message(main_win, 'Acertou!', 1)
            total_points += points
            operations.remove(op)
        else:
            win_center_message(main_win, 'Errou!', 1)

    return total_points, operations

def lesson(main_win, stdscr, niveis, nivel, operation, shuffle = True):
    operations = generate_list(niveis[nivel][0], niveis[nivel][1], niveis[nivel][2], niveis[nivel][3], 20)
    
    points = 1
    total_points = 0

    while True:
        if total_points < 10 or len(operations) > 0:
            if len(operations) == 0:
                operations = generate_list(niveis[nivel][0], niveis[nivel][1], niveis[nivel][2], niveis[nivel][3], 5)
            if shuffle == True:
                random.shuffle(operations)
            total_points, operations = n2_lesson(main_win, operations, operation, points, total_points, shuffle)
            if points > 0.25:
                points = points - 0.25
        else:
            win_center_message(main_win, 'Parabéns! Você concluiu a lição.')
            break

def adicao(main_win, stdscr, nivel):
    ADICAO = {
        1:[1, 9, 1, 9],
        2:[8, 30, 1, 9],
        3:[10, 50, 10, 49],
        4:[50, 99, 10, 99],
        5:[200, 499, 100, 300],
        6:[100, 999, 100, 499],
        7:[1000, 1500, 100, 999],
        8:[1500, 5000, 1000, 5000]
    }

    lesson(main_win, stdscr, ADICAO, nivel, '+')

def subtracao(main_win, stdscr, nivel):
    SUBTRACAO = {
        1:[4, 9, 1, 4],
        2:[9, 30, 1, 9],
        3:[49, 99, 10, 49],
        4:[100, 199, 10, 99],
        5:[200, 499, 49, 199],
        6:[500, 999, 100, 499],
        7:[1000, 1500, 100, 999],
        8:[3000, 5000, 800, 2500]
    }

    lesson(main_win, stdscr, SUBTRACAO, nivel, '-', False)

def multiplicacao(main_win, stdscr, nivel):
    MULTIPLICACAO = {
        1:[2, 9, 1, 5],
        2:[2, 9, 1, 9],
        3:[11, 99, 2, 5],
        4:[11, 99, 2, 9],
        5:[100, 499, 2, 9],
        6:[499, 1200, 2, 9],
        7:[10, 99, 10, 12],
        8:[10, 99, 12, 40]
    }

    lesson(main_win, stdscr, MULTIPLICACAO, nivel, 'x')

def divisao(main_win, stdscr, nivel):
    DIVISAO = {
        1:[10, 98, 2, 5],
        2:[18, 98, 4, 9],
        3:[100, 200, 2, 5],
        4:[100, 200, 2, 9],
        5:[100, 998, 2, 9],
        6:[998, 3000, 2, 9],
        7:[100, 1000, 10, 30],
        8:[1000, 5000, 10, 30]
    }

    lesson(main_win, stdscr, DIVISAO, nivel, '/', False)



def main(stdscr):
    global players, players_info
    NVDA_SILENCE()
    curses.curs_set(0)
    message = 'Bem-Vindo ao Instrutor de Matemática'
    center_message(stdscr, message)
    NVDA_SPEAK(message)
    sleep(2)
    while True:
        mode_menu = ['Aprender', 'Lições', 'Sair']
        option = newMenu(stdscr, mode_menu, 'Escolha o modo de aprendizado: ')
        if option == 'Aprender':
            mode_menu = ['Adição', 'Subtração', 'Multiplicação', 'Divisão', 'Voltar']
            operacao = newMenu(stdscr, mode_menu, 'Qual operação você deseja aprender?')
            if operacao != 'Voltar': 
                nivel_menu = ['Nivel 1', 'Nivel 2', 'Nivel 3', 'Nivel 4', 'Nivel 5', 'Nivel 6', 'Nivel 7', 'Nivel 8']
                option_select = newMenu(stdscr, nivel_menu, 'Escolha o nível da lição: ')
                nivel = int(option_select.split(' ')[1])
                call_func = globals().get(str_to_function(operacao))
                stdscr.clear()
                main_win = get_max_window(stdscr)
                call_func(main_win, stdscr, nivel)
        elif option == 'Sair':
            break


NVDA_SILENCE, NVDA_SPEAK = get_nvda()
curses.wrapper(main)