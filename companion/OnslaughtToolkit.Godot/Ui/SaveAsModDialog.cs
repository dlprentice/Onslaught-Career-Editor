// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Asks what to call an Onslaught CE mod and where to put it: a name, an id (made from the name until it is edited), a version, an
/// author, a description and the folder the mod's own folder goes in. Nothing is written until the player confirms, and Save mod stays
/// off while any of it is something CE's mod loader would refuse.
/// </summary>
internal sealed partial class SaveAsModDialog : ConfirmationDialog
{
    private readonly Label _problem;
    private readonly FileDialog _folderDialog;
    private bool _idEdited, _filling;

    internal SaveAsModDialog(Node popups)
    {
        Title = "Save as a mod";
        OkButtonText = "Save mod";
        GetOkButton().ThemeTypeVariation = "Primary";
        MinSize = new Vector2I(640, 0);
        VBoxContainer body = new();
        body.AddThemeConstantOverride("separation", 10);
        AddChild(body);
        body.Add(Build.Text("The mod is a new folder that Onslaught CE can load. Nothing in your game changes.", "Muted", width: 600));
        GridContainer fields = body.Add(new GridContainer { Columns = 2 });
        fields.AddThemeConstantOverride("h_separation", 12);
        fields.AddThemeConstantOverride("v_separation", 8);
        ModName = Field(fields, "Name", "What the mod is called, 1 to 64 letters, digits or punctuation.");
        Id = Field(fields, "Id", "The mod's folder name and the word you put after mods= in ce.ini: lowercase letters, digits, - and _, up to 48.");
        Version = Field(fields, "Version", "Up to 32 characters.");
        Author = Field(fields, "Author", "Optional, up to 64 characters.");
        Description = Field(fields, "Description", "Optional, up to 1024 characters.");
        fields.Add(Build.Text("Save in", "Muted", wrap: false));
        HBoxContainer where = fields.Add(Build.Row(8));
        where.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        Destination = where.Add(new LineEdit
        {
            ThemeTypeVariation = "MonoField", SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, ClearButtonEnabled = true,
            TooltipText = "The folder the mod's own folder is made in. Onslaught CE looks for mods in the mods folder of its user folder.",
        });
        Button choose = where.Add(Build.Button("Choose…", tooltip: "Pick a folder; or type one. Folders that do not exist yet are made."));
        _problem = body.Add(Build.Text("", "Warn", width: 600));
        _folderDialog = popups.Add(Build.FilePicker("Choose the folder to save the mod in", FileDialog.FileModeEnum.OpenDir));
        choose.Pressed += () => _folderDialog.PopupCenteredRatio(0.75f);
        _folderDialog.DirSelected += folder =>
        {
            Destination.Text = folder;
            Validate();
        };
        ModName.TextChanged += _ =>
        {
            if (!_idEdited && !_filling) SetId(LevelEditorModel.ModIdFromName(ModName.Text));
            Validate();
        };
        Id.TextChanged += _ =>
        {
            if (!_filling) _idEdited = true;
            Validate();
        };
        foreach (LineEdit field in new[] { Version, Author, Description, Destination }) field.TextChanged += _ => Validate();
    }

    internal LineEdit ModName { get; }
    internal LineEdit Id { get; }
    internal LineEdit Version { get; }
    internal LineEdit Author { get; }
    internal LineEdit Description { get; }
    internal LineEdit Destination { get; }
    internal FileDialog FolderDialog => _folderDialog;

    /// <summary>The first thing wrong with what is filled in (a sentence), or an empty string when the mod can be saved.</summary>
    internal string Problem => _problem.Text;

    internal ModInfo Info => new(Id.Text, ModName.Text, Version.Text, Author.Text, Description.Text);

    /// <summary>Starts a fresh form for a level, with the folder CE looks in when it is known.</summary>
    internal void Begin(int level, string destination)
    {
        _filling = true;
        _idEdited = false;
        ModName.Text = LevelEditorModel.DefaultModName(level);
        SetId(LevelEditorModel.ModIdFromName(ModName.Text));
        Version.Text = "1";
        Author.Text = "";
        Description.Text = "";
        Destination.Text = destination;
        _filling = false;
        Validate();
    }

    private void SetId(string id)
    {
        bool was = _filling;
        _filling = true;
        Id.Text = id;
        _filling = was;
    }

    private LineEdit Field(GridContainer grid, string label, string tooltip)
    {
        grid.Add(Build.Text(label, "Muted", wrap: false));
        return grid.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, TooltipText = tooltip, CustomMinimumSize = new Vector2(420, 0) });
    }

    private void Validate()
    {
        string problem = ModStager.Problem(Info) ?? "";
        if (problem.Length == 0 && Destination.Text.Trim().Length == 0) problem = "Choose the folder to save the mod in.";
        else if (problem.Length == 0 && !Path.IsPathFullyQualified(Destination.Text.Trim())) problem = "Choose a full folder path to save the mod in.";
        _problem.Text = problem;
        GetOkButton().Disabled = problem.Length > 0;
    }
}
