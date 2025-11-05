<div align="center">

# ☕ beanOS

**The Ultimate Coffee Tracking System for Badger2040**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Badger2040-green.svg)](https://shop.pimoroni.com/products/badger-2040)
[![MicroPython](https://img.shields.io/badge/MicroPython-1.19+-orange.svg)](https://micropython.org/)
[![Version](https://img.shields.io/badge/Version-2.3.1-red.svg)](https://github.com/neisinger/beanOS)

*Track your coffee journey with style on your e-ink display*

![Main Screen](images/beanOS_screen-6.jpg)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Achievements](#-achievement-system) • [Maintenance](#-maintenance-system)

</div>

---

## 📖 About

**beanOS** is a feature-rich MicroPython application designed specifically for the **Badger2040** e-ink display device. Transform your coffee routine into an engaging experience with comprehensive tracking, gamification, and maintenance reminders.

Whether you're a casual coffee drinker or a dedicated espresso enthusiast, beanOS helps you:
- 📊 Track every cup with detailed statistics
- 🏆 Unlock achievements and build streaks
- 🔧 Maintain your coffee machine properly
- 📈 Analyze your consumption patterns

### 🚫 Anti-Fascist Declaration
This code must not be used by fascists! No code for the AfD or Musk or Trump!

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### ☕ Coffee Tracking
- **8 Drink Types**: Espresso, Cappuccino, Lungo, Iced Latte, Affogato, Shakerato, Espresso Tonic, and more
- **Smart Statistics**: Daily, weekly, and lifetime tracking
- **Bean Analytics**: Consumption per day, days per pack
- **Auto Logging**: All data saved to CSV format
- **Customizable Packs**: Multiple bean pack sizes (125g-1000g)

</td>
<td width="33%" valign="top">

### 🏆 Achievement System
- **20+ Achievements** across 5 categories
- **Milestone Rewards**: 1, 10, 50, 100, 500, 1000 coffees
- **Streak Tracking**: 7-day and 30-day consistency
- **Special Drinks**: Unlock by trying new beverages
- **Maintenance Master**: Rewards for machine care
- **Progress Bars**: Visual feedback on goals
- **Daily Star**: Title bar indicator (★) for unlocks
- **Full-Screen Celebrations**: Animated notifications

</td>
<td width="33%" valign="top">

### 🔧 Smart Maintenance
- **5 Maintenance Types**: Cleaning, descaling, brew group, grinder, deep clean
- **Dual Triggers**: Time-based AND usage-based
- **Visual Warnings**: Full-screen alerts when due
- **Quick Action**: One-button task completion
- **Smart Reminders**: Persistent icon (!<) until resolved
- **Complete History**: Track all maintenance activities
- **Auto-Reset**: Warnings clear after completion

</td>
</tr>
</table>

---

## 📦 What's in the Box?

### Hardware Requirements
- **Badger2040** e-ink display device by Pimoroni
- USB cable for connection and power
- Computer with Thonny IDE (or similar MicroPython development environment)

### Software Requirements
- **MicroPython** firmware (version 1.19 or higher)
- **Thonny IDE** (recommended) or any MicroPython-compatible editor

---

## 🚀 Installation

### Quick Start (5 minutes)

<details>
<summary><b>Step 1: Prepare Your Badger2040</b></summary>

1. Ensure your Badger2040 has MicroPython firmware installed
2. Connect it to your computer via USB cable
3. The device should appear as a storage device

</details>

<details>
<summary><b>Step 2: Install Thonny IDE</b></summary>

1. Download Thonny from [thonny.org](https://thonny.org/)
2. Install and launch the application
3. Go to **Tools** → **Options** → **Interpreter**
4. Select "MicroPython (Raspberry Pi Pico)" as the interpreter
5. Choose the correct COM port for your Badger2040

</details>

<details>
<summary><b>Step 3: Copy Files to Badger2040</b></summary>

1. Download or clone this repository
2. Open `main.py` in Thonny IDE
3. Click **File** → **Save As**
4. Select **Raspberry Pi Pico** (your Badger2040)
5. Save the file as `main.py`
6. Repeat the process for `maintenance_config.json`

**Required Files:**
- ✅ `main.py` - Main application code
- ✅ `maintenance_config.json` - Maintenance configuration

**Optional Files (created automatically):**
- `kaffee_log.csv` - Coffee consumption log
- `current_date.txt` - Current date tracking
- `current_counts.txt` - Daily counters
- `achievements.json` - Achievement progress
- `maintenance_status.json` - Maintenance history

</details>

<details>
<summary><b>Step 4: First Run</b></summary>

1. Disconnect and reconnect your Badger2040 (or press the reset button)
2. The beanOS interface should appear on the e-ink screen
3. Start tracking your coffee! ☕

</details>

### Alternative Installation Methods

#### Using `mpremote`
```bash
mpremote cp main.py :main.py
mpremote cp maintenance_config.json :maintenance_config.json
```

#### Using `ampy`
```bash
ampy --port /dev/ttyACM0 put main.py
ampy --port /dev/ttyACM0 put maintenance_config.json
```

---

## 🎮 Usage

### 🏠 Main Screen Interface

![Main Screen](images/beanOS_screen-6.jpg)

The main screen is your coffee tracking hub. It displays:
- 📅 Current date with achievement indicator (★)
- ☕ Daily espresso count
- 🥛 Daily cappuccino count  
- 🌟 Daily other drinks count
- ⚠️ Maintenance reminder icon (!) when tasks are due

#### Button Controls

| Button | Action |
|--------|--------|
| **A** | Increment espresso count (+1 ☕) |
| **B** | Increment cappuccino count (+1 🥛) |
| **C** | Open drink menu for other beverages |
| **UP ⬆** | Open main menu |
| **DOWN ⬇** | Advance to next day (resets daily counts) |

---

### 🍵 Drink Menu

![Drink Menu](images/beanOS_screen-5.jpg)

Access 6 additional specialty drinks beyond espresso and cappuccino:

**Available Drinks:**
1. 🥃 **Lungo** - Extended espresso shot
2. 🧊 **Iced Latte** - Cold coffee perfection
3. 🍨 **Affogato** - Espresso meets ice cream
4. 🥤 **Shakerato** - Shaken iced espresso
5. 🍋 **Espresso Tonic** - Refreshing coffee soda
6. ❓ **Other** - Custom creations

#### Button Controls

| Button | Action |
|--------|--------|
| **A** | Select highlighted drink |
| **C** | Close menu (return to main screen) |
| **UP ⬆ / DOWN ⬇** | Navigate drink options |

---

### 📋 Main Menu

![Main Menu](images/beanOS_screen-4.jpg)

Access all beanOS features from the main menu:

#### Menu Options

| Option | Description |
|--------|-------------|
| **🌰 Bohnen** | Quick access to drink menu (same as Button C) |
| **📊 Statistiken anzeigen** | View comprehensive statistics and analytics |
| **🔄 Tagesstatistiken zurücksetzen** | Reset today's drink counters to zero |
| **📅 Datum ändern** | Manually adjust the current date |
| **🔧 Wartungshistorie** | View and log maintenance tasks |
| **🏆 Achievements** | Browse unlocked achievements and progress |
| **ℹ️ Information** | Version info and credits |

#### Button Controls

| Button | Action |
|--------|--------|
| **A** | Select highlighted menu option |
| **C** | Close menu (return to main screen) |
| **UP ⬆ / DOWN ⬇** | Navigate menu options |

---

### 📊 Statistics View

Access detailed analytics about your coffee consumption:

**Total Counters:**
- Total espresso consumed
- Total cappuccino consumed
- Total other drinks consumed
- **Grand Total** of all beverages

**Bean Analytics:**
- Average beans per day (in grams)
- Days remaining in current pack
- Average coffees per day
- Pack size selection (125g-1000g)

**Usage Patterns:**
- Daily trends
- Weekly consumption
- Popular drink types

*Tip: Press Button C to toggle between different statistics pages*

---

### 🏆 Achievement System

Gamify your coffee journey with **20+ unique achievements** across 5 categories!

#### 🏅 Achievement Categories

<details open>
<summary><b>Meilensteine (Milestones)</b> - Coffee consumption milestones</summary>

Unlock these as you build your coffee portfolio:

| Achievement | Icon | Requirement | Description |
|-------------|------|-------------|-------------|
| **Erster Kaffee** | [1] | 1 coffee | Your very first coffee! |
| **Kaffee-Starter** | [10] | 10 coffees | Getting into the habit |
| **Kaffee-Fan** | [50] | 50 coffees | You're a fan now! |
| **Kaffee-Liebhaber** | [100] | 100 coffees | True coffee lover |
| **Kaffee-Experte** | [500] | 500 coffees | Coffee expert level |
| **Kaffee-Meister** | [1K] | 1000 coffees | Coffee master achieved! |

</details>

<details>
<summary><b>⚡ Streaks</b> - Consistency achievements</summary>

Build your daily coffee routine:

| Achievement | Icon | Requirement | Progress |
|-------------|------|-------------|----------|
| **Wochenentkämpfer** | [7d] | 7 consecutive days | Visual progress bar |
| **Monatsmarathon** | [30d] | 30 consecutive days | Visual progress bar |

*Progress bars show your current streak for incomplete achievements*

</details>

<details>
<summary><b>🍹 Spezialgetränke (Special Drinks)</b> - Variety achievements</summary>

Explore different coffee experiences:

| Achievement | Icon | Requirement | Description |
|-------------|------|-------------|-------------|
| **Stay Cool** | [IC] | First iced latte | Refreshing choice! |
| **Dessert** | [AF] | First affogato | Sweet indulgence |
| **Shake it!** | [SH] | First shakerato | Perfectly chilled |

</details>

<details>
<summary><b>🔧 Wartung (Maintenance)</b> - Machine care achievements</summary>

Keep your equipment in top shape:

| Achievement | Icon | Requirement | Description |
|-------------|------|-------------|-------------|
| **Saubere Maschine** | [CL] | First maintenance | Starting good habits |
| **Wartungsmeister** | [WM] | All tasks on time | Maintenance master! |

</details>

<details>
<summary><b>🧪 Experimentell (Experimental)</b> - Special achievements</summary>

Master the art of coffee:

| Achievement | Icon | Requirement | Description |
|-------------|------|-------------|-------------|
| **Barista** | [BA] | Try all drink types | You've tried everything! |
| **Happy Bean Day** | [HB] | 10 coffees in one day | Caffeine champion! |

</details>

#### 🎉 Achievement Features

- **Full-Screen Celebrations**: Animated notifications when you unlock achievements
- **Daily Indicator**: Star (★) appears in the title bar on days you unlock achievements
- **Progress Tracking**: Visual progress bars for streak achievements
- **Category Organization**: Achievements grouped by type for easy browsing
- **Persistent Storage**: All achievements saved to `achievements.json`

---

### 🔧 Maintenance System

Keep your coffee machine in optimal condition with beanOS's intelligent maintenance reminder system.

#### 📋 Maintenance Tasks

beanOS tracks 5 essential maintenance tasks:

| Task | Interval | Trigger Type | Description |
|------|----------|--------------|-------------|
| **☕ Cleaning** | 7 days | Time-based | Regular machine cleaning |
| **💧 Descaling** | 28 days | Time-based | Remove mineral buildup |
| **🔩 Brew Group Cleaning** | 42 days OR 150 drinks | Time + Usage | Deep component cleaning |
| **⚙️ Grinder Cleaning** | 56 days | Time-based | Keep grinder fresh |
| **🧹 Deep Cleaning** | 365 days | Time-based | Annual thorough cleaning |

#### 🎯 How It Works

1. **Automatic Monitoring**: beanOS tracks time elapsed and drinks consumed for each task
2. **Smart Alerts**: Full-screen warnings appear when maintenance is due
3. **Quick Action**: Press **Button A** on a warning to mark the task as complete
4. **Persistent Reminders**: Warning icon (!) appears next to the date if you dismiss the alert
5. **Manual Logging**: Access "Wartungshistorie" menu to manually log maintenance

#### 🖥️ Maintenance Interface

**Warning Screen Features:**
- Clear task name and description
- Time since last maintenance
- Drink count (for usage-based tasks)
- Quick completion with Button A
- Dismissal option with Button C

**Maintenance History Menu:**
- View all maintenance tasks
- See last completion date for each
- Manually log any task
- Track maintenance patterns

#### ⚡ Quick Tips

- ✅ Dismiss warnings with **Button C** to see a subtle reminder icon
- ✅ Complete tasks directly from warnings with **Button A**
- ✅ Use the menu for manual logging if you complete tasks offline
- ✅ Icon automatically disappears when you log the task

---

### 📦 Bean Pack Management

Track your bean consumption and optimize ordering:

**Supported Pack Sizes:**
- 125g (small packs)
- 200g (travel size)
- 250g (standard small)
- 500g (medium)
- 750g (large)
- 1000g (bulk/commercial)

**Analytics Provided:**
- Grams of beans used per day
- Days remaining in current pack
- Average consumption rate
- Predicted reorder date

*Tip: Select your pack size in the statistics menu for accurate tracking*

---

## 📸 Screenshots Gallery

<div align="center">

### Main Interface
<img src="images/beanOS_screen-6.jpg" width="45%" alt="Main Screen"> <img src="images/beanOS_screen-5.jpg" width="45%" alt="Drink Menu">

*Left: Main tracking screen | Right: Specialty drink menu*

### Menus & Features
<img src="images/beanOS_screen-4.jpg" width="45%" alt="Main Menu"> <img src="images/beanOS_screen-3.jpg" width="45%" alt="Statistics">

*Left: Main menu | Right: Statistics view*

### Additional Screens
<img src="images/beanOS_screen-2.jpg" width="45%" alt="Screen 2"> <img src="images/beanOS_screen-1.jpg" width="45%" alt="Screen 1">

*Various interface screens showing different features*

</div>

---

## 🗂️ Data Management

### File Structure

beanOS creates and maintains several files on your Badger2040:

```
/ (root)
├── main.py                    # Main application (REQUIRED)
├── maintenance_config.json    # Maintenance settings (REQUIRED)
├── kaffee_log.csv            # Coffee consumption log
├── current_date.txt          # Current date tracker
├── current_counts.txt        # Daily drink counters
├── achievements.json         # Achievement progress
└── maintenance_status.json   # Maintenance history
```

### CSV Data Format

The `kaffee_log.csv` file logs all your coffee data:

```csv
Date,Espresso,Cappuccino,Lungo,Iced Latte,Affogato,Shakerato,Espresso Tonic,Other
2024-01-15,3,2,0,1,0,0,0,0
2024-01-16,2,1,1,0,0,0,0,0
```

**Features:**
- Automatic logging on each drink
- Compatible with Excel, Google Sheets, Python pandas
- Perfect for external analysis and visualization
- Append-only format preserves history

### Data Export

You can export your data by:
1. Connecting Badger2040 to your computer
2. Copying `kaffee_log.csv` to your desktop
3. Opening in spreadsheet software or data analysis tools

---

## ⚙️ Configuration

### Maintenance Configuration

Edit `maintenance_config.json` to customize maintenance schedules:

```json
{
  "tasks": [
    {
      "name": "Cleaning",
      "interval_days": 7,
      "usage_trigger": null
    },
    {
      "name": "Brew Group Cleaning",
      "interval_days": 42,
      "usage_trigger": 150
    }
  ]
}
```

**Parameters:**
- `name`: Task display name
- `interval_days`: Days between required maintenance
- `usage_trigger`: Optional drink count trigger (null if not used)

---

## 🎯 Tips & Tricks

### Maximize Your beanOS Experience

#### 🏆 Achievement Hunting
- **Consistency is key**: Coffee every day builds streaks
- **Try everything**: Experiment with all drink types for Barista achievement
- **Plan ahead**: Aim for Happy Bean Day on weekends
- **Maintain regularly**: Easy achievements through machine care

#### 📊 Better Statistics
- **Set correct pack size**: Accurate bean consumption tracking
- **Daily logging**: Use the DOWN button to advance days
- **Regular sync**: Export CSV data weekly for backup

#### 🔋 Battery Optimization
- E-ink displays use minimal power
- Battery can last weeks on a single charge
- Disable LED notifications if needed (edit code)

#### 🔧 Maintenance Best Practices
- **Don't ignore warnings**: Machine longevity depends on it
- **Log immediately**: Use Button A for quick completion
- **Track patterns**: Review history to optimize schedules

---

## 🆘 Troubleshooting

<details>
<summary><b>Screen not updating after button press</b></summary>

**Solution:**
1. Check battery level (may need charging)
2. Press reset button on Badger2040
3. Verify main.py is in root directory
4. Reconnect USB and check Thonny output for errors

</details>

<details>
<summary><b>maintenance_config.json error on startup</b></summary>

**Solution:**
1. Verify file is properly copied to Badger2040
2. Check JSON syntax (use online JSON validator)
3. Ensure file is named exactly `maintenance_config.json`
4. Re-copy the file from repository

</details>

<details>
<summary><b>Achievements not unlocking</b></summary>

**Solution:**
1. Check achievements.json file exists
2. Verify drink counts are being saved
3. Try unlocking a simple achievement (first coffee)
4. Reset achievement file if corrupted (delete achievements.json)

</details>

<details>
<summary><b>Date/time incorrect</b></summary>

**Solution:**
1. Use "Datum ändern" in main menu
2. Or edit current_date.txt directly
3. Format: YYYY-MM-DD

</details>

<details>
<summary><b>CSV file not creating</b></summary>

**Solution:**
1. Check available storage on Badger2040
2. Verify write permissions (some firmwares vary)
3. Delete and recreate from scratch
4. Check for file system errors

</details>

---

## ❓ FAQ

**Q: Can I use beanOS with other e-ink displays?**  
A: beanOS is specifically designed for Badger2040. Porting to other displays would require significant code modifications.

**Q: How much storage does beanOS use?**  
A: The main.py is ~56KB. Log files grow slowly (few bytes per day). Typical usage: <100KB total.

**Q: Can I track tea or other beverages?**  
A: Yes! The "other" category and custom drinks can be repurposed for any beverage.

**Q: Does beanOS connect to WiFi?**  
A: No. beanOS is completely offline and stores data locally on the device.

**Q: Can I export data to my phone?**  
A: Connect Badger2040 to computer and copy the CSV file, then transfer to your phone.

**Q: How do I reset all data?**  
A: Delete all generated files (keep main.py and maintenance_config.json), then restart.

**Q: Can multiple people share one beanOS device?**  
A: Currently no multi-user support. Consider using different CSV files for each user.

**Q: How accurate is the bean consumption calculation?**  
A: Based on standard espresso ratios (7g espresso, 14g cappuccino). Adjust if your machine differs.

---

## 🛣️ Roadmap

### Coming in v2.4
- 🔋 **Battery indicator**: Real-time battery level display
- 📈 **Heatmap visualization**: Calendar-style consumption heatmap
- 📊 **Advanced analytics**: Weekday patterns, trend analysis
- 🏆 **Enhanced achievements**: Difficulty levels, monthly challenges

### Future Ideas (v2.5+)
- 📱 Mobile companion app integration
- ☁️ Optional cloud backup
- 🌐 Achievement sharing
- 📸 Photo logging of latte art
- 🎨 Customizable themes

See [ROADMAP.md](ROADMAP.md) for detailed planning.

---

---

## 📝 Changelog

### v2.3.1 (Current)
- 🐛 **Fixed**: Button B now correctly increments cappuccino count
- 🏆 **Improved**: Achievement checking for cappuccino button restored

### v2.3.0 
- 🏆 **New**: Complete achievement system with 20+ achievements
- 🔧 **New**: Smart maintenance reminders with visual warnings
- 📊 **Improved**: Enhanced statistics and tracking

### v2.2.x
- 📊 Bean consumption analytics
- 📦 Multiple pack size support
- 🍹 Extended drink menu (6 specialty drinks)

### v2.1.x
- 🎯 Basic tracking system
- 📈 Simple statistics
- 💾 CSV logging

### v2.0.0
- 🎉 Initial public release
- ☕ Espresso and cappuccino tracking
- 📅 Date management

---

## 🤝 Contributing

We welcome contributions to beanOS! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: Open an issue with detailed reproduction steps
- 💡 **Suggest Features**: Share your ideas in the issues section
- 📖 **Improve Documentation**: Fix typos, add examples, clarify instructions
- 💻 **Submit Code**: Fork, develop, and submit pull requests
- 🎨 **Design**: UI/UX improvements, icons, graphics
- 🌍 **Translate**: Help localize beanOS to other languages

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/beanOS.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes and test on Badger2040
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style Guidelines

- Follow existing code structure
- Comment complex logic
- Test on actual Badger2040 hardware
- Update README if adding features
- Keep MicroPython compatibility in mind

### Testing

Test your changes on a real Badger2040 device:
1. Load modified `main.py`
2. Test all affected features
3. Verify e-ink display updates correctly
4. Check button responsiveness
5. Validate data persistence

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

**What this means:**
- ✅ You can use this software freely
- ✅ You can modify the source code
- ✅ You can distribute it
- ✅ You can use it commercially
- ❗ You must disclose source code of modifications
- ❗ You must license derivatives under GPL-3.0
- ❗ You must state significant changes made

See the [LICENSE](LICENSE) file for full details.

### Anti-Fascist License Addendum

**This software must not be used by:**
- Fascist organizations or individuals
- AfD (Alternative für Deutschland)
- Supporters of authoritarian regimes
- Elon Musk or his entities
- Donald Trump or his entities

Any use by these parties is explicitly forbidden and constitutes a license violation.

---

## 👨‍💻 Author

**Joao Neisinger**

- GitHub: [@neisinger](https://github.com/neisinger)
- Project: [beanOS](https://github.com/neisinger/beanOS)

### Acknowledgments

- **Pimoroni** for the excellent Badger2040 hardware
- **MicroPython** community for the amazing firmware
- All contributors and coffee enthusiasts who make beanOS better

---

## 🌟 Support the Project

If you find beanOS useful, consider:

- ⭐ **Star the repository** on GitHub
- 🐛 **Report bugs** to help improve quality
- 💬 **Share feedback** in discussions
- 🔀 **Contribute code** via pull requests
- ☕ **Share your coffee stats** with the community

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/neisinger/beanOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neisinger/beanOS/discussions)
- **Email**: [Contact via GitHub profile](https://github.com/neisinger)

---

<div align="center">

**Made with ☕ and ❤️ for the coffee community**

[![GitHub stars](https://img.shields.io/github/stars/neisinger/beanOS?style=social)](https://github.com/neisinger/beanOS)
[![GitHub forks](https://img.shields.io/github/forks/neisinger/beanOS?style=social)](https://github.com/neisinger/beanOS/fork)

[⬆ Back to Top](#-beanos)

</div>
