/* address: 0x00510a90 */
/* name: CWorldPhysicsManager__Unk_00510a90 */
/* signature: void CWorldPhysicsManager__Unk_00510a90(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorldPhysicsManager__Unk_00510a90(void)

{
  undefined4 *puVar1;
  int *piVar2;
  void *pvVar3;

  pvVar3 = CSPtrSet__First(&DAT_006602a0);
  while (pvVar3 != (void *)0x0) {
    CSPtrSet__Remove(&DAT_006602a0,pvVar3);
    CBattleEngineDataManager__Clear();
    if (pvVar3 != (void *)0x0) {
      CWorldPhysicsManager__Unk_005113a0((int)pvVar3);
      OID__FreeObject(pvVar3);
    }
    pvVar3 = CSPtrSet__First(&DAT_006602a0);
  }
  if (DAT_008553e8 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553e8;
      DAT_008553e8[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_008553e8,pvVar3);
      CWorldPhysicsManager__Unk_00511040(pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_008553ec != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553ec;
      DAT_008553ec[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_008553ec,pvVar3);
      CWorldPhysicsManager__Unk_00510f10(pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_008553f0 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553f0;
      DAT_008553f0[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_008553f0,pvVar3);
      CWorldPhysicsManager__Unk_00510eb0((int)pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_008553f4 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553f4;
      DAT_008553f4[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) ||
         (puVar1 = (undefined4 *)*puVar1, puVar1 == (undefined4 *)0x0)) break;
      CSPtrSet__Remove(DAT_008553f4,puVar1);
      (**(code **)*puVar1)(1);
    }
  }
  if (DAT_008553f8 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553f8;
      DAT_008553f8[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_008553f8,pvVar3);
      CWorldPhysicsManager__Unk_00511070((int)pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_008553fc != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_008553fc;
      DAT_008553fc[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_008553fc,pvVar3);
      CWorldPhysicsManager__Unk_005110f0((int)pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_00855400 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_00855400;
      DAT_00855400[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_00855400,pvVar3);
      CWorldPhysicsManager__Unk_005110f0((int)pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_00855404 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_00855404;
      DAT_00855404[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_00855404,pvVar3);
      CWorldPhysicsManager__Unk_00510e60(pvVar3);
      OID__FreeObject(pvVar3);
    }
  }
  if (DAT_00855408 != (int *)0x0) {
    while( true ) {
      puVar1 = (undefined4 *)*DAT_00855408;
      DAT_00855408[2] = (int)puVar1;
      if ((puVar1 == (undefined4 *)0x0) || (pvVar3 = (void *)*puVar1, pvVar3 == (void *)0x0)) break;
      CSPtrSet__Remove(DAT_00855408,pvVar3);
      OID__FreeObject(*(void **)((int)pvVar3 + 0x10));
      *(undefined4 *)((int)pvVar3 + 0x10) = 0;
      OID__FreeObject(*(void **)((int)pvVar3 + 8));
      *(undefined4 *)((int)pvVar3 + 8) = 0;
      OID__FreeObject(*(void **)((int)pvVar3 + 0xc));
      *(undefined4 *)((int)pvVar3 + 0xc) = 0;
      OID__FreeObject(pvVar3);
    }
  }
  piVar2 = DAT_008553e8;
  if (DAT_008553e8 != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553e8);
    OID__FreeObject(piVar2);
    DAT_008553e8 = (int *)0x0;
  }
  piVar2 = DAT_008553ec;
  if (DAT_008553ec != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553ec);
    OID__FreeObject(piVar2);
    DAT_008553ec = (int *)0x0;
  }
  piVar2 = DAT_008553f0;
  if (DAT_008553f0 != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553f0);
    OID__FreeObject(piVar2);
    DAT_008553f0 = (int *)0x0;
  }
  piVar2 = DAT_008553f4;
  if (DAT_008553f4 != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553f4);
    OID__FreeObject(piVar2);
    DAT_008553f4 = (int *)0x0;
  }
  piVar2 = DAT_008553f8;
  if (DAT_008553f8 != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553f8);
    OID__FreeObject(piVar2);
    DAT_008553f8 = (int *)0x0;
  }
  piVar2 = DAT_008553fc;
  if (DAT_008553fc != (int *)0x0) {
    CSPtrSet__Clear(DAT_008553fc);
    OID__FreeObject(piVar2);
    DAT_008553fc = (int *)0x0;
  }
  piVar2 = DAT_00855400;
  if (DAT_00855400 != (int *)0x0) {
    CSPtrSet__Clear(DAT_00855400);
    OID__FreeObject(piVar2);
    DAT_00855400 = (int *)0x0;
  }
  piVar2 = DAT_00855404;
  if (DAT_00855404 != (int *)0x0) {
    CSPtrSet__Clear(DAT_00855404);
    OID__FreeObject(piVar2);
    DAT_00855404 = (int *)0x0;
  }
  piVar2 = DAT_00855408;
  if (DAT_00855408 != (int *)0x0) {
    CSPtrSet__Clear(DAT_00855408);
    OID__FreeObject(piVar2);
    DAT_00855408 = (int *)0x0;
  }
  return;
}
