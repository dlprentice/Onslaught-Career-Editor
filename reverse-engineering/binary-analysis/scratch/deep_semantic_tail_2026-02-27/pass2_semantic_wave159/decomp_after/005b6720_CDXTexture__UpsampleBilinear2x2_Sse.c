/* address: 0x005b6720 */
/* name: CDXTexture__UpsampleBilinear2x2_Sse */
/* signature: void __fastcall CDXTexture__UpsampleBilinear2x2_Sse(int param_1, int param_2, int param_3, int param_4) */


void __fastcall CDXTexture__UpsampleBilinear2x2_Sse(int param_1,int param_2,int param_3,int param_4)

{
  ulonglong uVar1;
  ulonglong uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  int iVar5;
  int iVar6;
  undefined8 uVar7;
  ulonglong uVar8;
  int iVar9;
  int iVar10;
  ulonglong *puVar11;
  undefined8 *puVar12;
  ulonglong *puVar13;
  short sVar14;
  short sVar15;
  short sVar16;
  ushort uVar17;
  ushort uVar18;
  ushort uVar19;
  ushort uVar20;
  ulonglong uVar21;
  ulonglong uVar22;
  ulonglong uVar23;
  ushort uVar24;
  ushort uVar25;
  ushort uVar26;
  ushort uVar27;
  ulonglong uVar28;

  iVar5 = *(int *)(param_1 + 0x1c);
  iVar6 = *(int *)(param_1 + 0xc);
  CDXTexture__Helper_005b6290(param_3,*(int *)(param_2 + 0xf4),*(int *)(param_2 + 0x1c),iVar5 << 4);
  uVar8 = DAT_005f4c10;
  iVar9 = 0;
  do {
    uVar7 = DAT_005f4c08;
    puVar12 = *(undefined8 **)(param_4 + iVar9 * 4);
    puVar13 = *(ulonglong **)(param_3 + iVar9 * 4);
    puVar11 = *(ulonglong **)(param_3 + (iVar9 + 1) * 4);
    iVar10 = iVar5 << 3;
    do {
      uVar1 = *puVar13;
      uVar2 = *puVar11;
      uVar21 = uVar1 & uVar8;
      uVar22 = uVar2 & uVar8;
      uVar3 = puVar13[1];
      uVar4 = puVar11[1];
      uVar28 = uVar3 & uVar8;
      uVar23 = uVar4 & uVar8;
      sVar14 = (short)((ulonglong)uVar7 >> 0x10);
      sVar15 = (short)((ulonglong)uVar7 >> 0x20);
      sVar16 = (short)((ulonglong)uVar7 >> 0x30);
      uVar17 = (ushort)(((ushort)uVar1 >> 8) + (short)uVar21 + (short)uVar22 + ((ushort)uVar2 >> 8)
                       + (short)uVar7) >> 2;
      uVar18 = (ushort)(((ushort)(uVar1 >> 0x10) >> 8) + (short)(uVar21 >> 0x10) +
                        (short)(uVar22 >> 0x10) + ((ushort)(uVar2 >> 0x10) >> 8) + sVar14) >> 2;
      uVar19 = (ushort)(((ushort)(uVar1 >> 0x20) >> 8) + (short)(uVar21 >> 0x20) +
                        (short)(uVar22 >> 0x20) + ((ushort)(uVar2 >> 0x20) >> 8) + sVar15) >> 2;
      uVar20 = (ushort)((ushort)(uVar1 >> 0x38) + (short)(uVar21 >> 0x30) +
                        (short)(uVar22 >> 0x30) + (ushort)(uVar2 >> 0x38) + sVar16) >> 2;
      uVar24 = (ushort)(((ushort)uVar3 >> 8) + (short)uVar28 + ((ushort)uVar4 >> 8) + (short)uVar23
                       + (short)uVar7) >> 2;
      uVar25 = (ushort)(((ushort)(uVar3 >> 0x10) >> 8) + (short)(uVar28 >> 0x10) +
                        ((ushort)(uVar4 >> 0x10) >> 8) + (short)(uVar23 >> 0x10) + sVar14) >> 2;
      uVar26 = (ushort)(((ushort)(uVar3 >> 0x20) >> 8) + (short)(uVar28 >> 0x20) +
                        ((ushort)(uVar4 >> 0x20) >> 8) + (short)(uVar23 >> 0x20) + sVar15) >> 2;
      uVar27 = (ushort)((ushort)(uVar3 >> 0x38) + (short)(uVar28 >> 0x30) +
                        (ushort)(uVar4 >> 0x38) + (short)(uVar23 >> 0x30) + sVar16) >> 2;
      puVar13 = puVar13 + 2;
      puVar11 = puVar11 + 2;
      iVar10 = iVar10 + -8;
      *puVar12 = CONCAT17((uVar27 != 0) * (uVar27 < 0x100) * (char)uVar27 - (0xff < uVar27),
                          CONCAT16((uVar26 != 0) * (uVar26 < 0x100) * (char)uVar26 - (0xff < uVar26)
                                   ,CONCAT15((uVar25 != 0) * (uVar25 < 0x100) * (char)uVar25 -
                                             (0xff < uVar25),
                                             CONCAT14((uVar24 != 0) * (uVar24 < 0x100) *
                                                      (char)uVar24 - (0xff < uVar24),
                                                      CONCAT13((uVar20 != 0) * (uVar20 < 0x100) *
                                                               (char)uVar20 - (0xff < uVar20),
                                                               CONCAT12((uVar19 != 0) *
                                                                        (uVar19 < 0x100) *
                                                                        (char)uVar19 -
                                                                        (0xff < uVar19),
                                                                        CONCAT11((uVar18 != 0) *
                                                                                 (uVar18 < 0x100) *
                                                                                 (char)uVar18 -
                                                                                 (0xff < uVar18),
                                                                                 (uVar17 != 0) *
                                                                                 (uVar17 < 0x100) *
                                                                                 (char)uVar17 -
                                                                                 (0xff < uVar17)))))
                                            )));
      puVar12 = puVar12 + 1;
    } while (7 < iVar10);
    iVar9 = iVar9 + 1;
  } while (iVar9 < iVar6);
  return;
}
