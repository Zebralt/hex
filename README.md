
<h1 align="center">
  hex
</h1>


Simple GUI management for Curses.

Curses allows you :
* to print text at a given position x, y (or rather y, x);
* to capture key events.

With those basic features, we can make out a basic GUI system.

# Features

The Python Curses wrapper does already some abstraction for us, such as for function calls entering and exiting the Curses program and the multiple `addstr` being combined into one.
