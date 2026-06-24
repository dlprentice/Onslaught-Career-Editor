/* address: 0x005110f0 */
/* name: CWorldPhysicsManager__Unk_005110f0 */
/* signature: void __fastcall CWorldPhysicsManager__Unk_005110f0(int param_1) */


void __fastcall CWorldPhysicsManager__Unk_005110f0(int param_1)

{
  void *this;
  void *pvVar1;
  void *pvVar2;
  void *pvVar3;
  void *value;
  undefined1 local_14 [4];
  void *local_10;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d667c;
  local_c = ExceptionList;
  local_4 = 3;
  ExceptionList = &local_c;
  OID__FreeObject(*(void **)(param_1 + 0xb0));
  *(undefined4 *)(param_1 + 0xb0) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x2c));
  *(undefined4 *)(param_1 + 0x2c) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x30));
  this = (void *)(param_1 + 0x3c);
  *(undefined4 *)(param_1 + 0x30) = 0;
  pvVar1 = CSPtrSet__First(this);
  while (pvVar1 != (void *)0x0) {
    CSPtrSet__Remove(this,pvVar1);
    OID__FreeObject(pvVar1);
    pvVar1 = CSPtrSet__First(this);
  }
  pvVar1 = (void *)(param_1 + 0x4c);
  pvVar2 = CSPtrSet__First(pvVar1);
  while (pvVar2 != (void *)0x0) {
    CSPtrSet__Remove(pvVar1,pvVar2);
    OID__FreeObject(pvVar2);
    pvVar2 = CSPtrSet__First(pvVar1);
  }
  pvVar2 = (void *)(param_1 + 0x5c);
  pvVar3 = CSPtrSet__First(pvVar2);
  while (pvVar3 != (void *)0x0) {
    CSPtrSet__Remove(pvVar2,pvVar3);
    OID__FreeObject(pvVar3);
    pvVar3 = CSPtrSet__First(pvVar2);
  }
  OID__FreeObject(*(void **)(param_1 + 0x7c));
  *(undefined4 *)(param_1 + 0x7c) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x80));
  *(undefined4 *)(param_1 + 0x80) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x84));
  *(undefined4 *)(param_1 + 0x84) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x88));
  *(undefined4 *)(param_1 + 0x88) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x8c));
  *(undefined4 *)(param_1 + 0x8c) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x94));
  *(undefined4 *)(param_1 + 0x94) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x98));
  *(undefined4 *)(param_1 + 0x98) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x9c));
  *(undefined4 *)(param_1 + 0x9c) = 0;
  OID__FreeObject(*(void **)(param_1 + 0xa0));
  *(undefined4 *)(param_1 + 0xa0) = 0;
  OID__FreeObject(*(void **)(param_1 + 0xa4));
  *(undefined4 *)(param_1 + 0xa4) = 0;
  OID__FreeObject(*(void **)(param_1 + 0xa8));
  *(undefined4 *)(param_1 + 0xa8) = 0;
  OID__FreeObject(*(void **)(param_1 + 0xac));
  *(undefined4 *)(param_1 + 0xac) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x90));
  pvVar3 = (void *)(param_1 + 0x6c);
  *(undefined4 *)(param_1 + 0x90) = 0;
  local_10 = pvVar3;
  value = (void *)LinkedPtrCursor__MoveFirstAndGet(local_14);
  while (value != (void *)0x0) {
    CSPtrSet__Remove(pvVar3,value);
    OID__FreeObject(value);
    value = (void *)LinkedPtrCursor__MoveFirstAndGet(local_14);
  }
  local_4._1_3_ = (uint3)((uint)local_4 >> 8);
  local_4._0_1_ = 2;
  CSPtrSet__Clear(pvVar3);
  local_4._0_1_ = 1;
  CSPtrSet__Clear(pvVar2);
  local_4 = (uint)local_4._1_3_ << 8;
  CSPtrSet__Clear(pvVar1);
  local_4 = 0xffffffff;
  CSPtrSet__Clear(this);
  ExceptionList = local_c;
  return;
}
