/* address: 0x005b3ec0 */
/* name: CDXTexture__Helper_005b3ec0 */
/* signature: void __stdcall CDXTexture__Helper_005b3ec0(uint param_1) */


void CDXTexture__Helper_005b3ec0(uint param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  char *pcVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  undefined1 *puVar6;
  char cVar7;
  int in_EAX;
  int iVar8;
  uint uVar9;
  int unaff_ESI;
  uint uVar10;
  uint uStack_4;

  iVar8 = *(int *)(unaff_ESI + 0x1c);
  if (in_EAX == 0) {
    piVar1 = *(int **)(unaff_ESI + 0x20);
    puVar2 = (undefined4 *)*piVar1;
    puVar2[5] = 0x28;
    (*(code *)*puVar2)(piVar1);
  }
  if (*(int *)(unaff_ESI + 0xc) == 0) {
    uVar9 = iVar8 + in_EAX;
    uVar10 = ((1 << ((byte)in_EAX & 0x1f)) - 1U & param_1) << (0x18U - (char)uVar9 & 0x1f) |
             *(uint *)(unaff_ESI + 0x18);
    if (7 < (int)uVar9) {
      uStack_4 = uVar9 >> 3;
      uVar9 = uVar9 + uStack_4 * -8;
      do {
        pcVar3 = *(char **)(unaff_ESI + 0x10);
        cVar7 = (char)(uVar10 >> 0x10);
        *pcVar3 = cVar7;
        *(char **)(unaff_ESI + 0x10) = pcVar3 + 1;
        piVar1 = (int *)(unaff_ESI + 0x14);
        *piVar1 = *piVar1 + -1;
        if (*piVar1 == 0) {
          puVar2 = *(undefined4 **)(*(int *)(unaff_ESI + 0x20) + 0x18);
          iVar8 = (*(code *)puVar2[3])(*(int *)(unaff_ESI + 0x20));
          if (iVar8 == 0) {
            piVar1 = *(int **)(unaff_ESI + 0x20);
            puVar4 = (undefined4 *)*piVar1;
            puVar4[5] = 0x18;
            (*(code *)*puVar4)(piVar1);
          }
          uVar5 = puVar2[1];
          *(undefined4 *)(unaff_ESI + 0x10) = *puVar2;
          *(undefined4 *)(unaff_ESI + 0x14) = uVar5;
        }
        if (cVar7 == -1) {
          puVar6 = *(undefined1 **)(unaff_ESI + 0x10);
          *puVar6 = 0;
          *(undefined1 **)(unaff_ESI + 0x10) = puVar6 + 1;
          piVar1 = (int *)(unaff_ESI + 0x14);
          *piVar1 = *piVar1 + -1;
          if (*piVar1 == 0) {
            puVar2 = *(undefined4 **)(*(int *)(unaff_ESI + 0x20) + 0x18);
            iVar8 = (*(code *)puVar2[3])(*(int *)(unaff_ESI + 0x20));
            if (iVar8 == 0) {
              piVar1 = *(int **)(unaff_ESI + 0x20);
              puVar4 = (undefined4 *)*piVar1;
              puVar4[5] = 0x18;
              (*(code *)*puVar4)(piVar1);
            }
            uVar5 = puVar2[1];
            *(undefined4 *)(unaff_ESI + 0x10) = *puVar2;
            *(undefined4 *)(unaff_ESI + 0x14) = uVar5;
          }
        }
        uVar10 = uVar10 << 8;
        uStack_4 = uStack_4 - 1;
      } while (uStack_4 != 0);
    }
    *(uint *)(unaff_ESI + 0x18) = uVar10;
    *(uint *)(unaff_ESI + 0x1c) = uVar9;
  }
  return;
}
