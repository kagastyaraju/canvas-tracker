# canvas-tracker

A command-line tool that shows your upcoming Canvas assignments every time you open your terminal. Fetches due dates across all your active courses directly from your Canvas calendar feed.

## Usage

### First-time setup

Get your Canvas iCal URL:
- Go to **canvas.ucsd.edu** → **Calendar** → scroll down in the right panel → **Calendar Feed** → copy the URL

Then configure the tool:

```bash
canvas-tracker configure
```

### Show upcoming assignments

```bash
canvas-tracker
```

Filter by course:

```bash
canvas-tracker upcoming --course DSC190
```

### Auto-show on every terminal open

```bash
canvas-tracker setup-autorun
```

Adds `canvas-tracker` to your `.zshrc` or `.bashrc` so your assignments appear automatically whenever you open a new terminal window.