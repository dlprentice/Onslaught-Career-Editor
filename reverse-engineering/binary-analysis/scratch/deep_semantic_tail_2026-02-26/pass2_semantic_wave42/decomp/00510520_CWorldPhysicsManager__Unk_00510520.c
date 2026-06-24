/* address: 0x00510520 */
/* name: CWorldPhysicsManager__Unk_00510520 */
/* signature: void CWorldPhysicsManager__Unk_00510520(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorldPhysicsManager__Unk_00510520(void)

{
  undefined4 *puVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  int *piVar5;
  void *unaff_ESI;

  piVar5 = (int *)*DAT_008553ec;
  DAT_008553ec[2] = (int)piVar5;
  if (piVar5 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar5;
  }
  while (iVar2 != 0) {
    CVBufTexture__Unk_00511ca0(iVar2);
    piVar5 = *(int **)(DAT_008553ec[2] + 4);
    DAT_008553ec[2] = (int)piVar5;
    if (piVar5 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar5;
    }
  }
  piVar5 = (int *)*DAT_008553f0;
  DAT_008553f0[2] = (int)piVar5;
  if (piVar5 == (int *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*piVar5;
  }
  while (piVar5 != (int *)0x0) {
    if ((void *)piVar5[4] != (void *)0x0) {
      iVar2 = CWorldPhysicsManager__Helper_004cd7a0(&DAT_0082b400,(void *)piVar5[4],unaff_ESI);
      *piVar5 = iVar2;
    }
    if ((void *)piVar5[5] != (void *)0x0) {
      iVar2 = CWorldPhysicsManager__Helper_004cd7a0(&DAT_0082b400,(void *)piVar5[5],unaff_ESI);
      piVar5[1] = iVar2;
    }
    piVar5 = *(int **)(DAT_008553f0[2] + 4);
    DAT_008553f0[2] = (int)piVar5;
    if (piVar5 == (int *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*piVar5;
    }
  }
  puVar1 = (undefined4 *)*DAT_008553f8;
  DAT_008553f8[2] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    pvVar3 = (void *)0x0;
  }
  else {
    pvVar3 = (void *)*puVar1;
  }
  while (pvVar3 != (void *)0x0) {
    CVBufTexture__Unk_00511d20(pvVar3);
    puVar1 = *(undefined4 **)(DAT_008553f8[2] + 4);
    DAT_008553f8[2] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = (void *)*puVar1;
    }
  }
  puVar1 = (undefined4 *)*DAT_008553fc;
  DAT_008553fc[2] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    pvVar3 = (void *)0x0;
  }
  else {
    pvVar3 = (void *)*puVar1;
  }
  while (pvVar3 != (void *)0x0) {
    CWorldPhysicsManager__Helper_00511db0(pvVar3);
    puVar1 = *(undefined4 **)(DAT_008553fc[2] + 4);
    DAT_008553fc[2] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = (void *)*puVar1;
    }
  }
  puVar1 = (undefined4 *)*DAT_00855400;
  DAT_00855400[2] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    pvVar3 = (void *)0x0;
  }
  else {
    pvVar3 = (void *)*puVar1;
  }
  while (pvVar3 != (void *)0x0) {
    CWorldPhysicsManager__Helper_00511db0(pvVar3);
    puVar1 = *(undefined4 **)(DAT_00855400[2] + 4);
    DAT_00855400[2] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = (void *)*puVar1;
    }
  }
  piVar5 = (int *)*DAT_00855404;
  DAT_00855404[2] = (int)piVar5;
  if (piVar5 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar5;
  }
  while (iVar2 != 0) {
    if (*(int *)(iVar2 + 0xc) != 0) {
      iVar4 = CBattleEngine__Helper_004e1910(&DAT_00896988,*(int *)(iVar2 + 0xc),0,(int)unaff_ESI);
      *(int *)(iVar2 + 4) = iVar4;
    }
    piVar5 = *(int **)(DAT_00855404[2] + 4);
    DAT_00855404[2] = (int)piVar5;
    if (piVar5 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar5;
    }
  }
  piVar5 = (int *)*DAT_00855408;
  DAT_00855408[2] = (int)piVar5;
  if (piVar5 == (int *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*piVar5;
  }
  while (piVar5 != (int *)0x0) {
    if ((void *)piVar5[2] != (void *)0x0) {
      iVar2 = CWorldPhysicsManager__Helper_004cd7a0(&DAT_0082b400,(void *)piVar5[2],unaff_ESI);
      *piVar5 = iVar2;
    }
    if (piVar5[3] != 0) {
      iVar2 = CBattleEngine__Helper_004e1910(&DAT_00896988,piVar5[3],0,(int)unaff_ESI);
      piVar5[1] = iVar2;
    }
    piVar5 = *(int **)(DAT_00855408[2] + 4);
    DAT_00855408[2] = (int)piVar5;
    if (piVar5 == (int *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*piVar5;
    }
  }
  return;
}
