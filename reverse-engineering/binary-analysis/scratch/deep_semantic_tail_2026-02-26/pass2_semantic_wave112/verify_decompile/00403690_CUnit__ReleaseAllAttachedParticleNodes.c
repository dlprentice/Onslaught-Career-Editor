/* address: 0x00403690 */
/* name: CUnit__ReleaseAllAttachedParticleNodes */
/* signature: int __fastcall CUnit__ReleaseAllAttachedParticleNodes(int param_1) */


int __fastcall CUnit__ReleaseAllAttachedParticleNodes(int param_1)

{
  undefined4 *puVar1;
  void *pvVar2;
  int iVar3;
  int unaff_EDI;

  iVar3 = CUnit__Helper_004fd140(param_1);
  if (iVar3 == 0) {
    return 0;
  }
  CUnit__Unk_004fcfe0(param_1);
  while( true ) {
    puVar1 = *(undefined4 **)(param_1 + 0x25c);
    *(undefined4 **)(param_1 + 0x264) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (pvVar2 = (void *)*puVar1, pvVar2 == (void *)0x0)) break;
    CSPtrSet__Remove((int *)(param_1 + 0x25c),pvVar2);
    CUnit__Helper_004cb0b0(pvVar2,0,unaff_EDI);
    CParticleManager__RemoveFromGlobalList();
    OID__FreeObject(pvVar2);
  }
  while( true ) {
    puVar1 = *(undefined4 **)(param_1 + 0x26c);
    *(undefined4 **)(param_1 + 0x274) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (pvVar2 = (void *)*puVar1, pvVar2 == (void *)0x0)) break;
    CSPtrSet__Remove((int *)(param_1 + 0x26c),pvVar2);
    CUnit__Helper_004cb0b0(pvVar2,0,unaff_EDI);
    CParticleManager__RemoveFromGlobalList();
    OID__FreeObject(pvVar2);
  }
  return 1;
}
