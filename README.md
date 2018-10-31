
<h1 align="center">
  hex
</h1>


Simple GUI management for Curses.

Curses allows you :
* to print text at a given position x, y (or rather y, x);
* to capture key events.

With those basic features, we can make out a basic GUI system.

# Features

The Python Curses wrapper does already some abstraction for us, such as for 
function calls entering and exiting the Curses program and the multiple `addstr` 
being combined into one.

From functions that allows to refresh the screen and write colored text at a 
specifc location on the screen, how we could design a simple GUI system ?

## Gui Elements

We can use GUI Elements. Everyone is familiar with that. Label, Panel and so on.
Each having their own role.

An element is simply a rect, with coordinates (x, y) and dimensions (width, 
height). As we are in a purely textual context all visible elements will be 
made solely of text.

### Text Elements

The primary class being 'Label'.

### Containers

Panel and so on.

## Layout

`pack`.

### Size calculus

percentage, sum of size of children ...

### Row

### Column

### Grid

### Border

### Complex

### Text Align

## Key Events

The concept of shortcut/keybinding.

### Global Key Events

### Element Focus

### Local (Element-wise) Key Events

## Dialogs

* alert : simply bringing something to the attention of the user.
* prompt (yesno, etc. one character answer)
* ask a question (with a typed answer)

## Styling

### Colors

### Borders

There exists specific unicode characters for the purpose of drawing borders in
a terminal. We can use these.