/* address: 0x005aebb0 */
/* name: CDXTexture__UpsampleAndConvertYccToRgb_Mmx */
/* signature: void __thiscall CDXTexture__UpsampleAndConvertYccToRgb_Mmx(void * this, int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UpsampleAndConvertYccToRgb_Mmx(void *this,int param_1,int param_2,int param_3)

{
  ulonglong uVar1;
  ulonglong uVar2;
  int iVar3;
  ulonglong *puVar4;
  undefined8 *puVar5;
  short sVar6;
  undefined8 *puVar8;
  int iVar9;
  int *in_EAX;
  int *piVar10;
  int iVar11;
  int iVar12;
  byte bVar15;
  short sVar13;
  short sVar14;
  byte bVar16;
  byte bVar19;
  short sVar17;
  short sVar18;
  short sVar20;
  short sVar21;
  short sVar22;
  byte bVar24;
  byte bVar25;
  short sVar23;
  ushort uVar26;
  ushort uVar27;
  ushort uVar28;
  ushort uVar29;
  ushort uVar30;
  ushort uVar31;
  byte bVar33;
  ushort uVar32;
  byte bVar34;
  ushort uVar35;
  byte bVar36;
  ulonglong uVar37;
  short sVar7;

  iVar3 = *(int *)((int)this + 0x28);
  piVar10 = (int *)*in_EAX;
  iVar11 = 0;
  if (0 < *(int *)(param_1 + 0x13c)) {
    iVar12 = param_2 - (int)piVar10;
    do {
      puVar4 = *(ulonglong **)(iVar12 + (int)piVar10);
      puVar5 = (undefined8 *)*piVar10;
      uVar1 = *puVar4;
      bVar19 = (byte)(uVar1 >> 0x18);
      bVar16 = (byte)(uVar1 >> 0x10);
      uVar27 = (ushort)(((uint7)bVar19 << 0x30) >> 0x28);
      bVar15 = (byte)(uVar1 >> 8);
      sVar13 = (ushort)(byte)uVar1 * (short)DAT_005f49d0;
      sVar17 = (ushort)bVar15 * (short)((ulonglong)DAT_005f49d0 >> 0x10);
      sVar20 = (short)CONCAT21(uVar27,bVar16) * (short)((ulonglong)DAT_005f49d0 >> 0x20);
      sVar22 = (uVar27 >> 8) * (short)((ulonglong)DAT_005f49d0 >> 0x30);
      uVar37 = uVar1 & _DAT_005f4a18;
      uVar30 = (ushort)(((uint7)(byte)(bVar16 + (char)(uVar37 >> 0x18)) << 0x30) >> 0x28);
      bVar33 = (byte)(uVar1 >> 0x20);
      uVar27 = (ushort)(((uint7)bVar33 << 0x30) >> 0x28);
      uVar26 = (ushort)(byte)uVar37 + sVar13 + (short)DAT_005f4a00;
      uVar28 = (ushort)(byte)((byte)uVar1 + (char)(uVar37 >> 8)) + sVar17 +
               (short)((ulonglong)DAT_005f4a00 >> 0x10);
      uVar29 = (short)CONCAT21(uVar30,bVar15 + (char)(uVar37 >> 0x10)) + sVar20 +
               (short)((ulonglong)DAT_005f4a00 >> 0x20);
      uVar30 = (uVar30 >> 8) + sVar22 + (short)((ulonglong)DAT_005f4a00 >> 0x30);
      uVar31 = (ushort)bVar15 + sVar13 + (short)DAT_005f4a08;
      uVar32 = (ushort)bVar16 + sVar17 + (short)((ulonglong)DAT_005f4a08 >> 0x10);
      uVar35 = (short)CONCAT21(uVar27,bVar19) + sVar20 + (short)((ulonglong)DAT_005f4a08 >> 0x20);
      *puVar5 = CONCAT17((char)((ushort)((uVar27 >> 8) + sVar22 +
                                        (short)((ulonglong)DAT_005f4a08 >> 0x30)) >> 2) +
                         (byte)(uVar30 >> 10),
                         CONCAT16((byte)(uVar35 >> 10) + (char)(uVar30 >> 2),
                                  CONCAT15((char)(uVar35 >> 2) + (byte)(uVar29 >> 10),
                                           CONCAT14((byte)(uVar32 >> 10) + (char)(uVar29 >> 2),
                                                    CONCAT13((char)(uVar32 >> 2) +
                                                             (byte)(uVar28 >> 10),
                                                             CONCAT12((byte)(uVar31 >> 10) +
                                                                      (char)(uVar28 >> 2),
                                                                      CONCAT11((char)(uVar31 >> 2) +
                                                                               (byte)(uVar26 >> 10),
                                                                               (char)(uVar26 >> 2)))
                                                            )))));
      bVar15 = (byte)(uVar1 >> 0x28);
      bVar16 = (byte)(uVar1 >> 0x30);
      bVar24 = (byte)(uVar1 >> 0x38);
      sVar13 = (ushort)bVar33 * (short)DAT_005f49d0;
      sVar17 = (ushort)bVar15 * (short)((ulonglong)DAT_005f49d0 >> 0x10);
      sVar20 = (ushort)bVar16 * (short)((ulonglong)DAT_005f49d0 >> 0x20);
      sVar22 = (ushort)bVar24 * (short)((ulonglong)DAT_005f49d0 >> 0x30);
      uVar37 = puVar4[1];
      uVar27 = (ushort)bVar19 + sVar13 + (short)DAT_005f4a00;
      uVar30 = (ushort)bVar33 + sVar17 + (short)((ulonglong)DAT_005f4a00 >> 0x10);
      uVar26 = (ushort)bVar15 + sVar20 + (short)((ulonglong)DAT_005f4a00 >> 0x20);
      uVar28 = (ushort)bVar16 + sVar22 + (short)((ulonglong)DAT_005f4a00 >> 0x30);
      uVar29 = (ushort)bVar15 + sVar13 + (short)DAT_005f4a08;
      uVar31 = (ushort)bVar16 + sVar17 + (short)((ulonglong)DAT_005f4a08 >> 0x10);
      uVar32 = (ushort)bVar24 + sVar20 + (short)((ulonglong)DAT_005f4a08 >> 0x20);
      puVar5[1] = CONCAT17((char)((ushort)((ushort)(byte)uVar37 + sVar22 +
                                          (short)((ulonglong)DAT_005f4a08 >> 0x30)) >> 2) +
                           (byte)(uVar28 >> 10),
                           CONCAT16((byte)(uVar32 >> 10) + (char)(uVar28 >> 2),
                                    CONCAT15((char)(uVar32 >> 2) + (byte)(uVar26 >> 10),
                                             CONCAT14((byte)(uVar31 >> 10) + (char)(uVar26 >> 2),
                                                      CONCAT13((char)(uVar31 >> 2) +
                                                               (byte)(uVar30 >> 10),
                                                               CONCAT12((byte)(uVar29 >> 10) +
                                                                        (char)(uVar30 >> 2),
                                                                        CONCAT11((char)(uVar29 >> 2)
                                                                                 + (byte)(uVar27 >>
                                                                                         10),
                                                                                 (char)(uVar27 >> 2)
                                                                                )))))));
      iVar9 = iVar3;
      while( true ) {
        iVar9 = iVar9 + -8;
        puVar8 = puVar5 + 2;
        bVar15 = (byte)(uVar37 >> 8);
        bVar16 = (byte)(uVar37 >> 0x10);
        bVar19 = (byte)(uVar37 >> 0x18);
        bVar34 = (byte)(uVar37 >> 0x20);
        bVar24 = (byte)(uVar37 >> 0x28);
        bVar33 = (byte)(uVar37 >> 0x30);
        bVar25 = (byte)(uVar37 >> 0x38);
        uVar27 = (ushort)(uVar37 >> 8);
        sVar18 = (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar21 = (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar23 = (short)((ulonglong)DAT_005f49d0 >> 0x30);
        bVar36 = (byte)(uVar1 >> 0x38);
        sVar13 = (short)((ulonglong)DAT_005f4a00 >> 0x10);
        sVar20 = (short)((ulonglong)DAT_005f4a00 >> 0x20);
        sVar6 = (short)((ulonglong)DAT_005f4a00 >> 0x30);
        sVar17 = (short)((ulonglong)DAT_005f4a08 >> 0x10);
        sVar22 = (short)((ulonglong)DAT_005f4a08 >> 0x20);
        sVar7 = (short)((ulonglong)DAT_005f4a08 >> 0x30);
        if (iVar9 < 9) break;
        uVar30 = (ushort)(((uint7)bVar19 << 0x30) >> 0x28);
        sVar14 = ((ushort)uVar37 & 0xff) * (short)DAT_005f49d0;
        sVar18 = (ushort)bVar15 * sVar18;
        sVar21 = (short)CONCAT21(uVar30,bVar16) * sVar21;
        sVar23 = (uVar30 >> 8) * sVar23;
        uVar26 = (ushort)(((uint7)bVar16 << 0x30) >> 0x28);
        uVar30 = (ushort)(((uint7)bVar34 << 0x30) >> 0x28);
        uVar28 = (ushort)bVar36 + sVar14 + (short)DAT_005f4a00;
        uVar29 = (ushort)(byte)uVar37 + sVar18 + sVar13;
        uVar31 = (short)CONCAT21(uVar26,bVar15) + sVar21 + sVar20;
        uVar26 = (uVar26 >> 8) + sVar23 + sVar6;
        uVar27 = (uVar27 & 0xff) + sVar14 + (short)DAT_005f4a08;
        uVar32 = (ushort)bVar16 + sVar18 + sVar17;
        uVar35 = (short)CONCAT21(uVar30,bVar19) + sVar21 + sVar22;
        *puVar8 = CONCAT17((char)((ushort)((uVar30 >> 8) + sVar23 + sVar7) >> 2) +
                           (byte)(uVar26 >> 10),
                           CONCAT16((byte)(uVar35 >> 10) + (char)(uVar26 >> 2),
                                    CONCAT15((char)(uVar35 >> 2) + (byte)(uVar31 >> 10),
                                             CONCAT14((byte)(uVar32 >> 10) + (char)(uVar31 >> 2),
                                                      CONCAT13((char)(uVar32 >> 2) +
                                                               (byte)(uVar29 >> 10),
                                                               CONCAT12((byte)(uVar27 >> 10) +
                                                                        (char)(uVar29 >> 2),
                                                                        CONCAT11((char)(uVar27 >> 2)
                                                                                 + (byte)(uVar28 >>
                                                                                         10),
                                                                                 (char)(uVar28 >> 2)
                                                                                )))))));
        sVar13 = (ushort)bVar34 * (short)DAT_005f49d0;
        sVar17 = (ushort)bVar24 * (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar20 = (ushort)bVar33 * (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar22 = (ushort)bVar25 * (short)((ulonglong)DAT_005f49d0 >> 0x30);
        uVar2 = puVar4[2];
        uVar27 = (ushort)bVar19 + sVar13 + (short)DAT_005f4a00;
        uVar30 = (ushort)bVar34 + sVar17 + (short)((ulonglong)DAT_005f4a00 >> 0x10);
        uVar26 = (ushort)bVar24 + sVar20 + (short)((ulonglong)DAT_005f4a00 >> 0x20);
        uVar28 = (ushort)bVar33 + sVar22 + (short)((ulonglong)DAT_005f4a00 >> 0x30);
        uVar29 = (ushort)bVar24 + sVar13 + (short)DAT_005f4a08;
        uVar31 = (ushort)bVar33 + sVar17 + (short)((ulonglong)DAT_005f4a08 >> 0x10);
        uVar32 = (ushort)bVar25 + sVar20 + (short)((ulonglong)DAT_005f4a08 >> 0x20);
        puVar5[3] = CONCAT17((char)((ushort)((ushort)(byte)uVar2 + sVar22 +
                                            (short)((ulonglong)DAT_005f4a08 >> 0x30)) >> 2) +
                             (byte)(uVar28 >> 10),
                             CONCAT16((byte)(uVar32 >> 10) + (char)(uVar28 >> 2),
                                      CONCAT15((char)(uVar32 >> 2) + (byte)(uVar26 >> 10),
                                               CONCAT14((byte)(uVar31 >> 10) + (char)(uVar26 >> 2),
                                                        CONCAT13((char)(uVar31 >> 2) +
                                                                 (byte)(uVar30 >> 10),
                                                                 CONCAT12((byte)(uVar29 >> 10) +
                                                                          (char)(uVar30 >> 2),
                                                                          CONCAT11((char)(uVar29 >>
                                                                                         2) +
                                                                                   (byte)(uVar27 >>
                                                                                         10),
                                                                                   (char)(uVar27 >>
                                                                                         2))))))));
        puVar4 = puVar4 + 1;
        uVar1 = uVar37;
        uVar37 = uVar2;
        puVar5 = puVar8;
      }
      uVar30 = (ushort)(((uint7)bVar19 << 0x30) >> 0x28);
      sVar14 = ((ushort)uVar37 & 0xff) * (short)DAT_005f49d0;
      sVar18 = (ushort)bVar15 * sVar18;
      sVar21 = (short)CONCAT21(uVar30,bVar16) * sVar21;
      sVar23 = (uVar30 >> 8) * sVar23;
      uVar26 = (ushort)(((uint7)bVar16 << 0x30) >> 0x28);
      uVar30 = (ushort)(((uint7)bVar34 << 0x30) >> 0x28);
      uVar28 = (ushort)bVar36 + sVar14 + (short)DAT_005f4a00;
      uVar29 = (ushort)(byte)uVar37 + sVar18 + sVar13;
      uVar31 = (short)CONCAT21(uVar26,bVar15) + sVar21 + sVar20;
      uVar26 = (uVar26 >> 8) + sVar23 + sVar6;
      uVar27 = (uVar27 & 0xff) + sVar14 + (short)DAT_005f4a08;
      uVar32 = (ushort)bVar16 + sVar18 + sVar17;
      uVar35 = (short)CONCAT21(uVar30,bVar19) + sVar21 + sVar22;
      *puVar8 = CONCAT17((char)((ushort)((uVar30 >> 8) + sVar23 + sVar7) >> 2) +
                         (byte)(uVar26 >> 10),
                         CONCAT16((byte)(uVar35 >> 10) + (char)(uVar26 >> 2),
                                  CONCAT15((char)(uVar35 >> 2) + (byte)(uVar31 >> 10),
                                           CONCAT14((byte)(uVar32 >> 10) + (char)(uVar31 >> 2),
                                                    CONCAT13((char)(uVar32 >> 2) +
                                                             (byte)(uVar29 >> 10),
                                                             CONCAT12((byte)(uVar27 >> 10) +
                                                                      (char)(uVar29 >> 2),
                                                                      CONCAT11((char)(uVar27 >> 2) +
                                                                               (byte)(uVar28 >> 10),
                                                                               (char)(uVar28 >> 2)))
                                                            )))));
      if (4 < iVar9) {
        sVar13 = (ushort)bVar34 * (short)DAT_005f49d0;
        sVar17 = (ushort)bVar24 * (short)((ulonglong)DAT_005f49d0 >> 0x10);
        sVar20 = (ushort)bVar33 * (short)((ulonglong)DAT_005f49d0 >> 0x20);
        sVar22 = (ushort)bVar25 * (short)((ulonglong)DAT_005f49d0 >> 0x30);
        uVar37 = uVar37 & _DAT_005f4a10;
        uVar27 = (ushort)bVar19 + sVar13 + (short)DAT_005f4a00;
        uVar30 = (ushort)bVar34 + sVar17 + (short)((ulonglong)DAT_005f4a00 >> 0x10);
        uVar26 = (ushort)bVar24 + sVar20 + (short)((ulonglong)DAT_005f4a00 >> 0x20);
        uVar28 = (ushort)bVar33 + sVar22 + (short)((ulonglong)DAT_005f4a00 >> 0x30);
        uVar29 = (ushort)(byte)(bVar24 + (char)(uVar37 >> 0x20)) + sVar13 + (short)DAT_005f4a08;
        uVar31 = (ushort)(byte)(bVar33 + (char)(uVar37 >> 0x28)) + sVar17 +
                 (short)((ulonglong)DAT_005f4a08 >> 0x10);
        uVar32 = (ushort)(byte)(bVar25 + (char)(uVar37 >> 0x30)) + sVar20 +
                 (short)((ulonglong)DAT_005f4a08 >> 0x20);
        puVar5[3] = CONCAT17((char)((ushort)((ushort)(byte)(uVar37 >> 0x38) + sVar22 +
                                            (short)((ulonglong)DAT_005f4a08 >> 0x30)) >> 2) +
                             (byte)(uVar28 >> 10),
                             CONCAT16((byte)(uVar32 >> 10) + (char)(uVar28 >> 2),
                                      CONCAT15((char)(uVar32 >> 2) + (byte)(uVar26 >> 10),
                                               CONCAT14((byte)(uVar31 >> 10) + (char)(uVar26 >> 2),
                                                        CONCAT13((char)(uVar31 >> 2) +
                                                                 (byte)(uVar30 >> 10),
                                                                 CONCAT12((byte)(uVar29 >> 10) +
                                                                          (char)(uVar30 >> 2),
                                                                          CONCAT11((char)(uVar29 >>
                                                                                         2) +
                                                                                   (byte)(uVar27 >>
                                                                                         10),
                                                                                   (char)(uVar27 >>
                                                                                         2))))))));
      }
      iVar11 = iVar11 + 1;
      piVar10 = piVar10 + 1;
    } while (iVar11 < *(int *)(param_1 + 0x13c));
  }
  return;
}
