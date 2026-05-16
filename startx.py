import os
import sys
import asyncio
import importlib.util
from colorama import init
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.tree import Tree
from rich.live import Live
import rich.box
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PTStyle

import apis

# Инициализация
init(autoreset=True)
console = Console()

# Новый логотип
BIG_X = [
    r"████████╗          ████████╗",
    r"╚████████╗        ████████╔╝",
    r" ╚████████╗      ████████╔╝ ",
    r"  ╚████████╗    ████████╔╝  ",
    r"   ╚████████╗  ████████╔╝   ",
    r"    ╚████████████████╔╝     ",
    r"     ╚██████████████╔╝      ",
    r"     ████████████████╗      ",
    r"    ████████╔█████████╗     ",
    r"   ████████╔╝ ╚████████╗    ",
    r"  ████████╔╝   ╚████████╗   ",
    r" ████████╔╝     ╚████████╗  ",
    r"████████╔╝       ╚████████╗ ",
    r"╚═══════╝         ╚═══════╝ "
]

DESCRIPTION = "Advanced OSINT Architecture"
PLUGINS_DIR = "plugins"

# --- СИСТЕМА ПЛАГИНОВ ---
loaded_plugins = {}

def load_plugins():
    if not os.path.exists(PLUGINS_DIR):
        os.makedirs(PLUGINS_DIR)
    
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            name = filename[:-3]
            filepath = os.path.join(PLUGINS_DIR, filename)
            spec = importlib.util.spec_from_file_location(name, filepath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            if hasattr(mod, "PLUGIN_NAME") and hasattr(mod, "run"):
                loaded_plugins[name] = mod

# --- АНИМАЦИИ И ИНТЕРФЕЙС ---
async def intro_animation():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print("\n")
    
    # Анимация появления лого
    for line in BIG_X:
        console.print(Align.center(f"[bold red]{line}[/bold red]"))
        await asyncio.sleep(0.08)
    
    await asyncio.sleep(0.3)
    # Появление названия
    console.print(Align.center("\n[bold white]X - F R A M E W O R K[/bold white]"))
    await asyncio.sleep(0.3)
    console.print(Align.center(f"[dim red]{DESCRIPTION}[/dim red]\n"))
    await asyncio.sleep(0.8)

def draw_static_header():
    os.system('clear' if os.name == 'posix' else 'cls')
    for line in BIG_X:
        console.print(Align.center(f"[bold red]{line}[/bold red]"))
    console.print(Align.center("\n[bold white]X - F R A M E W O R K[/bold white]"))
    console.print(Align.center(f"[dim red]{DESCRIPTION}[/dim red]\n"))

# Красивый древовидный вывод результатов
def build_result_tree(data, tree=None, name="Result"):
    if tree is None:
        tree = Tree(f"[bold red]❖ {name} ❖[/bold red]", guide_style="bold red")
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                subtree = tree.add(f"[bold white]{k}[/bold white]")
                build_result_tree(v, subtree, k)
            else:
                tree.add(f"[bold white]{k}:[/bold white] [green]{v}[/green]")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                subtree = tree.add("[bold white]>[/bold white]")
                build_result_tree(item, subtree, "Item")
            else:
                tree.add(f"[green]{item}[/green]")
    else:
        tree.add(f"[green]{data}[/green]")
    return tree

async def run_module(coro, target):
    title = f" Выполнение: {target} "
    console.print(Align.center(Text(title, style="bold red")))
    
    with console.status("[bold red]Анализ данных...[/bold red]", spinner="bouncingBar"):
        results = await coro
        
    for mod, data in results.items():
        is_error = "error" in str(data).lower()
        color = "red" if is_error else "green"
        
        # Используем древовидный видер
        tree = build_result_tree(data, name=mod)
        
        panel = Panel(
            tree,
            title=f"[{color}]{mod}[/{color}]",
            border_style="red",
            expand=False
        )
        console.print(Align.center(panel))
        console.print()

def create_module_panel(title, items):
    """Создает отдельный красивый блок для модуля"""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("ID", style="bold red", justify="right")
    table.add_column("Desc", style="white")
    
    for uid, desc in items:
        table.add_row(f"[{uid}]", desc)
        
    return Panel(table, title=f"[bold white]{title}[/bold white]", border_style="red", expand=False)

async def menu():
    load_plugins()
    await intro_animation()
    
    # Настройка автозаполнения
    plugin_mapping = {}
    idx = 1
    for p_name, p_mod in loaded_plugins.items():
        plugin_mapping[f"3.{idx}"] = p_mod
        idx += 1

    base_commands = [
        '1.1', '1.2', '1.3', '1.4', '1.5', '1.6',
        '2.1', '2.2', '2.3', '2.4',
        '0', 'exit'
    ] + list(plugin_mapping.keys())
    
    completer = WordCompleter(base_commands, ignore_case=True)
    
    style = PTStyle.from_dict({
        'prompt': 'ansired bold',
        'input': 'ansiwhite'
    })
    session = PromptSession(style=style)

    while True:
        draw_static_header()
        
        # --- Блок 1: Recon ---
        recon_items = [
            ("1.1", "IP & Infrastructure Search"),
            ("1.2", "Domain & Email Search"),
            ("1.3", "Phone & Identity Search"),
            ("1.4", "Username Global Scan (Deep Dive)"),
            ("1.5", "IP Geolocation (Free)"),
            ("1.6", "Subdomain Scanner (Free)")
        ]
        console.print(Align.center(create_module_panel("Module 1: Recon", recon_items)))
        
        # --- Блок 2: Tools ---
        tools_items = [
            ("2.1", "Google Dorks Generator"),
            ("2.2", "Generate Fake Identity"),
            ("2.3", "Password Generator"),
            ("2.4", "Base64 Encoder / Decoder")
        ]
        console.print(Align.center(create_module_panel("Module 2: Tools", tools_items)))

        # --- Блок 3: Plugins ---
        plugin_items = []
        if not plugin_mapping:
            plugin_items.append(("-", "[dim]No plugins loaded[/dim]"))
        for k, v in plugin_mapping.items():
            plugin_items.append((k, f"{v.PLUGIN_NAME} (Plugin)"))
            
        console.print(Align.center(create_module_panel("Module 3: Plugins", plugin_items)))
        
        # --- Блок Выхода ---
        console.print()
        exit_panel = Panel("[0] Exit Framework", style="bold red", expand=False, border_style="red")
        console.print(Align.center(exit_panel))
        console.print()

        try:
            choice = await session.prompt_async("➤ X-Terminal > ", completer=completer)
            choice = choice.strip()
        except (EOFError, KeyboardInterrupt):
            break

        # --- Обработка команд Recon ---
        if choice == '1.1':
            target = await session.prompt_async("❖ Введите IP: ")
            await run_module(apis.scan_ip(target), f"IP: {target}")
        elif choice == '1.2':
            target = await session.prompt_async("❖ Введите Домен: ")
            await run_module(apis.scan_domain(target), f"Domain: {target}")
        elif choice == '1.3':
            target = await session.prompt_async("❖ Введите Номер: ")
            await run_module(apis.scan_phone(target), f"Phone: {target}")
        elif choice == '1.4':
            target = await session.prompt_async("❖ Введите Username: ")
            await run_module(apis.scan_username_deep(target), f"User Deep Dive: {target}")
        elif choice == '1.5':
            target = await session.prompt_async("❖ Введите IP: ")
            await run_module(apis.scan_ip_geo_free(target), f"Free IP Geo: {target}")
        elif choice == '1.6':
            target = await session.prompt_async("❖ Введите Домен: ")
            await run_module(apis.scan_subdomains_free(target), f"Free Subdomains: {target}")
            
        # --- Обработка команд Tools ---
        elif choice == '2.1':
            target = await session.prompt_async("❖ Введите Домен для Dorks: ")
            await run_module(apis.google_dorks_scan(target), f"Dorks: {target}")
        elif choice == '2.2':
            target = await session.prompt_async("❖ Введите локаль [Enter=ru_RU]: ") or 'ru_RU'
            await run_module(apis.get_fake_identity_async(target), f"Identity [{target}]")
        elif choice == '2.3':
            try:
                length_input = await session.prompt_async("❖ Длина пароля (6-32): ")
                length = int(length_input)
                pwd = apis.generate_password(length)
                console.print(Align.center(f"\n[bold green]✔ Сгенерированный пароль:[/bold green] [white]{pwd}[/white]"))
            except ValueError:
                console.print(Align.center("\n[bold red]✖ Ошибка: Введите число![/bold red]"))
        elif choice == '2.4':
            action = await session.prompt_async("❖ [1] Encode | [2] Decode : ")
            text = await session.prompt_async("❖ Введите текст: ")
            if action == '1':
                await run_module(apis.b64_encode(text), "Base64 Encode")
            elif action == '2':
                await run_module(apis.b64_decode(text), "Base64 Decode")
                
        # --- Обработка плагинов ---
        elif choice in plugin_mapping:
            target = await session.prompt_async(f"❖ Введите цель для {plugin_mapping[choice].PLUGIN_NAME}: ")
            await run_module(plugin_mapping[choice].run(target), f"Plugin: {plugin_mapping[choice].PLUGIN_NAME}")
            
        # --- Выход ---
        elif choice in ['0', 'Exit', 'exit']:
            os.system('clear' if os.name == 'posix' else 'cls')
            console.print(Align.center("\n[bold red]Завершение работы X-Framework... Удачи![/bold red]\n"))
            break

        # Пауза перед возвратом в меню
        if choice not in ['0', 'Exit', 'exit'] and choice in base_commands:
            await session.prompt_async("\n[ Enter для возврата в меню ]")

if __name__ == "__main__":
    try:
        asyncio.run(menu())
    except KeyboardInterrupt:
        console.print("\n[bold red]Прервано пользователем. Выход...[/bold red]")

