// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The career's path through the campaign, drawn in code from <see cref="CampaignGraph"/>: a circle per
/// mission in columns from training to the finale, banded by chapter, with the rank letter on each
/// completed mission and the routes between them: solid where the career went on, broken where the game
/// recorded a route not taken, faint where it has not reached. Hovering a mission names it.
/// </summary>
internal sealed partial class CampaignMap : Control
{
    private const float Radius = 11f, RowGap = 38f, Top = 34f, Bottom = 14f, Side = 22f;

    private readonly Dictionary<int, Vector2> _positions = [];
    private CampaignGraph? _graph;
    private GameText? _text;

    internal CampaignMap()
    {
        MouseFilter = MouseFilterEnum.Pass;
        SizeFlagsHorizontal = SizeFlags.ExpandFill;
        TooltipText = "Hover a mission to see its name.";
        Resized += QueueRedraw;
    }

    internal CampaignGraph? Graph => _graph;

    internal void Show(CampaignGraph graph, GameText? text)
    {
        (_graph, _text) = (graph, text);
        CustomMinimumSize = new Vector2(0, Top + Math.Max(0, graph.MaxRows - 1) * RowGap + 2 * Radius + Bottom);
        QueueRedraw();
    }

    /// <summary>What hovering a mission says: its code, the game's name for it, and how far the career got.</summary>
    internal string Describe(CampaignNode node)
    {
        string name = _text?.LevelName(node.World) is string display && display.IndexOf(" - ", StringComparison.Ordinal) is int dash && dash > 0
            ? display[(dash + 3)..] : "";
        string state = node.Progress switch
        {
            MissionProgress.Complete => "Complete" + (node.Rank is string rank ? $", rank {rank}" : ""),
            MissionProgress.Open => "Open: a route leads here",
            _ => "Not reached yet",
        };
        return $"{node.Code}{(name.Length > 0 ? "  " + name : "")}\n{state}";
    }

    internal CampaignNode? NodeAt(Vector2 position)
    {
        Layout();
        return _graph?.Nodes.FirstOrDefault(node => _positions.TryGetValue(node.Index, out Vector2 centre) &&
            centre.DistanceTo(position) <= Radius + 4);
    }

    public override string _GetTooltip(Vector2 atPosition) =>
        NodeAt(atPosition) is CampaignNode node ? Describe(node) : TooltipText;

    public override void _Draw()
    {
        if (_graph is not CampaignGraph graph || graph.Nodes.Count == 0) return;
        Layout();
        Font font = ThemeDB.FallbackFont;
        float step = Step(graph);

        // Chapter bands: alternate shading behind each chapter's columns, its number above them.
        foreach (IGrouping<int, CampaignNode> chapter in graph.Nodes.GroupBy(node => node.Chapter).OrderBy(group => group.Key))
        {
            float left = Side + chapter.Min(node => node.Column) * step - step / 2, right = Side + chapter.Max(node => node.Column) * step + step / 2;
            left = Math.Max(0, left);
            right = Math.Min(Size.X, right);
            if (chapter.Key % 2 == 0) DrawRect(new Rect2(left, 0, right - left, Size.Y), new Color(Palette.Raised, 0.55f));
            string label = $"Chapter {chapter.Key}";
            if (font.GetStringSize(label, HorizontalAlignment.Left, -1, 12).X > right - left - 6) label = chapter.Key.ToString();
            DrawString(font, new Vector2(left, 17), label, HorizontalAlignment.Center, right - left, 12, Palette.Muted);
        }

        foreach (CampaignRoute route in graph.Routes.OrderBy(route => route.State == LinkState.Complete))
        {
            if (!_positions.TryGetValue(route.From, out Vector2 from) || !_positions.TryGetValue(route.To, out Vector2 to)) continue;
            Vector2 direction = (to - from).Normalized();
            (from, to) = (from + direction * Radius, to - direction * Radius);
            switch (route.State)
            {
                case LinkState.Complete:
                    DrawLine(from, to, Palette.Good, 3f, true);
                    break;
                case LinkState.AlternateRoute:
                    DrawDashedLine(from, to, Palette.Muted, 2f, 5f, true, true);
                    break;
                default:
                    DrawLine(from, to, Palette.Border, 1.5f, true);
                    break;
            }
        }

        foreach (CampaignNode node in graph.Nodes)
        {
            Vector2 centre = _positions[node.Index];
            switch (node.Progress)
            {
                case MissionProgress.Complete:
                    DrawCircle(centre, Radius, Palette.Good, true, -1, true);
                    if (node.Rank is string rank)
                        DrawString(CompanionTheme.StrongFont, centre + new Vector2(-Radius, 5), rank, HorizontalAlignment.Center, 2 * Radius, 13,
                            Palette.Background);
                    break;
                case MissionProgress.Open:
                    DrawCircle(centre, Radius, Palette.Field, true, -1, true);
                    DrawCircle(centre, Radius - 1, Palette.Data, false, 2.5f, true);
                    break;
                default:
                    DrawCircle(centre, Radius, Palette.Background, true, -1, true);
                    DrawCircle(centre, Radius - 1, Palette.Border, false, 1.5f, true);
                    break;
            }
        }
    }

    private float Step(CampaignGraph graph) => graph.Columns <= 1 ? 0 : (Size.X - 2 * Side) / (graph.Columns - 1);

    private void Layout()
    {
        _positions.Clear();
        if (_graph is not CampaignGraph graph) return;
        float step = Step(graph), middle = Top + Radius + (graph.MaxRows - 1) * RowGap / 2;
        foreach (CampaignNode node in graph.Nodes)
            _positions[node.Index] = new Vector2(Side + node.Column * step, middle + (node.Row - (node.RowsInColumn - 1) / 2f) * RowGap);
    }
}

/// <summary>One legend mark drawn the way the campaign map draws it.</summary>
internal sealed partial class CampaignSwatch : Control
{
    private readonly string _kind;

    internal CampaignSwatch(string kind)
    {
        _kind = kind;
        CustomMinimumSize = new Vector2(kind.StartsWith("route", StringComparison.Ordinal) ? 26 : 16, 16);
        SizeFlagsVertical = SizeFlags.ShrinkCenter;
        MouseFilter = MouseFilterEnum.Ignore;
    }

    public override void _Draw()
    {
        Vector2 centre = Size / 2;
        switch (_kind)
        {
            case "complete":
                DrawCircle(centre, 7, Palette.Good, true, -1, true);
                break;
            case "open":
                DrawCircle(centre, 7, Palette.Field, true, -1, true);
                DrawCircle(centre, 6, Palette.Data, false, 2f, true);
                break;
            case "closed":
                DrawCircle(centre, 6, Palette.Border, false, 1.5f, true);
                break;
            case "route-taken":
                DrawLine(new Vector2(1, centre.Y), new Vector2(Size.X - 1, centre.Y), Palette.Good, 3f, true);
                break;
            case "route-not-taken":
                DrawDashedLine(new Vector2(1, centre.Y), new Vector2(Size.X - 1, centre.Y), Palette.Muted, 2f, 5f, true, true);
                break;
            default:
                DrawLine(new Vector2(1, centre.Y), new Vector2(Size.X - 1, centre.Y), Palette.Border, 1.5f, true);
                break;
        }
    }
}
