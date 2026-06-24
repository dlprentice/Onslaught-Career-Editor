/* address: 0x0059b880 */
/* name: CTexture__Helper_0059b880 */
/* signature: void CTexture__Helper_0059b880(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__Helper_0059b880(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  int *unaff_EBX;
  undefined4 *puVar5;
  undefined4 *puVar6;
  int *local_8;
  int local_4;

  local_4 = 0;
  if (0 < unaff_EBX[0x53]) {
    local_8 = unaff_EBX + 0x54;
    do {
      iVar1 = *local_8;
      if (*(int *)(iVar1 + 0x4c) == 0) {
        iVar2 = *(int *)(iVar1 + 0x10);
        if (((iVar2 < 0) || (3 < iVar2)) || (unaff_EBX[iVar2 + 0x2a] == 0)) {
          puVar5 = (undefined4 *)*unaff_EBX;
          puVar5[5] = 0x34;
          puVar5[6] = iVar2;
          (*(code *)*puVar5)();
        }
        puVar3 = (undefined4 *)(**(code **)unaff_EBX[1])();
        puVar5 = (undefined4 *)unaff_EBX[iVar2 + 0x2a];
        puVar6 = puVar3;
        for (iVar4 = 0x21; iVar4 != 0; iVar4 = iVar4 + -1) {
          *puVar6 = *puVar5;
          puVar5 = puVar5 + 1;
          puVar6 = puVar6 + 1;
        }
        *(undefined4 **)(iVar1 + 0x4c) = puVar3;
      }
      local_4 = local_4 + 1;
      local_8 = local_8 + 1;
    } while (local_4 < unaff_EBX[0x53]);
  }
  return;
}
