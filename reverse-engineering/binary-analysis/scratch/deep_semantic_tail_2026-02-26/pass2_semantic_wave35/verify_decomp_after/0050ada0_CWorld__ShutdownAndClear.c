/* address: 0x0050ada0 */
/* name: CWorld__ShutdownAndClear */
/* signature: void __fastcall CWorld__ShutdownAndClear(void * param_1) */


void __fastcall CWorld__ShutdownAndClear(void *param_1)

{
  void *pvVar1;
  int *piVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  int unaff_ESI;

  if (DAT_0067a748 != (int *)0x0) {
    (**(code **)(*DAT_0067a748 + 4))(1);
  }
  DAT_0067a748 = (int *)0x0;
  if (*(void **)((int)param_1 + 0x200) != (void *)0x0) {
    CWorld__ReleaseSubObject_AndMaybeFree(*(void **)((int)param_1 + 0x200),(void *)0x1,unaff_ESI);
  }
  *(undefined4 *)((int)param_1 + 0x200) = 0;
  if (*(void **)((int)param_1 + 0x204) != (void *)0x0) {
    CWorld__ReleaseSubObject_AndMaybeFree(*(void **)((int)param_1 + 0x204),(void *)0x1,unaff_ESI);
  }
  *(undefined4 *)((int)param_1 + 0x204) = 0;
  if (*(void **)((int)param_1 + 0x208) != (void *)0x0) {
    CWorld__ReleaseSubObject_AndMaybeFree(*(void **)((int)param_1 + 0x208),(void *)0x1,unaff_ESI);
  }
  *(undefined4 *)((int)param_1 + 0x208) = 0;
  pvVar1 = CSPtrSet__First(param_1);
  while (pvVar1 != (void *)0x0) {
    piVar2 = CSPtrSet__First(param_1);
    (**(code **)(*piVar2 + 8))();
    puVar4 = *(undefined4 **)param_1;
    *(undefined4 **)((int)param_1 + 8) = puVar4;
    if (puVar4 == (undefined4 *)0x0) {
      piVar3 = (int *)0x0;
    }
    else {
      piVar3 = (int *)*puVar4;
    }
    if (piVar2 == piVar3) {
      CSPtrSet__Remove(param_1,piVar2);
    }
    pvVar1 = CSPtrSet__First(param_1);
  }
  CWorld__ClearLinkedObjectPairSet((void *)((int)param_1 + 0x120));
  CSPtrSet__Clear((void *)((int)param_1 + 0xb0));
  CSPtrSet__Clear((void *)((int)param_1 + 0x110));
  while( true ) {
    puVar4 = *(undefined4 **)((int)param_1 + 0xc0);
    *(undefined4 **)((int)param_1 + 200) = puVar4;
    if ((puVar4 == (undefined4 *)0x0) || (pvVar1 = (void *)*puVar4, pvVar1 == (void *)0x0)) break;
    CSPtrSet__Remove((int *)((int)param_1 + 0xc0),pvVar1);
    CGenericActiveReader__dtor(pvVar1);
    OID__FreeObject(pvVar1);
  }
  CSPtrSet__Clear(param_1);
  while( true ) {
    piVar2 = *(int **)((int)param_1 + 0xf0);
    *(int **)((int)param_1 + 0xf8) = piVar2;
    if ((piVar2 == (int *)0x0) || ((int *)*piVar2 == (int *)0x0)) break;
    (**(code **)(*(int *)*piVar2 + 4))(1);
  }
  while( true ) {
    piVar2 = *(int **)((int)param_1 + 0x100);
    *(int **)((int)param_1 + 0x108) = piVar2;
    if ((piVar2 == (int *)0x0) || ((int *)*piVar2 == (int *)0x0)) break;
    (**(code **)(*(int *)*piVar2 + 4))(1);
  }
  CWaypointManager__Unk_00505ab0();
  OID_FreeObject__Wrapper_0040f140();
  CWorldMeshList__Clear();
  OID__FreeObject(DAT_0067a07c);
  DAT_0067a07c = (void *)0x0;
  OID__FreeObject(DAT_0067a078);
  DAT_0067a078 = (void *)0x0;
  puVar4 = (undefined4 *)((int)param_1 + 0x198);
  iVar5 = 0x1a;
  do {
    puVar4[-0x1a] = 0;
    *puVar4 = 0;
    puVar4 = puVar4 + 1;
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  CSPtrSet__Clear((void *)((int)param_1 + 0xe0));
  CSPtrSet__Clear((void *)((int)param_1 + 0x50));
  CSPtrSet__Clear((void *)((int)param_1 + 0x30));
  CSPtrSet__Clear((void *)((int)param_1 + 0x20));
  *(undefined4 *)((int)param_1 + 0x20c) = 0;
  *(undefined4 *)((int)param_1 + 0x210) = 0;
  *(undefined4 *)((int)param_1 + 0x214) = 0;
  *(undefined4 *)((int)param_1 + 0x218) = 0;
  return;
}
