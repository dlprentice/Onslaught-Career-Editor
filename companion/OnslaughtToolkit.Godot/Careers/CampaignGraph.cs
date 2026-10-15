// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Careers;

public enum MissionProgress { Complete, Open, NotYetOpen }

/// <summary>One mission on the campaign map: its column and row, and how far the career has got with it.</summary>
public sealed record CampaignNode(int Index, uint World, int Column, int Row, int RowsInColumn, MissionProgress Progress, string? Rank)
{
    /// <summary>The game's own level code: world 211 is "2.11".</summary>
    public string Code => CareerSave.LevelCode(World);

    /// <summary>The campaign chapter: the code's first number.</summary>
    public int Chapter => (int)(World / 100);
}

/// <summary>A route from one mission to the next, with the state the career stores for it.</summary>
public sealed record CampaignRoute(int From, int To, LinkState State);

/// <summary>
/// The campaign as the career stores it (reverse-engineering/save-file/struct-layouts.md and
/// career-graph.md): each used node's mLowerLink and mHigherLink name links whose mToNode is the next
/// mission. A mission is complete when the game recorded a win for it (mComplete); it is open when a
/// route into it is complete (CN_COMPLETE, the solid line), or when nothing leads to it (training).
/// Missions sit in columns by their longest distance from the start, and within a column by level
/// number. Reading only; a career whose routes loop draws no map.
/// </summary>
public sealed class CampaignGraph
{
    private CampaignGraph(IReadOnlyList<CampaignNode> nodes, IReadOnlyList<CampaignRoute> routes, int columns)
        => (Nodes, Routes, Columns) = (nodes, routes, columns);

    public IReadOnlyList<CampaignNode> Nodes { get; }
    public IReadOnlyList<CampaignRoute> Routes { get; }
    public int Columns { get; }
    public int MaxRows => Nodes.Count == 0 ? 0 : Nodes.Max(node => node.RowsInColumn);

    public static CampaignGraph From(CareerInspection career)
    {
        IReadOnlyList<MissionRecord> missions = career.Missions;
        List<CampaignRoute> routes = [];
        foreach (MissionRecord mission in missions.Where(mission => mission.Used))
        {
            foreach (int link in new[] { mission.LowerLink, mission.HigherLink })
            {
                if (link < 0 || link >= career.Links.Count || career.Links[link] is not { Used: true } record) continue;
                if (record.ToNode >= missions.Count || !missions[(int)record.ToNode].Used) continue;
                routes.Add(new CampaignRoute(mission.Index, (int)record.ToNode, record.State));
            }
        }

        // Longest distance from the start, in topological order; a loop means the routes are not a campaign.
        int[] used = missions.Where(mission => mission.Used).Select(mission => mission.Index).ToArray();
        Dictionary<int, int> incoming = used.ToDictionary(index => index, _ => 0);
        foreach (CampaignRoute route in routes) incoming[route.To]++;
        Dictionary<int, int> column = used.ToDictionary(index => index, _ => 0);
        Queue<int> ready = new(used.Where(index => incoming[index] == 0));
        int placed = 0;
        while (ready.TryDequeue(out int index))
        {
            placed++;
            foreach (CampaignRoute route in routes.Where(route => route.From == index))
            {
                column[route.To] = Math.Max(column[route.To], column[index] + 1);
                if (--incoming[route.To] == 0) ready.Enqueue(route.To);
            }
        }
        if (placed != used.Length) return new CampaignGraph([], [], 0);

        List<CampaignNode> nodes = [];
        foreach (IGrouping<int, int> group in used.GroupBy(index => column[index]).OrderBy(group => group.Key))
        {
            int[] ordered = group.OrderBy(index => missions[index].World).ThenBy(index => index).ToArray();
            for (int row = 0; row < ordered.Length; row++)
            {
                MissionRecord mission = missions[ordered[row]];
                bool reached = routes.Where(route => route.To == mission.Index).ToArray() is var into &&
                    (into.Length == 0 || into.Any(route => route.State == LinkState.Complete));
                MissionProgress progress = mission.Completed ? MissionProgress.Complete : reached ? MissionProgress.Open : MissionProgress.NotYetOpen;
                nodes.Add(new CampaignNode(mission.Index, mission.World, group.Key, row, ordered.Length, progress,
                    mission.Completed ? mission.RankLetter : null));
            }
        }
        return new CampaignGraph(nodes, routes, used.Length == 0 ? 0 : column.Values.Max() + 1);
    }
}
