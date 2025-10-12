from core.data_manager import initialize_storage
from core.auth_manager import AuthManager

def main():
    print("=== Basic Security System ===")
    initialize_storage()
    auth = AuthManager()

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            auth.register_user(username, password)

        elif choice == "2":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if auth.login(username, password):
                print(f"Welcome, {username}!")
                # Placeholder for OS simulation here
                input("Press Enter to logout...")
        elif choice == "3":
            print("Exiting system...")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
