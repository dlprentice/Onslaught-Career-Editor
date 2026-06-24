/* address: 0x0057d32e */
/* name: CWaypointManager__BoxBlurPackedColorRows_SIMD */
/* signature: int CWaypointManager__BoxBlurPackedColorRows_SIMD(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CWaypointManager__BoxBlurPackedColorRows_SIMD(void)

{
  undefined8 uVar1;
  undefined8 uVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  short sVar10;
  undefined8 *puVar11;
  int iVar12;
  undefined8 *puVar13;
  undefined8 *puVar14;
  undefined8 *puVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  undefined8 *in_stack_00000004;
  undefined8 *in_stack_00000008;
  uint in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;

  if ((in_stack_0000000c & 3) == 0) {
    puVar13 = (undefined8 *)(in_stack_00000010 * in_stack_00000014 + (int)in_stack_00000008);
    for (; (int)in_stack_00000008 < (int)puVar13;
        in_stack_00000008 = (undefined8 *)((int)in_stack_00000008 + in_stack_00000014 * 2)) {
      puVar14 = (undefined8 *)((int)in_stack_00000008 + in_stack_00000014);
      puVar11 = in_stack_00000004;
      puVar15 = in_stack_00000008;
      while ((int)puVar15 < (int)((int)in_stack_00000008 + in_stack_0000000c * 4)) {
        uVar16 = *puVar15;
        uVar17 = *puVar14;
        uVar1 = puVar15[1];
        uVar2 = puVar14[1];
        puVar15 = puVar15 + 2;
        puVar14 = puVar14 + 2;
        uVar16 = psraw(CONCAT26((ushort)(byte)((ulonglong)uVar16 >> 0x18) +
                                (ushort)(byte)((ulonglong)uVar16 >> 0x38) +
                                (ushort)(byte)((ulonglong)uVar17 >> 0x18) +
                                (ushort)(byte)((ulonglong)uVar17 >> 0x38) + 2,
                                CONCAT24((ushort)(byte)((ulonglong)uVar16 >> 0x10) +
                                         (ushort)(byte)((ulonglong)uVar16 >> 0x30) +
                                         (ushort)(byte)((ulonglong)uVar17 >> 0x10) +
                                         (ushort)(byte)((ulonglong)uVar17 >> 0x30) + 2,
                                         CONCAT22((ushort)(byte)((ulonglong)uVar16 >> 8) +
                                                  (ushort)(byte)((ulonglong)uVar16 >> 0x28) +
                                                  (ushort)(byte)((ulonglong)uVar17 >> 8) +
                                                  (ushort)(byte)((ulonglong)uVar17 >> 0x28) + 2,
                                                  (ushort)(byte)uVar16 +
                                                  (ushort)(byte)((ulonglong)uVar16 >> 0x20) +
                                                  (ushort)(byte)uVar17 +
                                                  (ushort)(byte)((ulonglong)uVar17 >> 0x20) + 2))),2
                      );
        uVar17 = psraw(CONCAT26((ushort)(byte)((ulonglong)uVar1 >> 0x18) +
                                (ushort)(byte)((ulonglong)uVar1 >> 0x38) +
                                (ushort)(byte)((ulonglong)uVar2 >> 0x18) +
                                (ushort)(byte)((ulonglong)uVar2 >> 0x38) + 2,
                                CONCAT24((ushort)(byte)((ulonglong)uVar1 >> 0x10) +
                                         (ushort)(byte)((ulonglong)uVar1 >> 0x30) +
                                         (ushort)(byte)((ulonglong)uVar2 >> 0x10) +
                                         (ushort)(byte)((ulonglong)uVar2 >> 0x30) + 2,
                                         CONCAT22((ushort)(byte)((ulonglong)uVar1 >> 8) +
                                                  (ushort)(byte)((ulonglong)uVar1 >> 0x28) +
                                                  (ushort)(byte)((ulonglong)uVar2 >> 8) +
                                                  (ushort)(byte)((ulonglong)uVar2 >> 0x28) + 2,
                                                  (ushort)(byte)uVar1 +
                                                  (ushort)(byte)((ulonglong)uVar1 >> 0x20) +
                                                  (ushort)(byte)uVar2 +
                                                  (ushort)(byte)((ulonglong)uVar2 >> 0x20) + 2))),2)
        ;
        sVar3 = (short)uVar16;
        sVar4 = (short)((ulonglong)uVar16 >> 0x10);
        sVar5 = (short)((ulonglong)uVar16 >> 0x20);
        sVar6 = (short)((ulonglong)uVar16 >> 0x30);
        sVar7 = (short)uVar17;
        sVar8 = (short)((ulonglong)uVar17 >> 0x10);
        sVar9 = (short)((ulonglong)uVar17 >> 0x20);
        sVar10 = (short)((ulonglong)uVar17 >> 0x30);
        *puVar11 = CONCAT17((0 < sVar10) * (sVar10 < 0x100) * (char)((ulonglong)uVar17 >> 0x30) -
                            (0xff < sVar10),
                            CONCAT16((0 < sVar9) * (sVar9 < 0x100) *
                                     (char)((ulonglong)uVar17 >> 0x20) - (0xff < sVar9),
                                     CONCAT15((0 < sVar8) * (sVar8 < 0x100) *
                                              (char)((ulonglong)uVar17 >> 0x10) - (0xff < sVar8),
                                              CONCAT14((0 < sVar7) * (sVar7 < 0x100) * (char)uVar17
                                                       - (0xff < sVar7),
                                                       CONCAT13((0 < sVar6) * (sVar6 < 0x100) *
                                                                (char)((ulonglong)uVar16 >> 0x30) -
                                                                (0xff < sVar6),
                                                                CONCAT12((0 < sVar5) *
                                                                         (sVar5 < 0x100) *
                                                                         (char)((ulonglong)uVar16 >>
                                                                               0x20) -
                                                                         (0xff < sVar5),
                                                                         CONCAT11((0 < sVar4) *
                                                                                  (sVar4 < 0x100) *
                                                                                  (char)((ulonglong)
                                                                                         uVar16 >>
                                                                                        0x10) -
                                                                                  (0xff < sVar4),
                                                                                  (0 < sVar3) *
                                                                                  (sVar3 < 0x100) *
                                                                                  (char)uVar16 -
                                                                                  (0xff < sVar3)))))
                                             )));
        puVar11 = puVar11 + 1;
      }
      in_stack_00000004 = (undefined8 *)((int)in_stack_00000004 + in_stack_00000018);
    }
    iVar12 = 0;
  }
  else {
    iVar12 = CWaypointManager__BoxBlurPackedColorRows_Scalar();
  }
  return iVar12;
}
