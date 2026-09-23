// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Only the existing managed comparison harnesses use this native-root adapter.</summary>
internal static class FrontendHarnessChecks
{
    internal static bool HasNativeRoot(RetailFrontendFlow flow)
    {
        using Variant script = flow.View.GetScript();
        return !typeof(Node).IsAssignableFrom(typeof(RetailFrontendFlow))
            && script.AsGodotObject() is GDScript native
            && native.ResourcePath == "res://Scenes/Frontend/frontend_flow.gd";
    }

    internal static void ReleaseFacades(List<RetailFrontendFlow> facades)
    {
        foreach (RetailFrontendFlow facade in facades)
        {
            Control view = facade.View;
            facade.Dispose();
            // A failed Initialize may precede AddChild. The test owns that
            // orphan; attached roots are removed by the existing viewport cleanup.
            if (GodotObject.IsInstanceValid(view) && view.GetParent() is null) view.Free();
        }
        facades.Clear();
    }

    internal static void Command(RetailFrontendFlow flow, string method, params Variant[] arguments)
    {
        using D result = flow.InvokeNative(method, arguments);
    }

    internal static bool Boolean(RetailFrontendFlow flow, string method, params Variant[] arguments)
    {
        using D result = flow.InvokeNative(method, arguments);
        using Variant value = result["value"];
        return value.AsBool();
    }

    internal static int Integer(RetailFrontendFlow flow, string method, params Variant[] arguments)
    {
        using D result = flow.InvokeNative(method, arguments);
        using Variant value = result["value"];
        return value.AsInt32();
    }

    internal static int Hit(RetailFrontendFlow flow, string method, Vector2 point)
    {
        using Variant result = flow.View.Call(method, point);
        return result.AsInt32();
    }

    internal static Texture2D[] SharedFrames(RetailFrontendFlow flow)
    {
        // Inspect the actual native page batch. Never decode a parallel preview.
        using Variant value = flow.View.Get("_fe_back_frames");
        using Godot.Collections.Array frames = value.AsGodotArray();
        var textures = new Texture2D[frames.Count];
        for (int index = 0; index < textures.Length; index++)
        {
            using Variant texture = frames[index];
            textures[index] = texture.As<Texture2D>();
        }
        return textures;
    }

    internal static void SetLoadingCaption(RetailFrontendFlow flow, string value)
    {
        // The page helper caches the admitted caption just as the former
        // managed host did; the retained pixel fixture overrides that cache.
        using Variant pages = flow.View.Get("_pages");
        using Variant units = value.Select(character => (int)character).ToArray();
        pages.AsGodotObject().Set("_loading_caption", units);
    }
}
