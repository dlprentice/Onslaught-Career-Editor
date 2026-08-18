// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// FEMessBox Create() arguments for the main-menu Quit confirm, recovered from
/// <c>CFEPMain__DoAction</c> <c>0x004623E0</c>–<c>0x00462618</c> in the
/// pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, SHA-256
/// <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para><b>The quit arm.</b> Selection 6 pushes localization id <c>0xE4</c>
/// at <c>0x004625D1</c>, then immediately before the Create call:</para>
/// <code>
/// 0x004625E1  push 0x3DCCCCCD   ; 0.1f — not claimed as a pixel height
/// 0x004625E6  push 400.0f
/// 0x004625EB  push 240.0f
/// 0x004625F0  push 320.0f
/// 0x004625F5  call Create
/// </code>
///
/// <para>The overwrite/save YESNO arm in the same body uses width 300.0f at
/// <c>0x004624BC</c>. Quit is the 400-wide Create. <c>FEPMessBox.cpp</c> is
/// absent from the GPL drop, so chrome tiles and pixel height stay unclaimed.
/// </para>
/// </summary>
public static class RetailFeMessBox
{
    /// <summary>Localization id for "Are you sure you want to quit the game?"</summary>
    public const int QuitLocalizationId = 0xE4;

    /// <summary>Create() X. Immediate at <c>0x004625F0</c>.</summary>
    public const float QuitCenterX = 320f;

    /// <summary>Create() Y. Immediate at <c>0x004625EB</c>.</summary>
    public const float QuitCenterY = 240f;

    /// <summary>Create() width. Immediate at <c>0x004625E6</c>.</summary>
    public const float QuitWidth = 400f;

    /// <summary>Left edge of a 400-wide box centred on <see cref="QuitCenterX"/>.</summary>
    public const float QuitLeft = QuitCenterX - (QuitWidth * 0.5f);
}
