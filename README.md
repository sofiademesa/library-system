**Stacked Knowledge: A Library System** is a library management system with both a console and GUI interface, built with Python and MySQL.

**Project Structure:** The project contains two files: library.py which is the core backend handling all logic, database operations, OOP principles, parallel programming, and console menus, and library_gui.py which is the GUI frontend built with tkinter.

**Important Note:** The core logic and comprehensive implementation of OOP principles, event-driven programming, parallel programming, memory management, and more are all in **library.py**. Similarly, all database interactions and queries are also handled in library.py. Please refer to those files when grading both the technical and database portions of the project.

**library_gui.py** is simply a graphical demonstration of the program in action. It serves as a visual frontend that calls the backend logic from library.py, and is not the primary file for grading purposes.

Requirements: Install the mysql-connector-python dependency by running **"pip install mysql-connector-python"** in your terminal. Then open the XAMPP Control Panel and click Admin next to MySQL. Next, run either "library.py" for the console version or "library_gui.py" for the GUI version. The database library_db and all its tables are automatically created on first run — no manual database setup is needed.

**Default Credentials:** The default admin account has the username** "admin" **and password** "123"**. Regular users can register their own accounts directly from the login screen.
