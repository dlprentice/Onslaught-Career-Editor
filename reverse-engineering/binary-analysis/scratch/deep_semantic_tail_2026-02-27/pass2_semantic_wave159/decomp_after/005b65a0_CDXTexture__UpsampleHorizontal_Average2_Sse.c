/* address: 0x005b65a0 */
/* name: CDXTexture__UpsampleHorizontal_Average2_Sse */
/* signature: void __fastcall CDXTexture__UpsampleHorizontal_Average2_Sse(int param_1, int param_2, int param_3, int param_4) */


void __fastcall
CDXTexture__UpsampleHorizontal_Average2_Sse(int param_1,int param_2,int param_3,int param_4)

{
  ulonglong uVar1;
  ulonglong uVar2;
  int iVar3;
  int iVar4;
  undefined8 uVar5;
  ulonglong uVar6;
  int iVar7;
  int iVar8;
  undefined8 *puVar9;
  ulonglong *puVar10;
  short sVar11;
  short sVar12;
  short sVar13;
  ushort uVar14;
  ushort uVar15;
  ushort uVar16;
  ushort uVar17;
  ulonglong uVar18;
  ushort uVar19;
  ushort uVar20;
  ushort uVar21;
  ushort uVar22;
  ulonglong uVar23;

  iVar3 = *(int *)(param_1 + 0x1c);
  iVar4 = *(int *)(param_1 + 0xc);
  CDXTexture__Helper_005b6290(param_3,*(int *)(param_2 + 0xf4),*(int *)(param_2 + 0x1c),iVar3 << 4);
  uVar6 = DAT_005f4c00;
  iVar7 = 0;
  do {
    uVar5 = DAT_005f4bf0;
    puVar9 = *(undefined8 **)(param_4 + iVar7 * 4);
    puVar10 = *(ulonglong **)(param_3 + iVar7 * 4);
    iVar8 = iVar3 << 3;
    do {
      uVar1 = *puVar10;
      uVar2 = puVar10[1];
      uVar18 = uVar1 & uVar6;
      uVar23 = uVar2 & uVar6;
      sVar11 = (short)((ulonglong)uVar5 >> 0x10);
      sVar12 = (short)((ulonglong)uVar5 >> 0x20);
      sVar13 = (short)((ulonglong)uVar5 >> 0x30);
      uVar14 = (ushort)(((ushort)uVar1 >> 8) + (short)uVar18 + (short)uVar5) >> 1;
      uVar15 = (ushort)(((ushort)(uVar1 >> 0x10) >> 8) + (short)(uVar18 >> 0x10) + sVar11) >> 1;
      uVar16 = (ushort)(((ushort)(uVar1 >> 0x20) >> 8) + (short)(uVar18 >> 0x20) + sVar12) >> 1;
      uVar17 = (ushort)((ushort)(uVar1 >> 0x38) + (short)(uVar18 >> 0x30) + sVar13) >> 1;
      uVar19 = (ushort)(((ushort)uVar2 >> 8) + (short)uVar23 + (short)uVar5) >> 1;
      uVar20 = (ushort)(((ushort)(uVar2 >> 0x10) >> 8) + (short)(uVar23 >> 0x10) + sVar11) >> 1;
      uVar21 = (ushort)(((ushort)(uVar2 >> 0x20) >> 8) + (short)(uVar23 >> 0x20) + sVar12) >> 1;
      uVar22 = (ushort)((ushort)(uVar2 >> 0x38) + (short)(uVar23 >> 0x30) + sVar13) >> 1;
      iVar8 = iVar8 + -8;
      puVar10 = puVar10 + 2;
      *puVar9 = CONCAT17((uVar22 != 0) * (uVar22 < 0x100) * (char)uVar22 - (0xff < uVar22),
                         CONCAT16((uVar21 != 0) * (uVar21 < 0x100) * (char)uVar21 - (0xff < uVar21),
                                  CONCAT15((uVar20 != 0) * (uVar20 < 0x100) * (char)uVar20 -
                                           (0xff < uVar20),
                                           CONCAT14((uVar19 != 0) * (uVar19 < 0x100) * (char)uVar19
                                                    - (0xff < uVar19),
                                                    CONCAT13((uVar17 != 0) * (uVar17 < 0x100) *
                                                             (char)uVar17 - (0xff < uVar17),
                                                             CONCAT12((uVar16 != 0) *
                                                                      (uVar16 < 0x100) *
                                                                      (char)uVar16 - (0xff < uVar16)
                                                                      ,CONCAT11((uVar15 != 0) *
                                                                                (uVar15 < 0x100) *
                                                                                (char)uVar15 -
                                                                                (0xff < uVar15),
                                                                                (uVar14 != 0) *
                                                                                (uVar14 < 0x100) *
                                                                                (char)uVar14 -
                                                                                (0xff < uVar14))))))
                                 ));
      puVar9 = puVar9 + 1;
    } while (7 < iVar8);
    iVar7 = iVar7 + 1;
  } while (iVar7 < iVar4);
  return;
}
