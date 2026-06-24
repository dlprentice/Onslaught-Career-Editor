/* address: 0x005ac180 */
/* name: CTexture__Helper_005ac180 */
/* signature: int CTexture__Helper_005ac180(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_005ac180(void)

{
  short *psVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int *piVar5;
  int unaff_EBX;
  int iVar6;
  int iVar7;
  int local_8;
  undefined4 *local_4;

  iVar6 = 0;
  iVar4 = *(int *)(unaff_EBX + 0x1b0);
  local_8 = 0;
  if ((*(int *)(unaff_EBX + 0xe0) == 0) || (*(int *)(unaff_EBX + 0xa4) == 0)) {
    return 0;
  }
  if (*(int *)(iVar4 + 0x70) == 0) {
    uVar3 = (*(code *)**(undefined4 **)(unaff_EBX + 4))();
    *(undefined4 *)(iVar4 + 0x70) = uVar3;
  }
  iVar7 = 0;
  if (0 < *(int *)(unaff_EBX + 0x24)) {
    local_4 = (undefined4 *)(*(int *)(unaff_EBX + 0xdc) + 0x4c);
    piVar5 = (int *)(*(int *)(iVar4 + 0x70) + 4);
    do {
      psVar1 = (short *)*local_4;
      if (psVar1 == (short *)0x0) {
        return 0;
      }
      if (*psVar1 == 0) {
        return 0;
      }
      if (psVar1[1] == 0) {
        return 0;
      }
      if (psVar1[8] == 0) {
        return 0;
      }
      if (psVar1[0x10] == 0) {
        return 0;
      }
      if (psVar1[9] == 0) {
        return 0;
      }
      if (psVar1[2] == 0) {
        return 0;
      }
      iVar4 = *(int *)(unaff_EBX + 0xa4) + iVar6;
      if (*(int *)(*(int *)(unaff_EBX + 0xa4) + iVar6) < 0) {
        return 0;
      }
      iVar2 = *(int *)(iVar4 + 4);
      *piVar5 = iVar2;
      if (iVar2 != 0) {
        local_8 = 1;
      }
      iVar2 = *(int *)(iVar4 + 8);
      piVar5[1] = iVar2;
      if (iVar2 != 0) {
        local_8 = 1;
      }
      iVar2 = *(int *)(iVar4 + 0xc);
      piVar5[2] = iVar2;
      if (iVar2 != 0) {
        local_8 = 1;
      }
      iVar2 = *(int *)(iVar4 + 0x10);
      piVar5[3] = iVar2;
      if (iVar2 != 0) {
        local_8 = 1;
      }
      iVar4 = *(int *)(iVar4 + 0x14);
      piVar5[4] = iVar4;
      if (iVar4 != 0) {
        local_8 = 1;
      }
      piVar5 = piVar5 + 6;
      iVar7 = iVar7 + 1;
      local_4 = local_4 + 0x15;
      iVar6 = iVar6 + 0x100;
    } while (iVar7 < *(int *)(unaff_EBX + 0x24));
  }
  return local_8;
}
