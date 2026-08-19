// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// <c>CGame::GetNumPrimaryObjectives</c> and
/// <c>GetNumSecondaryObjectives</c> — the scans FillOut uses to
/// decide whether the secondary ranking clamp runs, and the four
/// <c>MOS_COMPLETE</c> primary statuses a Level 100 win copies.
/// </summary>
/// <remarks>
/// <para>
/// Owner in the pinned drop: <c>references/Onslaught/game.cpp:4056-4078</c>
/// and <c>:965</c>. Retail identities: <c>0x00472670</c> and
/// <c>0x00472690</c> in the pristine <c>74154bfa…</c> image
/// (2,506,752 bytes). File offset = VA − 0x400000. Re-derived this
/// session.
/// </para>
/// <para>
/// <b>The scan counts every non-zero status.</b>
/// <c>0x00472670</c> is <c>xor eax, eax</c> /
/// <c>add ecx, 0x4C</c> / <c>mov edx, 0xA</c> /
/// <c>cmp dword ptr [ecx], 0</c> / <c>je</c> / <c>inc eax</c> /
/// <c>add ecx, 8</c> / <c>dec edx</c> / <c>jnz</c> / <c>ret</c>.
/// <c>0x00472690</c> is the same loop after
/// <c>add ecx, 0x9C</c>. <c>MOS_NOT_DEFINED</c> is the zero
/// sentinel (W004 A11). <c>MOS_FAILED</c> (2) still increments.
/// A rebuild that counted only <c>MOS_COMPLETE</c> would drop a
/// failed row.
/// </para>
/// <para>
/// <b>Level 100 copies four primaries and no secondaries.</b>
/// The shipped script defines objectives 1-4; after a win those
/// four statuses are <c>MOS_COMPLETE</c> (1), and the other six
/// primary slots plus all ten secondaries stay 0. That is not the
/// rebuild mission enum's <c>Level100PrimaryObjectiveStatus.Complete
/// = 2</c>. Do not invent secondary content. FillOut's
/// <c>if (GetNumSecondaryObjectives())</c> therefore stays false
/// and the 0.4 / 0.6 clamp is skipped — already pinned.
/// </para>
/// <para>
/// <b>Not established here.</b> The mission-layer enum mapping in
/// <c>Level100Mission</c>. Score-time ranking. Career does not
/// consume the primary table.
/// </para>
/// </remarks>
public static class RetailGameObjectiveCount
{
    /// <summary><c>MOS_NOT_DEFINED</c> — the <c>cmp [ecx], 0</c> sentinel.</summary>
    public const int StatusNotDefined = 0;

    /// <summary><c>MOS_COMPLETE</c> — <c>cmp ecx, 1</c> at <c>0x004496F6</c>.</summary>
    public const int StatusComplete = RetailEndLevelObjectives.StatusComplete;

    /// <summary><c>MOS_FAILED</c> — <c>cmp ecx, 2</c> at <c>0x004496FB</c>.</summary>
    public const int StatusFailed = RetailEndLevelObjectives.StatusFailed;

    /// <summary>The <c>mov edx, 0xA</c> loop counter at <c>0x00472675</c>.</summary>
    public const int ObjectiveSlotCount = RetailEndLevelObjectives.PrimaryObjectiveCount;

    /// <summary>Shipped Level 100 primary count — four defined rows.</summary>
    public const int Level100PrimaryCount = 4;

    /// <summary>Shipped Level 100 secondary count — there are none.</summary>
    public const int Level100SecondaryCount = 0;

    /// <summary>
    /// <c>CGame::GetNumPrimaryObjectives</c> — <c>0x00472670</c>.
    /// </summary>
    public static int GetNumPrimaryObjectives(IReadOnlyList<int> statuses) =>
        CountDefined(statuses);

    /// <summary>
    /// <c>CGame::GetNumSecondaryObjectives</c> — <c>0x00472690</c>.
    /// </summary>
    public static int GetNumSecondaryObjectives(IReadOnlyList<int> statuses) =>
        CountDefined(statuses);

    /// <summary>
    /// The ten primary <c>GetStatus()</c> words FillOut copies after
    /// a Level 100 win.
    /// </summary>
    public static int[] Level100WonPrimaryStatuses()
    {
        int[] statuses = new int[ObjectiveSlotCount];
        for (int index = 0; index < Level100PrimaryCount; index++)
        {
            statuses[index] = StatusComplete;
        }

        return statuses;
    }

    /// <summary>
    /// The ten unset secondary words — Level 100 authors none.
    /// </summary>
    public static int[] Level100WonSecondaryStatuses() =>
        RetailFillOutEndLevelData.UnsetSecondaryStatuses();

    private static int CountDefined(IReadOnlyList<int> statuses)
    {
        if (statuses is null)
        {
            throw new ArgumentNullException(nameof(statuses));
        }

        if (statuses.Count != ObjectiveSlotCount)
        {
            throw new ArgumentException(
                $"The loop counter at 0x00472675 is {ObjectiveSlotCount}; " +
                "retail reads exactly that many entries with no early exit.",
                nameof(statuses));
        }

        int found = 0;
        for (int index = 0; index < ObjectiveSlotCount; index++)
        {
            if (statuses[index] != StatusNotDefined)
            {
                found++;
            }
        }

        return found;
    }
}
