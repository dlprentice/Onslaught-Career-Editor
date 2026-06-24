/* address: 0x005473b0 */
/* name: CDXEngine__Unk_005473b0 */
/* signature: int CDXEngine__Unk_005473b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXEngine__Unk_005473b0(void)

{
  ushort *puVar1;
  byte *pbVar2;
  int iVar3;
  int *piVar4;
  int in_ECX;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  int in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int local_1c;

  iVar7 = *(int *)(in_ECX + 0x24);
  if (in_stack_00000014 == 0) {
    iVar8 = in_stack_0000000c - in_stack_00000004;
    iVar10 = in_stack_00000010 - in_stack_00000008;
    in_stack_00000004 = in_stack_00000004 + -1 >> 3;
    in_stack_00000008 = in_stack_00000008 + -1 >> 3;
    in_stack_0000000c = in_stack_0000000c >> 3;
    in_stack_00000010 = in_stack_00000010 >> 3;
    if (in_stack_00000004 < 0) {
      in_stack_00000004 = 0;
    }
    if (in_stack_00000008 < 0) {
      in_stack_00000008 = 0;
    }
    if (0x3f < in_stack_00000004) {
      in_stack_00000004 = 0x3f;
    }
    if (0x3f < in_stack_00000008) {
      in_stack_00000008 = 0x3f;
    }
    if (0x3f < in_stack_0000000c) {
      in_stack_0000000c = 0x3f;
    }
    iVar3 = in_stack_00000008;
    if (0x3f < in_stack_00000010) {
      in_stack_00000010 = 0x3f;
    }
    for (; iVar3 <= in_stack_00000010; iVar3 = iVar3 + 1) {
      if (in_stack_00000004 <= in_stack_0000000c) {
        iVar5 = in_stack_00000004;
        do {
          uVar9 = iVar3 * 0x40 + iVar5 & 0xffff;
          if ((*(int *)(in_ECX + 0x20) != 0) && (local_1c = 0, 0 < *(int *)(in_ECX + 0x20))) {
            in_stack_00000014 = 0;
            do {
              iVar6 = 1;
              if (1 < *(int *)(in_stack_00000014 + 0xc + iVar7)) {
                iVar11 = 0x50;
                do {
                  puVar1 = (ushort *)(*(int *)(in_stack_00000014 + iVar7) + -6 + iVar11);
                  iVar7 = *(int *)(in_stack_00000014 + iVar7) + -0x50 + iVar11;
                  iVar11 = iVar11 + 0x50;
                  pbVar2 = (byte *)(*(int *)(iVar7 + 0x40) + 1 +
                                   (((*puVar1 & uVar9) >> (*(byte *)(iVar7 + 0x34) & 0x1f)) +
                                   (*(ushort *)(iVar7 + 0x48) & uVar9)) * 2);
                  *pbVar2 = *pbVar2 | 0x80;
                  iVar6 = iVar6 + 1;
                  iVar7 = *(int *)(in_ECX + 0x24);
                } while (iVar6 < *(int *)(in_stack_00000014 + 0xc + iVar7));
              }
              local_1c = local_1c + 1;
              in_stack_00000014 = in_stack_00000014 + 0x34;
            } while (local_1c < *(int *)(in_ECX + 0x20));
          }
          iVar5 = iVar5 + 1;
        } while (iVar5 <= in_stack_0000000c);
      }
    }
    if ((1 < iVar8) && (1 < iVar10)) {
      in_stack_00000008 =
           CLandscapeTexture__UpdateTileRange
                     (in_stack_00000004,in_stack_00000008,in_stack_0000000c,in_stack_00000010);
    }
    return in_stack_00000008;
  }
  CDXLandscape__BuildVertexBuffer();
  iVar8 = 0;
  do {
    CDXPatchManager__ResetPatchSlots();
    iVar8 = iVar8 + 8;
  } while (iVar8 < 0x18);
  iVar8 = 0x1000;
  piVar4 = (int *)(*(int *)(iVar7 + 4) + 0xc);
  do {
    if (*piVar4 != 0) {
      *(undefined2 *)(*piVar4 + 0x3c) = 0xffff;
      *piVar4 = 0;
      *(undefined1 *)(piVar4 + 1) = 0x9d;
    }
    piVar4 = piVar4 + 5;
    iVar8 = iVar8 + -1;
  } while (iVar8 != 0);
  return (int)piVar4;
}
