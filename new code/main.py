import argparse
from auth_manager import bootstrap_admin

def run_gui():
    from gui.app import App
    app = App()
    app.mainloop()

def run_cli():
    print("CLI mode not implemented yet. Use the GUI or add CLI menus.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()


    bootstrap_admin()

    if args.cli:
        run_cli()
    else:
        run_gui()

if __name__ == "__main__":
    main()
