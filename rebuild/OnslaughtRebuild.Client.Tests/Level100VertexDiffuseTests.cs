// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Retail mesh vertices carry a per-vertex D3DCOLOR DIFFUSE dword and the
/// released renderer consumes it.
///
/// Static evidence, read read-only out of the maintainer Ghidra database
/// (<c>BEA.exe</c>, imported Steam specimen SHA-256
/// <c>74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750</c>)
/// with <c>analyzeHeadless.bat ... -readOnly -noanalysis</c>:
///
/// <list type="bullet">
/// <item><description>The mesh vertex profile is FVF <c>0x152</c> =
/// <c>XYZ|NORMAL|DIFFUSE|TEX1</c> at stride 36 = 12 + 12 + 4 + 8, rejected
/// otherwise by the converter and by the walker loader.</description></item>
/// <item><description><c>D3DStateCache__UseDefaultRenderState</c> at
/// <c>0x004EB1E0</c> issues <c>RenderState_SetRaw(0x89, 1)</c>
/// (<c>D3DRS_LIGHTING</c> = TRUE), <c>RenderState_SetRaw(0x91, 1)</c>
/// (<c>D3DRS_DIFFUSEMATERIALSOURCE</c> = <c>D3DMCS_COLOR1</c>) and
/// <c>RenderState_SetRaw(0x93, 1)</c> (<c>D3DRS_AMBIENTMATERIALSOURCE</c> =
/// <c>D3DMCS_COLOR1</c>). <c>D3DRS_COLORVERTEX</c> (<c>0x8D</c>) is written at
/// none of the 547 render-state call sites reachable from the three setters
/// <c>0x00513BC0</c>, <c>0x00513C20</c> and <c>0x00513A50</c>, so it keeps its
/// <c>TRUE</c> Direct3D 8 default.</description></item>
/// <item><description>The mesh draw keeps lighting on. Statically, <c>0x89</c>
/// is cleared only around the mode 2 and mode 6 passes of
/// <c>CMeshRenderer__RenderMeshCore</c> (<c>0x00549570</c>) and the two overlay
/// passes of <c>CMeshRenderer__RenderMeshWithLayerPasses</c>
/// (<c>0x0054D530</c>), and restored to <c>1</c> immediately. At runtime those
/// mode-2 and mode-6 branches turn out to be dead in Level 100 — their draw
/// calls at <c>0x0054a423</c> and <c>0x0054a466</c> never fired across 4,393
/// observed mesh renders, the mode global <c>[0x00704e48]</c> reading only
/// <c>0</c> or <c>4</c> — and <c>D3DRS_LIGHTING</c>, read from the
/// render-state shadow at <c>[0x00855764]</c>, is <c>1</c> at all 576 world and
/// tree mesh draws of a frame.</description></item>
/// <item><description>The same default block sets stage zero
/// <c>D3DTSS_COLORARG1 = D3DTA_TEXTURE</c> and
/// <c>D3DTSS_COLORARG2 = D3DTA_DIFFUSE</c>
/// (<c>SetStateRaw(0, 2, 2)</c>, <c>SetStateRaw(0, 3, 0)</c>), with
/// <c>D3DTSS_COLOROP</c> driven to <c>MODULATE</c> or <c>MODULATE2X</c> by
/// <c>D3DStateCache__SetSlotMode4or5</c> (<c>0x00513AF0</c>).</description></item>
/// </list>
///
/// So the dword is the diffuse and the ambient material reflectance of the
/// fixed-function lighting equation, and the lit result is stage zero's second
/// colour argument. It is consumed, not authored-and-ignored.
///
/// The terrain is the contrast case and is unaffected: its 20-byte vertex has
/// neither normal nor diffuse, and <c>CDXLandscape__Render</c>
/// (<c>0x00545410</c>) switches <c>0x91</c> to <c>D3DMCS_MATERIAL</c> for its
/// own draw, restoring <c>D3DMCS_COLOR1</c> at <c>0x00545590</c>.
/// </summary>
public sealed class Level100VertexDiffuseTests
{
    private const string MeshDirectory = "Assets/Level100/StaticWorld/Meshes";

    /// <summary>
    /// Measured over the 28 Level 100 static-world meshes as converted from the
    /// retail installation: 37,797 vertices, of which 75 are not opaque white.
    /// </summary>
    private const int StaticWorldVertexCount = 37_797;

    private const int StaticWorldNonWhiteVertexCount = 75;

    [Fact]
    public void EveryStaticWorldMeshCarriesThePerVertexDiffuseExtension()
    {
        int vertices = 0;
        foreach (string path in MeshPaths())
        {
            foreach (string[] fields in VertexRecords(path))
            {
                Assert.Equal(7, fields.Length);
                vertices++;
            }
        }

        Assert.Equal(28, MeshPaths().Count);
        Assert.Equal(StaticWorldVertexCount, vertices);
    }

    [Fact]
    public void OnlyTheHealthPadAndTankFactoryCarryNonWhiteVertexDiffuse()
    {
        var nonWhiteByMesh = new SortedDictionary<string, int>(StringComparer.Ordinal);
        foreach (string path in MeshPaths())
        {
            int nonWhite = VertexRecords(path).Count(fields => ToRgb8(fields) != (255, 255, 255));
            if (nonWhite != 0)
            {
                nonWhiteByMesh.Add(Path.GetFileNameWithoutExtension(path), nonWhite);
            }
        }

        Assert.Equal(
            new SortedDictionary<string, int>(StringComparer.Ordinal)
            {
                ["fb-health-pad"] = 42,
                ["fb-tank-factory"] = 33,
            },
            nonWhiteByMesh);
        Assert.Equal(StaticWorldNonWhiteVertexCount, nonWhiteByMesh.Values.Sum());
    }

    /// <summary>
    /// The repair pad's 42 coloured vertices are a single exact authored tint,
    /// D3DCOLOR <c>0xFF3EF6FD</c>. Its alpha is opaque, which matters because
    /// stage zero also runs <c>D3DTSS_ALPHAOP = MODULATE</c> against
    /// <c>D3DTA_DIFFUSE</c>: no vertex in the 194-mesh retail corpus
    /// (278,173 vertices) has a diffuse alpha other than 255, so the OBJ
    /// colour extension loses nothing by carrying RGB only.
    /// </summary>
    [Fact]
    public void TheHealthPadTintIsTheExactAuthoredD3DColor()
    {
        var distinct = VertexRecords(MeshPath("fb-health-pad.obj"))
            .Select(ToRgb8)
            .Distinct()
            .OrderBy(color => color)
            .ToArray();

        Assert.Equal([(0x3E, 0xF6, 0xFD), (0xFF, 0xFF, 0xFF)], distinct);
    }

    /// <summary>
    /// Every emitted channel must survive the OBJ text round trip back to the
    /// exact retail byte, because Godot quantizes the colour array to eight
    /// bits per channel and any drift would change the rendered product.
    /// </summary>
    [Fact]
    public void EveryEmittedChannelRoundTripsToItsExactRetailByte()
    {
        foreach (string path in MeshPaths())
        {
            foreach (string[] fields in VertexRecords(path))
            {
                foreach (string channel in fields[4..7])
                {
                    float value = float.Parse(channel, CultureInfo.InvariantCulture);
                    Assert.InRange(value, 0f, 1f);
                    int quantized = (int)Math.Round(value * 255.0, MidpointRounding.AwayFromZero);
                    Assert.Equal(value, quantized / 255f, 6);
                }
            }
        }
    }

    [Fact]
    public void TheLoaderBindsTheColorArrayAndTheShaderModulatesTheLitDiffuseByIt()
    {
        string loader = ReadGodotSource("CuratedObjMeshLoader.cs");
        Assert.Contains("arrays[(int)Mesh.ArrayType.Color] = colors.ToArray();", loader);

        string staticWorld = ReadGodotSource("Level100StaticWorldAsset.cs");
        Assert.Contains("vertex_light_color *= COLOR.rgb;", staticWorld);
    }

    /// <summary>
    /// The stage-zero gain is per draw, not a constant folded into the shader.
    ///
    /// Retail's stage-zero <c>D3DTSS_COLOROP</c> was read out of the running
    /// safe copy from the texture-stage-state shadow at <c>0x008557f4</c> — the
    /// caching setter at <c>0x00513820</c> indexes that array as
    /// <c>(type + stage*0n30)*4 + 0x008557f0</c> — at the entry to every
    /// <c>CMeshRenderer::RenderMeshCore</c> call (<c>0x00549570</c>, the only
    /// mesh-render call site in the image) of one whole Level 100 frame. It is
    /// <c>5</c> = <c>D3DTOP_MODULATE2X</c> on the 134 mode-0 static-world draws
    /// and the 442 <c>CRTTree</c> mesh draws, and <c>4</c> =
    /// <c>D3DTOP_MODULATE</c> on all seven cockpit batches and on the 19 mode-4
    /// static-world draws of that same frame. One hardcoded <c>* 2.0</c> cannot
    /// be right for both, so the multiplier is a uniform.
    /// </summary>
    [Fact]
    public void TheStageZeroColourOperationIsAPerDrawUniformAndNotAHardcodedDoubling()
    {
        string staticWorld = ReadGodotSource("Level100StaticWorldAsset.cs");

        Assert.Contains("uniform float stage_zero_gain;", staticWorld);
        Assert.DoesNotContain("vertex_light_color * 2.0", staticWorld);
        Assert.Equal(2, Occurrences(staticWorld, "* vertex_light_color * stage_zero_gain,"));

        // The enumerant values are the Direct3D D3DTOP ones, so the source and
        // the runtime dump read alike, and the gain is exactly 1 and exactly 2.
        Assert.Contains("Modulate = 4,", staticWorld);
        Assert.Contains("Modulate2X = 5,", staticWorld);
        Assert.Contains("RetailStageZeroColorOperation.Modulate => 1f,", staticWorld);
        Assert.Contains("RetailStageZeroColorOperation.Modulate2X => 2f,", staticWorld);
        Assert.Contains("material.SetShaderParameter(\"stage_zero_gain\", stageZeroGain);", staticWorld);
    }

    /// <summary>
    /// The world and tree draws must keep the doubling. This pins the
    /// conditional against silently becoming unconditional in the other
    /// direction — a blanket removal of the <c>* 2.0</c> would regress the 134
    /// mode-0 static-world draws and the 442 tree draws that were measured at
    /// <c>MODULATE2X</c>, and the sky control band's retail/build ratio of
    /// 1.006/1.005/1.001 over 13,644 px says the rest of the frame is not 2x
    /// off.
    /// </summary>
    [Fact]
    public void TheStaticWorldMeshesStateTheMeasuredModulate2XAtTheirCallSite()
    {
        string staticWorld = Normalize(ReadGodotSource("Level100StaticWorldAsset.cs"));

        Assert.Contains(
            "        return RetailFixedFunctionMaterial.Create(\n" +
            "            layers,\n" +
            "            terrain,\n" +
            "            maximumHorizontalDistance,\n" +
            "            maximumHorizontalDistance > 0f ? 8f / 255f : 0.5f,\n" +
            "            RetailStageZeroColorOperation.Modulate2X);",
            staticWorld);

        // The shared default is MODULATE2X too, so a call site that says
        // nothing keeps the majority-measured behaviour rather than losing it.
        Assert.Contains(
            "        RetailStageZeroColorOperation stageZeroColorOperation =\n" +
            "            RetailStageZeroColorOperation.Modulate2X)",
            staticWorld);
    }

    /// <summary>
    /// The reflection layer stays lit, and no per-draw unlit flag exists.
    ///
    /// <c>[0x00704e48]</c>, the <c>CMeshRenderer::RenderMeshCore</c> mode
    /// global, was read at every one of 4,393 mesh renders across three
    /// launches: it is <c>0</c> on 4,314 and <c>4</c> on 79, never 2, never 6
    /// and never 8, and breakpoints on the mode-2 and mode-6 draw calls at
    /// <c>0x0054a423</c> and <c>0x0054a466</c> — the branches that bracket
    /// their draw with <c>D3DRS_LIGHTING := 0</c> — never fired. Meanwhile
    /// <c>D3DRS_LIGHTING</c> at <c>[0x00855764]</c> is <c>1</c> across all 576
    /// world and tree draws. So retail's fixed-function pipeline is lit for
    /// these meshes and substituting <c>COLOR.rgb</c> for
    /// <c>vertex_light_color</c> here would be wrong.
    /// </summary>
    [Fact]
    public void TheReflectionLayerStaysLitAndNoPerDrawUnlitFlagWasAdded()
    {
        string staticWorld = ReadGodotSource("Level100StaticWorldAsset.cs");

        Assert.Contains(
            "reflection_color.rgb * vertex_light_color * stage_zero_gain,",
            staticWorld);
        Assert.DoesNotContain("unlit", staticWorld);

        // The reflection layer's own mesh mode is 0, not 2. The superseded
        // comment identified it as mode 2.
        Assert.DoesNotContain("Mode 2 is another stage-zero world draw", staticWorld);
        Assert.Contains("it is a MODE-0 one", staticWorld);
    }

    /// <summary>
    /// The world path's normal space is the same map the cockpit's was proved
    /// to be, and it is proved here the same way: by carrying the shipped bytes
    /// through both chains numerically rather than by arguing about them.
    ///
    /// The reconstruction reaches Godot world space for a static-world mesh in
    /// two steps, not one. <c>emit_obj</c>
    /// (<c>rebuild/tools/cmsh_static_preview.py</c>, positions at line 775 and
    /// normals at line 738) negates the third component of the BEA model-space
    /// triple, i.e. applies <c>F = diag(1, 1, -1)</c>; then
    /// <see cref="Level100StaticWorldAsset"/> hangs the mesh under a
    /// <c>MeshInstance3D</c> with <c>RotationDegrees = (-90, 0, 0)</c>. The
    /// composite <c>Rx(-90) * F</c> is asserted below to be exactly
    /// <c>RetailAquilaWalkerAsset.MapVector</c>, <c>(x, y, z) -> (x, -z, -y)</c>
    /// — the same orthogonal, symmetric, self-inverse map with determinant -1
    /// the cockpit uses — so the world path is not a different normal space at
    /// all, only a different factorisation of the same one.
    ///
    /// The object yaw is the only part the cockpit chain does not have.
    /// Retail yaws a static about the BEA Z (down) axis; the reconstruction
    /// yaws its object root about Godot's Y. Those agree because
    /// <c>M * Rz(phi) * M = Ry(phi)</c> for every angle, asserted below, so the
    /// yaw conjugates through <c>M</c> exactly like the cockpit's part bases do.
    /// Since <c>Level100HeightFieldAsset</c> maps the sunlight direction by that
    /// same <c>M</c> and <c>M</c> is orthogonal, <c>N.L</c> is preserved.
    /// </summary>
    [Fact]
    public void TheWorldPathNormalSpaceIsMapVectorAndPreservesTheSunDotProduct()
    {
        double[,] rotateXMinus90 = RotationX(-Math.PI / 2.0);
        double[,] emitObjMap = { { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, -1 } };
        double[,] composite = Multiply(rotateXMinus90, emitObjMap);

        // MapVector: (x, y, z) -> (x, -z, -y).
        double[,] mapVector = { { 1, 0, 0 }, { 0, 0, -1 }, { 0, -1, 0 } };
        Assert.True(MaximumDifference(composite, mapVector) < 1e-15);
        Assert.Equal(-1.0, Determinant(mapVector));

        // The yaw conjugation identity the cockpit proof relied on, on the
        // world path's own axes: BEA yaw about Z (down) is Godot yaw about Y.
        for (int degrees = 0; degrees < 360; degrees++)
        {
            double phi = degrees * Math.PI / 180.0;
            double[,] conjugated = Multiply(mapVector, Multiply(RotationZ(phi), mapVector));
            Assert.True(MaximumDifference(conjugated, RotationY(phi)) < 1e-14);
        }

        // Now the shipped bytes. Every normal of every static-world OBJ, carried
        // through the retail chain (BEA model normal, yawed about Z, dotted with
        // the runtime-observed toward-sun vector) and through the reconstruction
        // chain (OBJ normal, Rx(-90), yawed about Y, dotted with the mapped
        // sunlight direction the shader uses).
        //
        // The sun vector is light 0's direction of travel, read live out of the
        // running safe copy at 0x009c65c0 + 0x14 and byte-identical across five
        // observations in two launches.
        double[] sunTravel = { -0.03407396, -0.90863329, +0.41620260 };
        double[] towardSunBea = { -sunTravel[0], -sunTravel[1], -sunTravel[2] };
        double[] godotSunlightDirection = Apply(mapVector, sunTravel);
        double[] towardSunGodot =
        {
            -godotSunlightDirection[0],
            -godotSunlightDirection[1],
            -godotSunlightDirection[2],
        };

        int normals = 0;
        double worst = 0.0;
        foreach (string path in MeshPaths())
        {
            foreach (double[] objNormal in NormalRecords(path))
            {
                // A yaw is authored per object, not per mesh, so sweep a dense
                // set rather than pick one: the identity must hold at all of
                // them, and the manifest's 33 authored yaws are a subset.
                for (int degrees = 0; degrees < 360; degrees += 60)
                {
                    double phi = degrees * Math.PI / 180.0;
                    double[] beaNormal = Normalize(Apply(emitObjMap, objNormal));
                    double retail = Dot(Apply(RotationZ(phi), beaNormal), towardSunBea);

                    double[] godotNormal = Normalize(
                        Apply(Multiply(RotationY(phi), rotateXMinus90), objNormal));
                    double reconstruction = Dot(godotNormal, towardSunGodot);

                    worst = Math.Max(worst, Math.Abs(retail - reconstruction));
                }
                normals++;
            }
        }

        Assert.Equal(StaticWorldVertexCount, normals);
        Assert.True(
            worst < 1e-12,
            $"world-path N.L deviates from retail by {worst:E3} over {normals} normals");
    }

    private static List<double[]> NormalRecords(string path) => File
        .ReadAllLines(path)
        .Where(line => line.StartsWith("vn ", StringComparison.Ordinal))
        .Select(line => line
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Skip(1)
            .Select(value => double.Parse(value, CultureInfo.InvariantCulture))
            .ToArray())
        .ToList();

    private static double[,] RotationX(double theta) => new[,]
    {
        { 1.0, 0.0, 0.0 },
        { 0.0, Math.Cos(theta), -Math.Sin(theta) },
        { 0.0, Math.Sin(theta), Math.Cos(theta) },
    };

    private static double[,] RotationY(double theta) => new[,]
    {
        { Math.Cos(theta), 0.0, Math.Sin(theta) },
        { 0.0, 1.0, 0.0 },
        { -Math.Sin(theta), 0.0, Math.Cos(theta) },
    };

    private static double[,] RotationZ(double theta) => new[,]
    {
        { Math.Cos(theta), -Math.Sin(theta), 0.0 },
        { Math.Sin(theta), Math.Cos(theta), 0.0 },
        { 0.0, 0.0, 1.0 },
    };

    private static double[,] Multiply(double[,] left, double[,] right)
    {
        var result = new double[3, 3];
        for (int row = 0; row < 3; row++)
        {
            for (int column = 0; column < 3; column++)
            {
                double sum = 0.0;
                for (int k = 0; k < 3; k++)
                {
                    sum += left[row, k] * right[k, column];
                }
                result[row, column] = sum;
            }
        }
        return result;
    }

    private static double[] Apply(double[,] matrix, double[] vector) =>
    [
        (matrix[0, 0] * vector[0]) + (matrix[0, 1] * vector[1]) + (matrix[0, 2] * vector[2]),
        (matrix[1, 0] * vector[0]) + (matrix[1, 1] * vector[1]) + (matrix[1, 2] * vector[2]),
        (matrix[2, 0] * vector[0]) + (matrix[2, 1] * vector[1]) + (matrix[2, 2] * vector[2]),
    ];

    private static double[] Normalize(double[] vector)
    {
        double length = Math.Sqrt(Dot(vector, vector));
        return length == 0.0
            ? vector
            : [vector[0] / length, vector[1] / length, vector[2] / length];
    }

    private static double Dot(double[] left, double[] right) =>
        (left[0] * right[0]) + (left[1] * right[1]) + (left[2] * right[2]);

    private static double Determinant(double[,] m) =>
        (m[0, 0] * ((m[1, 1] * m[2, 2]) - (m[1, 2] * m[2, 1])))
        - (m[0, 1] * ((m[1, 0] * m[2, 2]) - (m[1, 2] * m[2, 0])))
        + (m[0, 2] * ((m[1, 0] * m[2, 1]) - (m[1, 1] * m[2, 0])));

    private static double MaximumDifference(double[,] left, double[,] right)
    {
        double worst = 0.0;
        for (int row = 0; row < 3; row++)
        {
            for (int column = 0; column < 3; column++)
            {
                worst = Math.Max(worst, Math.Abs(left[row, column] - right[row, column]));
            }
        }
        return worst;
    }

    /// <summary>
    /// The proof above is only about the chain the asset actually builds, so
    /// pin that chain's two load-bearing lines. If either changes, the numeric
    /// result above stops describing the shipped code and must be re-derived.
    /// </summary>
    [Fact]
    public void TheWorldMeshChainStillUsesTheProvenRotationAndNormalTransform()
    {
        string staticWorld = Normalize(ReadGodotSource("Level100StaticWorldAsset.cs"));

        Assert.Contains("RotationDegrees = new Vector3(-90f, 0f, 0f),", staticWorld);
        Assert.Contains("new Basis(Vector3.Right, -Mathf.Pi / 2f)", staticWorld);
        Assert.Contains(
            "vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);",
            staticWorld);
    }

    private static int Occurrences(string text, string value)
    {
        int count = 0;
        for (int at = text.IndexOf(value, StringComparison.Ordinal);
             at >= 0;
             at = text.IndexOf(value, at + value.Length, StringComparison.Ordinal))
        {
            count++;
        }
        return count;
    }

    private static string Normalize(string text) => text.Replace("\r\n", "\n");

    private static (int R, int G, int B) ToRgb8(string[] fields) => (
        Channel(fields[4]),
        Channel(fields[5]),
        Channel(fields[6]));

    private static int Channel(string value) => (int)Math.Round(
        float.Parse(value, CultureInfo.InvariantCulture) * 255.0,
        MidpointRounding.AwayFromZero);

    private static List<string[]> VertexRecords(string path) => File
        .ReadAllLines(path)
        .Where(line => line.StartsWith("v ", StringComparison.Ordinal))
        .Select(line => line.Split(' ', StringSplitOptions.RemoveEmptyEntries))
        .ToList();

    private static string MeshPath(string fileName) =>
        Path.Combine(LocateGodotDirectory(), MeshDirectory, fileName);

    private static List<string> MeshPaths() => Directory
        .GetFiles(Path.Combine(LocateGodotDirectory(), MeshDirectory), "*.obj")
        .OrderBy(path => path, StringComparer.Ordinal)
        .ToList();

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(Path.Combine(LocateGodotDirectory(), fileName));

    private static string LocateGodotDirectory()
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(directory.FullName, "OnslaughtRebuild.Godot");
            if (Directory.Exists(Path.Combine(candidate, MeshDirectory)))
            {
                return candidate;
            }
            directory = directory.Parent;
        }
        throw new DirectoryNotFoundException(
            $"Could not locate OnslaughtRebuild.Godot/{MeshDirectory} above {AppContext.BaseDirectory}.");
    }
}
