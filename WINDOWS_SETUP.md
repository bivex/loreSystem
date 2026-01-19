# Windows Setup Guide for MythWeave

## Prerequisites

1. **Install Python** (if not already installed):
   - Visit https://python.org/downloads/
   - Download the latest Python installer for Windows
   - **Important**: During installation, check "Add Python to PATH"
   - Restart your command prompt after installation

2. **Verify Python Installation**:
   Open Command Prompt and run:
   ```cmd
   python --version
   ```
   You should see something like: `Python 3.11.0` (or newer)

## Running the Application

### Method 1: One-Click Launcher (Recommended)
1. Double-click `launch_gui.bat` in the project folder
2. The script will automatically:
   - Create a virtual environment (if needed)
   - Install required dependencies
   - Launch the MythWeave GUI

### Method 2: Manual Setup
If you prefer manual control:

1. **Create Virtual Environment**:
   ```cmd
   python -m venv venv
   ```

2. **Activate Virtual Environment**:
   ```cmd
   venv\Scripts\activate.bat
   ```

3. **Install Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```cmd
   python run_gui.py
   ```

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and ensure "Add Python to PATH" is checked
- Or edit `launch_gui.bat` and change `python` to the full path (e.g., `C:\Python311\python.exe`)

### "Failed to create virtual environment"
- Ensure you have write permissions in the project folder
- Try running Command Prompt as Administrator

### GUI Won't Start
- Check that PyQt6 installed correctly: `python -c "import PyQt6; print('PyQt6 OK')"`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Antivirus Blocking
Some antivirus software may flag the virtual environment or PyQt6 installation. Add exceptions if needed.

## First Steps

Once the GUI launches:
1. Click **"Load"** → Navigate to `examples/sample_lore.json`
2. Explore the sample worlds, characters, and events
3. Create your own content using the tabs at the top

For detailed instructions, see `QUICKSTART_GUI.md`.

## Support

If you encounter issues:
- Check the console output for error messages
- Verify all prerequisites are met
- See `QUICKSTART_GUI.md` for detailed GUI instructions