# Onslaught Career Editor

WPF save file editor for Battle Engine Aquila (.bes files).

## Tech Stack

- .NET 9.0 (Windows)
- WPF (Windows Presentation Foundation)
- C# with nullable reference types enabled
- Visual Studio 2022 / .NET SDK

## Project Structure

```
MainWindow.xaml[.cs]    - UI and event handlers
BesFilePatcher.cs       - Core patching logic
App.xaml[.cs]           - Application entry
```

## Code Style

- `PascalCase` - classes, methods, properties
- `camelCase` - local variables, parameters
- `SCREAMING_SNAKE_CASE` - constants
- Namespace: `Onslaught___Career_Editor` (triple underscore, historical)

## Save File Format

Battle Engine Aquila uses a 10,004-byte binary format with:
- Little-endian encoding
- Fixed-point 16.16 integers (left-shifted by 16 bits)
- IEEE-754 floats for scores/rankings
- See `README.MD` for comprehensive offset map

## Building

```bash
dotnet build "Onslaught - Career Editor.sln"
```

Requires Windows SDK for WPF support.

## Contributing

- Keep patches simple and well-documented
- Test against known-good .bes files
- Refer to README.MD for offset/structure details
- God mode only works in Free-Play mode
- Rank injection is limited due to hidden EndLevelData structure

## License

MIT License
