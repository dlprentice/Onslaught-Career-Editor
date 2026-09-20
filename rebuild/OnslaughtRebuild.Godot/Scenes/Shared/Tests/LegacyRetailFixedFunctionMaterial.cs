// SPDX-License-Identifier: GPL-3.0-or-later
// Exact pre-native material/layer/light-rig reference; only type names and
// the legacy heightfield dependency change. This owner is never gameplay.
using Godot;
namespace OnslaughtRebuild.GodotClient;

internal sealed record LegacyRetailTextureLayer(
    Texture2D Texture,
    float Opacity,
    Vector2 Offset,
    Vector2 Scale,
    bool BlendTextureAlpha = false);

/// <summary>
/// The two-directional-light fixed-function rig a draw through
/// <see cref="LegacyRetailFixedFunctionMaterial"/> runs under: <c>D3DRS_AMBIENT</c>
/// plus light 0 and light 1, whose directions retail keeps exactly
/// anti-parallel on both measured rigs.
/// </summary>
/// <remarks>
/// This is a per-draw property in the released game, not a level constant. The
/// values below were read at the <c>IDirect3DDevice9</c> calls themselves — the
/// <c>SetLight</c> site at <c>0x005512e1</c> (the tail of <c>0x00551200</c>,
/// which builds the 0x68-byte <c>D3DLIGHT9</c> on the stack from the 0x5c-byte
/// engine record at <c>0x009c65c0 + index*0x5c</c>), the <c>LightEnable</c> site
/// at <c>0x00551101</c>, and the seven <c>SetMaterial</c> sites — over two
/// independent launches of the safe copy (sha256 <c>E1436EF7…FADF4</c>) at two
/// different level times, with every payload byte-identical between them:
/// <list type="bullet">
/// <item><description>130 mode-0 <c>CRTMesh</c> static-world draws:
/// <c>D3DRS_AMBIENT = 0x000d0f2b</c>, light 0 = the height field's sun colour
/// travelling along the height field's sun vector, light 1 = the full anti-sun
/// travelling the other way.</description></item>
/// <item><description>442 <c>CRTTree</c> close-pine draws:
/// <c>D3DRS_AMBIENT = 0x0039293e</c>, light 0 = the sun colour scaled by
/// <c>0.1</c> travelling straight down BEA <c>+Z</c>, light 1 = the full
/// anti-sun travelling straight up BEA <c>-Z</c>.</description></item>
/// </list>
/// <c>D3DLIGHT9.Ambient</c> is <c>(0,0,0,0)</c> on both lights at every mesh
/// draw — only <c>CDXLandscape::Render</c>'s own re-upload carries a light
/// ambient term — so the whole normal-independent part of the vertex colour is
/// <c>D3DRS_AMBIENT</c>, and <c>D3DLIGHT9.Diffuse</c> carries the rest.
/// </remarks>
internal readonly record struct LegacyRetailMeshLightRig(
    Vector3 AmbientColor,
    Vector3 KeyLightColor,
    Vector3 FillLightColor,
    Vector3 KeyLightDirection)
{
    /// <summary>
    /// <c>D3DRS_AMBIENT</c> at all 442 <c>CRTTree</c> draws of a frame,
    /// <c>0x0039293e</c> = (57, 41, 62)/255, constant across 438 and 436 draws
    /// in two launches.
    ///
    /// FLAGGED: unlike the static world's <c>0x000d0f2b</c>, which is the
    /// height field's own <c>CHFD + 0x108C</c>, this value has no established
    /// shipped source. A whole-image operand scan of the safe copy finds zero
    /// occurrences of <c>0x0039293e</c>, so retail composes it at runtime and
    /// the composition is not yet read. It is a measurement, not a derivation.
    /// </summary>
    public const uint ClosePineAmbientRgb24 = 0x0039293Eu;

    /// <summary>
    /// The scale retail applies to the sun colour for the close-pine key light.
    /// <c>CRTTree::BuildRenderOutputs</c> unpacks the packed RGB24 sun colour at
    /// <c>0x004ddcb8</c>–<c>0x004ddd2f</c> and multiplies each channel by
    /// <c>[0x005db060]</c> = <c>1/256</c> and by <c>[0x005d85c0]</c> =
    /// <c>0.10000000149011612</c>. The parallel anti-sun block at
    /// <c>0x004ddd59</c> applies <c>1/256</c> only, which is why the fill light
    /// arrives unscaled. Confirmed at the device: the uploaded light-0
    /// <c>Diffuse</c> <c>(0.07382812, 0.06914063, 0.04726563)</c> divided by the
    /// sun colour <c>(189, 177, 121)/256</c> is <c>0.1</c> to float32 on all
    /// three channels.
    /// </summary>
    public const float ClosePineKeyLightScale = 0.1f;

    /// <summary>
    /// The rig measured at the 130 mode-0 <c>CRTMesh</c> static-world draws.
    /// This is the law the reconstruction already implemented, reproduced here
    /// unchanged: the device-side reading confirms it channel for channel,
    /// including the 3.32x up/under step, so nothing about the buildings moves.
    /// </summary>
    public static LegacyRetailMeshLightRig StaticWorld(LegacyLevel100HeightFieldReference terrain) => new(
        ToColorVector(terrain.AmbientColorRgb24, 255f),
        ToColorVector(terrain.SunColorRgb24, 256f),
        ToColorVector(terrain.AntiSunColorRgb24, 256f),
        terrain.SunlightDirection);

    /// <summary>
    /// The rig measured at the 442 <c>CRTTree</c> close-pine draws.
    ///
    /// Both light colours still come from the shipped height field and the only
    /// scale is the shipped <c>0.1</c>; the one value with no shipped source is
    /// <see cref="ClosePineAmbientRgb24"/>. With stage-zero
    /// <c>MODULATE2X</c> and white vertex colour this yields
    /// <c>2 x (ambient + light)</c> = <c>(0.59472, 0.45985, 0.58081)</c> on an
    /// up-facing normal and <c>(0.72050, 0.59501, 0.92377)</c> on a down-facing
    /// one — a step of <c>(1.21, 1.29, 1.59)</c>, luminance <c>1.304</c>,
    /// against the retail median of <c>1.144</c> measured at 353 matched pixel
    /// pairs. Note the sign: retail's foliage undersides are brighter and bluer
    /// than its tops.
    /// </summary>
    public static LegacyRetailMeshLightRig ClosePine(LegacyLevel100HeightFieldReference terrain) => new(
        ToColorVector(ClosePineAmbientRgb24, 255f),
        ToColorVector(terrain.SunColorRgb24, 256f) * ClosePineKeyLightScale,
        ToColorVector(terrain.AntiSunColorRgb24, 256f),
        // The uploaded light-0 Direction is BEA (0, 0, +1) exactly, and BEA's Z
        // is down. Carried into Godot by the same map the rest of the world path
        // uses -- MapVector, (x, y, z) -> (x, -z, -y), which
        // LegacyLevel100HeightFieldReference applies to the height field's own sun vector
        // and which Level100VertexDiffuseTests proves is the composite of
        // emit_obj's diag(1,1,-1) and this asset's RotationDegrees(-90, 0, 0) --
        // that is (0, -1, 0). Light 1's Direction is BEA (0, 0, -1), the exact
        // negation, which is the anti-parallel form the shader assumes.
        new Vector3(0f, -1f, 0f));

    private static Vector3 ToColorVector(uint rgb, float divisor) => new(
        ((rgb >> 16) & 0xFF) / divisor,
        ((rgb >> 8) & 0xFF) / divisor,
        (rgb & 0xFF) / divisor);
}

/// <summary>
/// The stage-zero <c>D3DTSS_COLOROP</c> a draw through
/// <see cref="LegacyRetailFixedFunctionMaterial"/> runs under. The members carry the
/// Direct3D <c>D3DTOP</c> enumerant values so the source reads the same way the
/// runtime dump does.
/// </summary>
/// <remarks>
/// This is a per-draw property in the released game, not a constant. Every
/// stage-zero <c>D3DTSS_COLOROP</c> value below was read out of the running
/// safe copy's texture-stage-state shadow at <c>0x008557f4</c> — the caching
/// setter at <c>0x00513820</c> computes its index as
/// <c>(type + stage*0n30)*4 + 0x008557f0</c> at <c>0x0051382a</c>–<c>0x00513833</c>,
/// and the invalidator at <c>0x00513600</c> clears 0n240 = 8 stages x 0n30
/// dwords there — sampled at the entry to <c>CMeshRenderer::RenderMeshCore</c>
/// (<c>0x00549570</c>, the image's only mesh-render call site) for one whole
/// Level 100 frame:
/// <list type="bullet">
/// <item><description>134 mode-0 static-world draws: <c>5</c>
/// = <c>D3DTOP_MODULATE2X</c>.</description></item>
/// <item><description>442 <c>CRTTree</c> close-mesh draws: <c>5</c>
/// = <c>D3DTOP_MODULATE2X</c>.</description></item>
/// <item><description>All seven cockpit batches: <c>4</c>
/// = <c>D3DTOP_MODULATE</c>, read 16 times inside the cockpit window with zero
/// stage-zero <c>COLOROP</c> transitions while inside it.</description></item>
/// <item><description>19 mode-4 static-world draws in that same frame: <c>4</c>
/// = <c>D3DTOP_MODULATE</c>.</description></item>
/// </list>
/// <c>COLORARG1</c> is <c>2</c> = <c>D3DTA_TEXTURE</c>, <c>COLORARG2</c> is
/// <c>0</c> = <c>D3DTA_DIFFUSE</c> and stage-one <c>COLOROP</c> is <c>1</c> =
/// <c>D3DTOP_DISABLE</c> at every one of those draws.
/// </remarks>
internal enum LegacyRetailStageZeroColorOperation
{
    /// <summary>D3DTOP_MODULATE. Texture x diffuse, no doubling.</summary>
    Modulate = 4,

    /// <summary>D3DTOP_MODULATE2X. Texture x diffuse x 2.</summary>
    Modulate2X = 5,
}

internal static class LegacyRetailFixedFunctionMaterial
{
    private static Shader? _objectShader;

    private const string ShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_back;

        uniform sampler2D base_texture : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D dot3_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D reflection_texture : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D overlay_texture : filter_linear_mipmap, repeat_enable;
        uniform float has_dot3;
        uniform float has_reflection;
        uniform float has_overlay;
        uniform float base_blend_texture_alpha;
        uniform float alpha_reference;
        // Stage-zero D3DTSS_COLOROP as a multiplier: 1.0 for D3DTOP_MODULATE
        // (4), 2.0 for D3DTOP_MODULATE2X (5). Per draw, never a constant --
        // see RetailStageZeroColorOperation for the runtime reads that fix it.
        uniform float stage_zero_gain;
        uniform vec2 dot3_offset;
        uniform vec2 dot3_scale;
        uniform float reflection_factor_alpha;
        uniform vec2 overlay_offset;
        uniform vec2 overlay_scale;
        uniform float overlay_opacity;
        // D3DRS_AMBIENT and the two anti-parallel D3DLIGHT9 records, per draw
        // and never a level constant -- see RetailMeshLightRig for the device
        // reads at SetLight (0x005512e1) that fix them. sun_color is light 0's
        // Diffuse, anti_sun_color is light 1's, and sunlight_direction is light
        // 0's Direction mapped into Godot; light 1's Direction is its exact
        // negation on both measured rigs, which is why one vector serves both.
        // On the 442 CRTTree draws light 0 is the sun scaled by the shipped 0.1
        // at 0x005d85c0 and the axis is vertical, so the names describe the
        // static-world rig and the slots, not the tree rig's physical roles.
        uniform vec3 ambient_color;
        uniform vec3 sun_color;
        uniform vec3 anti_sun_color;
        uniform vec3 sunlight_direction;
        uniform vec3 fog_color;
        uniform float fog_density;
        uniform float maximum_horizontal_distance_squared;
        varying vec3 vertex_light_color;
        varying vec3 model_light_direction;
        varying vec2 reflection_uv;
        varying float horizontal_distance_squared;

        vec3 retail_output(vec3 color) {
            if (OUTPUT_IS_SRGB) {
                return color;
            }
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        vec3 apply_retail_fog(vec3 color, float view_depth) {
            float visibility = clamp(exp(-fog_density * view_depth), 0.0, 1.0);
            return mix(fog_color, color, visibility);
        }

        void vertex() {
            // MultiMesh instance position is available through MODEL_MATRIX
            // here, so carry its camera distance into the fragment stage.
            vec2 horizontal_offset =
                MODEL_MATRIX[3].xz - CAMERA_POSITION_WORLD.xz;
            horizontal_distance_squared = dot(
                horizontal_offset,
                horizontal_offset);
            vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
            float sun = max(dot(world_normal, -sunlight_direction), 0.0);
            float anti_sun = max(dot(world_normal, sunlight_direction), 0.0);
            vertex_light_color = ambient_color + (sun_color * sun) +
                (anti_sun_color * anti_sun);
            // Retail leaves D3DRS_LIGHTING on for the FVF 0x152 mesh draw and
            // sets D3DRS_DIFFUSEMATERIALSOURCE and D3DRS_AMBIENTMATERIALSOURCE
            // to D3DMCS_COLOR1 (D3DStateCache__UseDefaultRenderState,
            // 0x004EB1E0), leaving D3DRS_COLORVERTEX at its TRUE default. The
            // per-vertex DIFFUSE dword is therefore the diffuse and ambient
            // material reflectance for every term of the lighting equation, and
            // the lit result is stage-zero COLORARG2 = D3DTA_DIFFUSE.
            vertex_light_color *= COLOR.rgb;
            model_light_direction = normalize(
                transpose(mat3(MODEL_MATRIX)) * sunlight_direction);

            // D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR generates
            // 2(N.E)N-E per vertex. Steam then applies [.5,0;0,-.5]
            // and the (.5,.5) offset before interpolating the coordinates.
            vec3 view_position = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
            vec3 view_normal = normalize(MODELVIEW_NORMAL_MATRIX * NORMAL);
            vec3 eye = normalize(-view_position);
            vec3 reflection_vector =
                (2.0 * dot(view_normal, eye) * view_normal) - eye;
            reflection_uv = vec2(
                (reflection_vector.x * 0.5) + 0.5,
                (reflection_vector.y * -0.5) + 0.5);
        }

        void fragment() {
            if (maximum_horizontal_distance_squared >= 0.0 &&
                horizontal_distance_squared > maximum_horizontal_distance_squared) {
                discard;
            }
            // Steam's high static-world renderer applies a -1 mip bias to
            // hardware stage zero.
            vec4 texture_color = texture(base_texture, UV, -1.0);
            if (base_blend_texture_alpha < 0.5 && texture_color.a < alpha_reference) {
                discard;
            }
            // Stage zero is COLORARG1 = D3DTA_TEXTURE, COLORARG2 =
            // D3DTA_DIFFUSE, and COLOROP is whichever of MODULATE /
            // MODULATE2X the draw is under. Read out of the running safe copy
            // from the texture-stage-state shadow at 0x008557f4 (the setter at
            // 0x00513820 indexes it as (type + stage*0n30)*4 + 0x008557f0):
            // 5 = MODULATE2X on the 134 mode-0 static-world draws and the 442
            // CRTTree mesh draws of one frame, 4 = MODULATE on all seven
            // cockpit batches (16 reads inside the cockpit window, zero
            // transitions while inside it) and on the 19 mode-4 static-world
            // draws of that same frame. So the gain is per draw.
            vec3 retail_color = min(
                texture_color.rgb * vertex_light_color * stage_zero_gain,
                vec3(1.0));
            if (base_blend_texture_alpha > 0.5) {
                retail_color = mix(retail_color, texture_color.rgb, texture_color.a);
            }

            if (has_dot3 > 0.5) {
                vec3 dot3_sample = texture(
                    dot3_texture,
                    (UV * dot3_scale) + dot3_offset).rgb;
                vec3 encoded_light = round(clamp(
                    (model_light_direction * 127.0) + vec3(128.0),
                    vec3(0.0),
                    vec3(255.0))) / 255.0;
                float dot3_value = clamp(
                    4.0 * dot(dot3_sample - vec3(0.5), encoded_light - vec3(0.5)),
                    0.0,
                    1.0);
                retail_color = vec3(dot3_value);
            }

            if (has_reflection > 0.5) {
                // The reflection layer is another stage-zero world draw, and
                // it is a MODE-0 one: [0x00704e48], the RenderMeshCore mode
                // global, was read at every one of 4,393 mesh renders across
                // three launches and is 0 on 4,314 and 4 on 79 -- never 2,
                // never 6, never 8, and the mode-2/mode-6 draw calls at
                // 0x0054a423 / 0x0054a466 never fired at all. D3DRS_LIGHTING
                // ([0x00855764], the render-state shadow at 0x00855540 indexed
                // state*4) is 1 across all 576 world and tree draws, so the
                // layer is lit, which is what this branch already assumed. It
                // inherits stage zero's colour operation and sampler state;
                // stage one only scales its alpha with texture factor.
                vec4 reflection_color = texture(
                    reflection_texture,
                    reflection_uv,
                    -1.0);
                vec3 reflection_stage_color = min(
                    reflection_color.rgb * vertex_light_color * stage_zero_gain,
                    vec3(1.0));
                float reflection_alpha = clamp(
                    reflection_color.a * reflection_factor_alpha,
                    0.0,
                    1.0);
                retail_color = mix(
                    retail_color,
                    reflection_stage_color,
                    reflection_alpha);
            }

            if (has_overlay > 0.5) {
                vec4 overlay_color = texture(
                    overlay_texture,
                    (UV * overlay_scale) + overlay_offset);
                float overlay_alpha = clamp(
                    overlay_color.a * overlay_opacity,
                    0.0,
                    1.0);
                retail_color = mix(retail_color, overlay_color.rgb, overlay_alpha);
            }

            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
        }
        """;

    public static ShaderMaterial Create(
        Texture2D texture,
        LegacyLevel100HeightFieldReference terrain,
        LegacyRetailStageZeroColorOperation stageZeroColorOperation)
    {
        return Create(
            [
                new LegacyRetailTextureLayer(texture, 1f, Vector2.Zero, Vector2.One),
                null,
                null,
                null,
                null,
                null,
            ],
            terrain,
            stageZeroColorOperation: stageZeroColorOperation);
    }

    /// <param name="stageZeroColorOperation">
    /// The stage-zero <c>D3DTSS_COLOROP</c> this draw runs under. Retail's
    /// value varies by draw, so every call site states the one it measured;
    /// the default is the <c>MODULATE2X</c> read at the 134 mode-0
    /// static-world and 442 tree draws, which are the majority of the draws
    /// through this shader. See <see cref="LegacyRetailStageZeroColorOperation"/>.
    /// </param>
    /// <param name="lightRig">
    /// The <c>D3DRS_AMBIENT</c> and two-<c>D3DLIGHT9</c> rig this draw runs
    /// under. Retail's rig also varies by draw — the close pines run a
    /// different ambient, a 0.1x key light and a vertical light axis — so a
    /// call site that draws trees must say so. Omitting it keeps the
    /// static-world rig measured at the 130 mode-0 <c>CRTMesh</c> draws, which
    /// is the majority case and what every other call site through this shader
    /// was measured at. See <see cref="LegacyRetailMeshLightRig"/>.
    /// </param>
    public static ShaderMaterial Create(
        IReadOnlyList<LegacyRetailTextureLayer?> layers,
        LegacyLevel100HeightFieldReference terrain,
        float maximumHorizontalDistance = 0f,
        float alphaReference = 0.5f,
        LegacyRetailStageZeroColorOperation stageZeroColorOperation =
            LegacyRetailStageZeroColorOperation.Modulate2X,
        LegacyRetailMeshLightRig? lightRig = null)
    {
        if (layers.Count != 6 || layers[0] is not LegacyRetailTextureLayer baseLayer)
        {
            throw new InvalidDataException("Retail material requires one base layer and six exact slots.");
        }
        if (!float.IsFinite(maximumHorizontalDistance) || maximumHorizontalDistance < 0f)
        {
            throw new ArgumentOutOfRangeException(nameof(maximumHorizontalDistance));
        }
        if (!float.IsFinite(alphaReference) || alphaReference is < 0f or > 1f)
        {
            throw new ArgumentOutOfRangeException(nameof(alphaReference));
        }
        float stageZeroGain = StageZeroGain(stageZeroColorOperation);
        LegacyRetailTextureLayer? dot3Layer = layers[1];
        LegacyRetailTextureLayer? reflectionLayer = layers[2];
        LegacyRetailTextureLayer? overlayLayer = layers[4];
        var material = new ShaderMaterial
        {
            Shader = _objectShader ??= new Shader { Code = ShaderCode },
        };
        material.SetShaderParameter("base_texture", baseLayer.Texture);
        material.SetShaderParameter("dot3_texture", dot3Layer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("reflection_texture", reflectionLayer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("overlay_texture", overlayLayer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("has_dot3", dot3Layer is null ? 0f : 1f);
        material.SetShaderParameter("has_reflection", reflectionLayer is null ? 0f : 1f);
        material.SetShaderParameter("has_overlay", overlayLayer is null ? 0f : 1f);
        material.SetShaderParameter(
            "base_blend_texture_alpha",
            baseLayer.BlendTextureAlpha ? 1f : 0f);
        material.SetShaderParameter("alpha_reference", alphaReference);
        material.SetShaderParameter("stage_zero_gain", stageZeroGain);
        material.SetShaderParameter("dot3_offset", dot3Layer?.Offset ?? Vector2.Zero);
        material.SetShaderParameter("dot3_scale", dot3Layer?.Scale ?? Vector2.One);
        material.SetShaderParameter(
            "reflection_factor_alpha",
            ToTextureFactorAlpha(reflectionLayer?.Opacity ?? 0f));
        material.SetShaderParameter("overlay_offset", overlayLayer?.Offset ?? Vector2.Zero);
        material.SetShaderParameter("overlay_scale", overlayLayer?.Scale ?? Vector2.One);
        material.SetShaderParameter("overlay_opacity", overlayLayer?.Opacity ?? 0f);
        LegacyRetailMeshLightRig rig = lightRig ?? LegacyRetailMeshLightRig.StaticWorld(terrain);
        material.SetShaderParameter("ambient_color", rig.AmbientColor);
        material.SetShaderParameter("sun_color", rig.KeyLightColor);
        material.SetShaderParameter("anti_sun_color", rig.FillLightColor);
        material.SetShaderParameter("sunlight_direction", rig.KeyLightDirection);
        material.SetShaderParameter("fog_color", new Vector3(
            terrain.FogColor.R,
            terrain.FogColor.G,
            terrain.FogColor.B));
        material.SetShaderParameter("fog_density", terrain.FogDensity);
        material.SetShaderParameter(
            "maximum_horizontal_distance_squared",
            maximumHorizontalDistance > 0f
                ? maximumHorizontalDistance * maximumHorizontalDistance
                : -1f);
        return material;
    }

    /// <summary>
    /// The stage-zero colour operation as the multiplier the shader applies.
    /// <c>D3DTOP_MODULATE</c> is texture x diffuse and <c>D3DTOP_MODULATE2X</c>
    /// is that doubled, so these are exactly 1 and 2. Any other enumerant is
    /// refused rather than silently collapsed onto one of them: nothing has
    /// observed retail using one at these draws.
    /// </summary>
    private static float StageZeroGain(LegacyRetailStageZeroColorOperation operation) =>
        operation switch
        {
            LegacyRetailStageZeroColorOperation.Modulate => 1f,
            LegacyRetailStageZeroColorOperation.Modulate2X => 2f,
            _ => throw new ArgumentOutOfRangeException(nameof(operation)),
        };

    private static float ToTextureFactorAlpha(float strength)
    {
        int alpha = Math.Clamp(
            (int)MathF.Round(strength * byte.MaxValue, MidpointRounding.ToEven),
            byte.MinValue,
            byte.MaxValue);
        return alpha / (float)byte.MaxValue;
    }
}
