# beanOS

beanOS is a Micropython application designed for the Badger2040 device. It tracks and logs your coffee consumption, providing a simple interface to view statistics, reset counts, and change settings.

This code must not be used by fascists! No code for the AfD or Musk or Trump!

## Installation

To install beanOS on your Badger2040:
1. Connect your Badger2040 to your computer.
2. Open Thonny IDE.
3. Copy the `main.py` file content into Thonny's editor.
4. Save the file to your Badger2040 as `main.py`.
5. Copy the file `maintenance_config.json` to your Badger2040 as well. This file is required for maintenance reminders and configuration.

## Usage

### Main screen
![main screen](images/beanOS_screen-6.jpg)
#### Buttons
- **a:**
Increments the espresso count
- **b:**
Increments the cappuccino count
- **c:**
Opens the additional drink menu
- **UP:**
Opens the main menu
- **DOWN:**
Switches to the next day and resets the daily counts

### Drink menu
![drink menu screen](images/beanOS_screen-5.jpg)
#### Buttons
- **a:**
Chooses the selected drink
- **c:**
Closes the menu
- **UP** & **DOWN:**
Navigate the menu

### Main menu
![main menu screen](images/beanOS_screen-4.jpg)
#### Buttons
- **a:**
Chooses the selected optoin
- **c:**
Closes the menu
- **UP** & **DOWN:**
Navigate the menu


#### Menu Options

- **Bohnen**: Opens the additional drink menu (same as Button C)
- **Statistiken anzeigen**: Displays total counts of espresso, cappuccino, and other drinks. Also shows bean consumption (grams per day, days per pack) and average coffee per day.
- **Tagesstatistiken zurücksetzen**: Resets the daily counts for espresso, cappuccino, and other drinks.
- **Datum ändern**: Allows you to change the current date.
- **Wartungshistorie**: View and manually log maintenance tasks. Select a task and press Button A to mark it as completed for today.
- **Information**: Displays version information and credits.

### Bean Packs
You can select the current pack size in the menu. The statistics will show how many days a pack lasts and your average bean consumption per day.

### Maintenance Reminders
beanOS includes an intelligent maintenance reminder system that helps you keep your coffee machine in optimal condition.

#### Features:
- **Automatic Warnings**: The system automatically shows full-screen warnings when maintenance tasks are due
- **Smart Icon**: When you dismiss a warning with Button C, a small "!" icon appears next to the date as a subtle reminder
- **Quick Action**: Press Button A on a maintenance warning to mark the current task as completed
- **Menu Integration**: Use the "Wartungshistorie" menu to manually log maintenance tasks
- **Auto-Reset**: The warning icon automatically disappears when you log a maintenance task through the menu

#### Maintenance Tasks:
- **Cleaning** (every 7 days)
- **Descaling** (every 28 days) 
- **Brew Group Cleaning** (every 42 days OR after 150 drinks)
- **Grinder Cleaning** (every 56 days)
- **Deep Cleaning** (every 365 days)

#### Button Controls for Maintenance:
- **Button A**: Mark the current maintenance task as completed
- **Button C**: Hide the warning and show the small reminder icon instead

## License

This project is licensed under the GNU GPLv3 License. See the LICENSE file for details.

## Author

Joao Neisinger
