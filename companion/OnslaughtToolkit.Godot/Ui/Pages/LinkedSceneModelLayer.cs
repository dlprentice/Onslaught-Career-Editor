// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Missions;
using NVector3 = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Static installed geometry, instantiated only on the Godot UI thread.</summary>
internal partial class LinkedSceneModelLayer : Node3D
{
    private readonly Dictionary<string, Node3D> _templates = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, Node3D> _nodes = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Aabb> _bounds = new(StringComparer.Ordinal);
    private readonly Dictionary<int, Node3D> _rows = [];
    private CeLinkedSceneSnapshot? _scene;
    private IReadOnlyList<CeLinkedSceneInstance> _instances = [];

    internal int ModelInstanceCount => _nodes.Count;
    internal Aabb? WorldBounds
    {
        get
        {
            Aabb? result = null;
            foreach ((string id, Node3D node) in _nodes)
                if (_bounds.TryGetValue(id, out Aabb local))
                {
                    Aabb box = node.Transform * local;
                    result = result is { } previous ? previous.Merge(box) : box;
                }
            return result;
        }
    }

    internal void Show(CeLinkedSceneSnapshot? scene, CeMissionProject? project)
    {
        if (scene is null) { Clear(); return; }
        if (project is null) throw new InvalidDataException("A linked preview requires its project.");
        IReadOnlyList<CeLinkedSceneInstance> instances = scene.Instances(project);
        if (!ReferenceEquals(_scene, scene))
        {
            Clear();
            try
            {
                foreach (CeLinkedSceneModel model in scene.Models)
                {
                    using GltfDocument document = new();
                    using GltfState state = new();
                    if (document.AppendFromBuffer(model.Glb.ToArray(), "", state) != Error.Ok ||
                        document.GenerateScene(state) is not Node3D template)
                        throw new InvalidDataException("A linked model could not be displayed.");
                    _templates.Add(model.Key, template);
                }
                foreach (CeLinkedSceneObject source in scene.Objects)
                {
                    if (source.ModelKey is null || !_templates.TryGetValue(source.ModelKey, out Node3D? template)) continue;
                    Node3D instance = new() { Name = "LinkedObject" };
                    AddChild(instance);
                    Node3D correction = new() { Basis = LinkedSceneCoordinates.GltfToViewport };
                    instance.AddChild(correction);
                    Node3D geometry = (Node3D)template.Duplicate();
                    correction.AddChild(geometry);
                    _nodes.Add(source.Id, instance);
                    Aabb? bounds = null;
                    foreach (MeshInstance3D mesh in geometry.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>())
                    {
                        Aabb box = RelativeTo(mesh, instance) * mesh.GetAabb();
                        bounds = bounds is { } previous ? previous.Merge(box) : box;
                    }
                    if (geometry is MeshInstance3D ownMesh)
                    {
                        Aabb box = RelativeTo(ownMesh, instance) * ownMesh.GetAabb();
                        bounds = bounds is { } previous ? previous.Merge(box) : box;
                    }
                    if (bounds is { } value) _bounds.Add(source.Id, value);
                }
                _scene = scene;
            }
            catch { Clear(); throw; }
        }
        _instances = instances;
        RestorePositions();
    }

    internal void RestorePositions()
    {
        _rows.Clear();
        foreach (CeLinkedSceneInstance item in _instances)
            if (_nodes.TryGetValue(item.Source.Id, out Node3D? node))
            {
                node.Transform = LinkedSceneCoordinates.Transform(item.Source.Orientation, item.Position);
                if (item.PlacementIndex is int row) _rows.Add(row, node);
            }
    }

    internal void PreviewPosition(int row, NVector3 position)
    {
        if (_rows.TryGetValue(row, out Node3D? node)) node.Position = LinkedSceneCoordinates.View(position);
    }

    internal int? RowAt(Camera3D camera, Vector2 screen)
    {
        Vector3 origin = camera.ProjectRayOrigin(screen), direction = camera.ProjectRayNormal(screen);
        int? picked = null;
        float nearest = float.PositiveInfinity;
        foreach (CeLinkedSceneInstance item in _instances)
        {
            if (item.PlacementIndex is not int row || !_nodes.TryGetValue(item.Source.Id, out Node3D? node) ||
                !_bounds.TryGetValue(item.Source.Id, out Aabb box)) continue;
            if (RayBox(origin, direction, node.Transform * box, out float distance) && distance < nearest)
                (picked, nearest) = (row, distance);
        }
        return picked;
    }

    private static bool RayBox(Vector3 origin, Vector3 direction, Aabb box, out float distance)
    {
        float first = 0f, last = float.PositiveInfinity;
        for (int axis = 0; axis < 3; axis++)
        {
            float start = origin[axis], d = direction[axis], minimum = box.Position[axis], maximum = box.End[axis];
            if (Math.Abs(d) < 0.000001f) { if (start < minimum || start > maximum) { distance = 0; return false; } continue; }
            float a = (minimum - start) / d, b = (maximum - start) / d;
            first = Math.Max(first, Math.Min(a, b)); last = Math.Min(last, Math.Max(a, b));
            if (first > last) { distance = 0; return false; }
        }
        distance = first;
        return float.IsFinite(first);
    }

    private static Transform3D RelativeTo(Node3D node, Node3D root)
    {
        Transform3D transform = node.Transform;
        for (Node? parent = node.GetParent(); parent is not null && parent != root; parent = parent.GetParent())
            if (parent is Node3D spatial) transform = spatial.Transform * transform;
        return transform;
    }

    internal void Clear()
    {
        _rows.Clear(); _instances = []; _bounds.Clear(); _scene = null;
        foreach (Node3D node in _nodes.Values)
            if (GodotObject.IsInstanceValid(node)) { RemoveChild(node); node.Free(); }
        _nodes.Clear();
        foreach (Node3D template in _templates.Values)
            if (GodotObject.IsInstanceValid(template)) template.Free();
        _templates.Clear();
    }

    public override void _ExitTree() => Clear();
}

internal static class LinkedSceneCoordinates
{
    // GltfExport uses (-X,-Z,Y), terrain uses (X,-Z,-Y): exact Ry(pi), below each world-instance orientation.
    internal static Basis GltfToViewport => new(-Vector3.Right, Vector3.Up, -Vector3.Back);
    internal static Vector3 View(NVector3 value) => new(value.X, -value.Z, -value.Y);

    internal static Transform3D Transform(NVector3 angles, NVector3 position)
    {
        MeshBasis original = Rotation(angles);
        // Columns of V * original * V^-1, with V^-1 == V.
        Basis basis = new(View(original.Apply(NVector3.UnitX)), View(original.Apply(-NVector3.UnitZ)),
            View(original.Apply(-NVector3.UnitY)));
        return new(basis, View(position));
    }

    // Preview form of FMatrix(yaw,pitch,roll), also used by the public rebuild's FMatrix.FromYawPitchRoll.
    // This static display calculation does not claim x87 arithmetic or simulation parity.
    internal static MeshBasis Rotation(NVector3 angles)
    {
        float cy = MathF.Cos(angles.X), sy = MathF.Sin(angles.X), cp = MathF.Cos(angles.Y), sp = MathF.Sin(angles.Y),
              cr = MathF.Cos(angles.Z), sr = MathF.Sin(angles.Z);
        return new(new(cr * cy - sp * sr * sy, -cp * sy, sp * cr * sy + sr * cy),
            new(sp * sr * cy + cr * sy, cp * cy, sr * sy - sp * cr * cy), new(-cp * sr, sp, cp * cr));
    }
}
