// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary host adapter for the production native Aquila scenes. The native
/// component owns specimen admission, part hierarchy, materials and pose math.
/// The remaining world host supplies transition frames and four contacts in
/// batches; it never keeps another decoded hierarchy or animation owner.
/// Original profiles, numerical code and detailed retail provenance are
/// retained only by Scenes/Aquila/Tests/LegacyRetailAquilaReference.cs.
/// </summary>
internal sealed partial class RetailAquilaWalkerAsset
{
    private RetailAquilaWalkerAsset(Node3D root)
    {
        Root = root;
        using Variant returned = root.Call("counts");
        using Godot.Collections.Dictionary counts = returned.AsGodotDictionary();
        PartCount = counts["part_count"].AsInt32();
        SurfaceCount = counts["surface_count"].AsInt32();
        AnimatedPartCount = counts["animated_count"].AsInt32();
        StandingClearance = counts["standing_clearance"].AsSingle();
    }

    public Node3D Root { get; }
    public int PartCount { get; }
    public int SurfaceCount { get; }
    public int AnimatedPartCount { get; }
    public float StandingClearance { get; }

    // Construction belongs to the explicit private-world importer. Runtime
    // binds its saved instances below, and editor tools use the same recipes.
    public static RetailAquilaWalkerAsset CreateWalker(Level100HeightFieldAsset terrain) =>
        Configure("walker", "Walker", terrain);
    public static RetailAquilaWalkerAsset CreateJet(Level100HeightFieldAsset terrain) =>
        Configure("jet", "Jet", terrain);
    public static RetailAquilaWalkerAsset CreateCockpit(Level100HeightFieldAsset terrain) =>
        Configure("cockpit", "Cockpit", terrain);

    private static RetailAquilaWalkerAsset Configure(
        string profile, string sceneName, Level100HeightFieldAsset terrain, Node3D? savedRoot = null)
    {
        ArgumentNullException.ThrowIfNull(terrain);
        Node3D root;
        if (savedRoot is null)
        {
            using PackedScene scene = GD.Load<PackedScene>($"res://Scenes/Aquila/{sceneName}.tscn");
            root = scene.Instantiate<Node3D>();
        }
        else root = savedRoot;
        try
        {
            if (!root.HasMethod("configure_prepared") || root.Get("profile").AsString() != profile)
                throw new InvalidDataException("The imported Aquila is stale. Rebuild the private production scene.");
            using Godot.Collections.Dictionary facts = new()
            {
                ["ambient_color_rgb24"] = terrain.AmbientColorRgb24,
                ["sun_color_rgb24"] = terrain.SunColorRgb24,
                ["anti_sun_color_rgb24"] = terrain.AntiSunColorRgb24,
                ["sunlight_direction"] = terrain.SunlightDirection,
                ["fog_color"] = terrain.FogColor,
                ["fog_density"] = terrain.FogDensity,
            };
            using Variant result = root.Call("configure_prepared", facts, savedRoot is not null, savedRoot is null);
            RequireOk(result);
            return new RetailAquilaWalkerAsset(root);
        }
        catch
        {
            if (savedRoot is null) root.Free();
            throw;
        }
    }

    public void SetVirtualFrame(float virtualFrame)
    {
        using Variant result = Root.Call("set_virtual_frame", virtualFrame);
        RequireOk(result);
    }

    public void SetGroundContactPose(IReadOnlyList<Vector3> contactsInPlayerSpace)
    {
        using Variant contacts = contactsInPlayerSpace is null
            ? default
            : Variant.From(contactsInPlayerSpace.ToArray());
        using Variant result = Root.Call("set_ground_contact_pose", contacts);
        RequireOk(result, nameof(contactsInPlayerSpace));
    }

    private static void RequireOk(Variant returned, string? parameter = null)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native Aquila aborted without a completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (result["ok"].AsBool()) return;
        string message = result["error"].AsString();
        string suffix = $" (Parameter '{parameter}')";
        bool hasParameter = parameter is not null && message.EndsWith(suffix, StringComparison.Ordinal);
        if (hasParameter)
            message = message[..^suffix.Length];
        throw result["error_type"].AsString() switch
        {
            "ArgumentNullException" => new ArgumentNullException(hasParameter ? parameter : null, message),
            "ArgumentException" => new ArgumentException(message, hasParameter ? parameter : null),
            "IndexOutOfRangeException" => new IndexOutOfRangeException(message),
            "InvalidOperationException" => new InvalidOperationException(message),
            _ => new InvalidDataException(message),
        };
    }
}
