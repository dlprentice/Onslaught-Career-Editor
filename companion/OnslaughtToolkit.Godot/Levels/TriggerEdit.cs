// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Changes one existing spherical trigger's radius. The command belongs to the captured body, row and record;
/// making, undoing or redoing it refuses a replaced record or an unexpected radius instead of overwriting it.
/// New requested radii must be finite and nonnegative. An older stored radius is kept exactly for undo.
/// </summary>
public sealed class ResizeSphereTrigger : IEditCommand
{
    private readonly WorldBody _body;
    private readonly PlacedObject _record;
    private readonly ObjectInit _init;
    private readonly SphereTriggerInit _trigger;
    private readonly int _objectId;
    private readonly float _previous;
    private bool _made;

    public ResizeSphereTrigger(WorldBody body, int thingIndex, float radius)
    {
        ArgumentNullException.ThrowIfNull(body);
        if (!IsRequestedRadius(radius))
            throw new InvalidOperationException("A trigger radius must be a finite number at least zero.");
        if (thingIndex < 0 || thingIndex >= body.Things.Count)
            throw new InvalidOperationException($"There is no row {thingIndex}: this world has {body.Things.Count}.");
        PlacedObject record = body.Things[thingIndex];
        if (!IsSphereTrigger(record))
            throw new InvalidOperationException($"Row {thingIndex} is not a spherical trigger with a stored radius.");
        _body = body;
        _record = record;
        _init = record.Init;
        _trigger = record.Init.SphereTrigger!;
        _objectId = record.ObjectId;
        _previous = _trigger.Radius;
        ThingIndex = thingIndex;
        Radius = radius;
        Description = $"Resize {record.Label} (row {thingIndex})";
    }

    public int ThingIndex { get; }
    public float Radius { get; }
    public string Description { get; }

    /// <summary>False only when the requested and captured stored radii have the same bits.</summary>
    public bool ChangesRadius => !SameBits(_previous, Radius);

    /// <summary>Use <see cref="EditSession.ResizeTrigger"/> to ignore an unchanged request without recording history.</summary>
    public void Do(WorldBody body)
    {
        if (_made) throw new InvalidOperationException("This trigger resize has already been made. Take it back first.");
        RequireTarget(body, _previous);
        if (!ChangesRadius) throw new InvalidOperationException("This trigger already has the requested radius.");
        _trigger.Radius = Radius;
        _made = true;
    }

    public void Undo(WorldBody body)
    {
        if (!_made) throw new InvalidOperationException("This trigger resize has not been made, so there is nothing to take back.");
        RequireTarget(body, Radius);
        _trigger.Radius = _previous;
        _made = false;
    }

    private void RequireTarget(WorldBody body, float expected)
    {
        if (!ReferenceEquals(body, _body) || ThingIndex >= body.Things.Count ||
            !ReferenceEquals(body.Things[ThingIndex], _record) || !ReferenceEquals(_record.Init, _init) ||
            !ReferenceEquals(_init.SphereTrigger, _trigger) || _record.ObjectId != _objectId ||
            !IsSphereTrigger(_record) || !SameBits(_trigger.Radius, expected))
            throw new InvalidOperationException("The trigger or its radius changed after this resize was prepared.");
    }

    internal static bool IsSphereTrigger(PlacedObject? record)
    {
        if (record?.Init?.SphereTrigger is null) return false;
        try { return ObjectKinds.ClassOf(record.ObjectId) == ObjectClass.SphereTrigger; }
        catch (InvalidDataException) { return false; }
    }

    internal static bool IsRequestedRadius(float radius) => float.IsFinite(radius) && radius >= 0;
    internal static bool SameBits(float left, float right) => BitConverter.SingleToUInt32Bits(left) == BitConverter.SingleToUInt32Bits(right);
}

/// <summary>An existing spherical trigger whose stored radius differs from the session's baseline.</summary>
public sealed record TriggerRadiusChange(int Index, string Name, float From, float To);
