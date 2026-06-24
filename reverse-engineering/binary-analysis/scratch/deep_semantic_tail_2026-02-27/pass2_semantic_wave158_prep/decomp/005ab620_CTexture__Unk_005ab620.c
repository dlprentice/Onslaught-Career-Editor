/* address: 0x005ab620 */
/* name: CTexture__Unk_005ab620 */
/* signature: void CTexture__Unk_005ab620(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__Unk_005ab620(void)

{
  int iVar1;
  int in_EAX;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int *piVar6;
  undefined4 *puVar7;
  int *piVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  int local_c;

  iVar1 = *(int *)(in_EAX + 0x140);
  local_c = *(int *)(in_EAX + 0x24);
  if (0 < local_c) {
    piVar6 = *(int **)(*(int *)(in_EAX + 0x1ac) + 0x3c);
    piVar8 = (int *)(*(int *)(in_EAX + 0xdc) + 0xc);
    iVar3 = *(int *)(*(int *)(in_EAX + 0x1ac) + 0x38) - (int)piVar6;
    do {
      iVar2 = (piVar8[6] * *piVar8) / iVar1;
      puVar9 = (undefined4 *)*piVar6;
      if (0 < iVar2) {
        puVar7 = puVar9 + (iVar1 + 2) * iVar2;
        puVar5 = puVar9 + -iVar2;
        puVar10 = puVar9 + (iVar1 + 1) * iVar2;
        iVar4 = *(int *)(iVar3 + (int)piVar6) - (int)puVar9;
        do {
          *(undefined4 *)(iVar4 + (int)puVar5) = *(undefined4 *)(iVar4 + (int)puVar10);
          *puVar5 = *puVar10;
          *(undefined4 *)(iVar4 + (int)puVar7) = *(undefined4 *)(iVar4 + (int)puVar9);
          *puVar7 = *puVar9;
          puVar10 = puVar10 + 1;
          puVar5 = puVar5 + 1;
          puVar9 = puVar9 + 1;
          puVar7 = puVar7 + 1;
          iVar2 = iVar2 + -1;
        } while (iVar2 != 0);
      }
      piVar6 = piVar6 + 1;
      piVar8 = piVar8 + 0x15;
      local_c = local_c + -1;
    } while (local_c != 0);
  }
  return;
}
