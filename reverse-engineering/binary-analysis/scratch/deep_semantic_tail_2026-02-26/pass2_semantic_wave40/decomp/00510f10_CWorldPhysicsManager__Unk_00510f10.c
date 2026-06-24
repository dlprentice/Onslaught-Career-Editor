/* address: 0x00510f10 */
/* name: CWorldPhysicsManager__Unk_00510f10 */
/* signature: void __fastcall CWorldPhysicsManager__Unk_00510f10(void * param_1) */


void __fastcall CWorldPhysicsManager__Unk_00510f10(void *param_1)

{
  int *this;
  int *this_00;
  undefined4 *puVar1;
  void *pvVar2;
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  puStack_8 = &LAB_005d6646;
  local_c = ExceptionList;
  this = (int *)((int)param_1 + 0x5c);
  local_4 = 1;
  ExceptionList = &local_c;
  while( true ) {
    puVar1 = (undefined4 *)*this;
    *(undefined4 **)((int)param_1 + 100) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (pvVar2 = (void *)*puVar1, pvVar2 == (void *)0x0)) break;
    CSPtrSet__Remove(this,pvVar2);
    OID__FreeObject(pvVar2);
  }
  this_00 = (int *)((int)param_1 + 0x4c);
  while( true ) {
    puVar1 = (undefined4 *)*this_00;
    *(undefined4 **)((int)param_1 + 0x54) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (pvVar2 = (void *)*puVar1, pvVar2 == (void *)0x0)) break;
    CSPtrSet__Remove(this_00,pvVar2);
    OID__FreeObject(pvVar2);
  }
  OID__FreeObject(*(void **)((int)param_1 + 0x30));
  *(undefined4 *)((int)param_1 + 0x30) = 0;
  OID__FreeObject(*(void **)param_1);
  *(undefined4 *)param_1 = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x1c));
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x20));
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x24));
  *(undefined4 *)((int)param_1 + 0x24) = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x28));
  *(undefined4 *)((int)param_1 + 0x28) = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x2c));
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  local_4 = local_4 & 0xffffff00;
  CSPtrSet__Clear(this);
  local_4 = 0xffffffff;
  CSPtrSet__Clear(this_00);
  ExceptionList = local_c;
  return;
}
