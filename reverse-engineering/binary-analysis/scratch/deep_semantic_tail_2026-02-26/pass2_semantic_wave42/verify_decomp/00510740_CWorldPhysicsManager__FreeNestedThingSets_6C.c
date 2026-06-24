/* address: 0x00510740 */
/* name: CWorldPhysicsManager__FreeNestedThingSets_6C */
/* signature: void CWorldPhysicsManager__FreeNestedThingSets_6C(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorldPhysicsManager__FreeNestedThingSets_6C(void)

{
  int *piVar1;
  undefined4 *puVar2;
  void *pvVar3;
  int iVar4;

  piVar1 = (int *)*DAT_008553fc;
  DAT_008553fc[2] = (int)piVar1;
  if (piVar1 == (int *)0x0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *piVar1;
  }
  while (iVar4 != 0) {
    while ((puVar2 = *(undefined4 **)(iVar4 + 0x6c), puVar2 != (undefined4 *)0x0 &&
           (pvVar3 = (void *)*puVar2, pvVar3 != (void *)0x0))) {
      CSPtrSet__Remove((int *)(iVar4 + 0x6c),pvVar3);
      OID__FreeObject(pvVar3);
    }
    piVar1 = *(int **)(DAT_008553fc[2] + 4);
    DAT_008553fc[2] = (int)piVar1;
    if (piVar1 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar1;
    }
  }
  piVar1 = (int *)*DAT_00855400;
  DAT_00855400[2] = (int)piVar1;
  if (piVar1 == (int *)0x0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *piVar1;
  }
  while (iVar4 != 0) {
    while ((puVar2 = *(undefined4 **)(iVar4 + 0x6c), puVar2 != (undefined4 *)0x0 &&
           (pvVar3 = (void *)*puVar2, pvVar3 != (void *)0x0))) {
      CSPtrSet__Remove((int *)(iVar4 + 0x6c),pvVar3);
      OID__FreeObject(pvVar3);
    }
    piVar1 = *(int **)(DAT_00855400[2] + 4);
    DAT_00855400[2] = (int)piVar1;
    if (piVar1 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar1;
    }
  }
  return;
}
