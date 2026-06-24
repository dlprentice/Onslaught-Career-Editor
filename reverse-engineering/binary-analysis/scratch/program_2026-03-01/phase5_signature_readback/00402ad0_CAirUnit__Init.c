/* address: 0x00402ad0 */
/* name: CAirUnit__Init */
/* signature: void __thiscall CAirUnit__Init(void * this, int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CAirUnit__Init(void *this,int param_1)

{
  undefined4 uVar1;
  int *piVar2;
  void *pvVar3;
  int iVar4;
  void *unaff_EDI;
  float local_90;
  float local_8c;
  float local_88;
  void *pvStack_80;
  float fStack_7c;
  float fStack_78;
  float fStack_74;
  undefined1 local_6c [48];
  undefined1 local_3c [48];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d0f9c;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  CUnit__Init(this);
  local_90 = *(float *)(*(int *)(param_1 + 0x3bc) + 0xb8);
  *(float *)((int)this + 300) = local_90;
  *(float *)((int)this + 0x130) = local_90;
  *(float *)((int)this + 0x134) = local_90;
  uVar1 = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 0xc4);
  *(undefined4 *)((int)this + 0x100) = uVar1;
  *(undefined4 *)((int)this + 0x104) = uVar1;
  *(undefined4 *)((int)this + 0x108) = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 0xcc);
  local_8c = local_90;
  local_88 = local_90;
  if (*(int *)(*(int *)((int)this + 0x164) + 8) != 0) {
    iVar4 = 1;
    while( true ) {
      piVar2 = *(int **)((int)this + 0x30);
      vector_constructor_iterator_nothrow(local_6c,0x10,3,&LAB_00402d20);
      (**(code **)(*piVar2 + 0x1c))(s_Trail_00622d14,iVar4,&local_90,local_6c,1,0);
      if (((local_90 == _DAT_005d856c) && (local_8c == _DAT_005d856c)) &&
         (local_88 == _DAT_005d856c)) break;
      pvVar3 = (void *)OID__AllocObject(8,0x10,s_C__dev_ONSLAUGHT2_AirUnit_cpp_00622cf4,0x2a);
      uStack_4 = 0;
      pvStack_80 = pvVar3;
      if (pvVar3 == (void *)0x0) {
        pvVar3 = (void *)0x0;
      }
      else {
        *(undefined4 *)((int)pvVar3 + 4) = 0;
        CWorldPhysicsManager__PushNodeGlobalList(unaff_EDI);
      }
      uStack_4 = 0xffffffff;
      CSPtrSet__AddToTail((void *)((int)this + 0x25c),pvVar3);
      iVar4 = iVar4 + 1;
    }
  }
  if (*(int *)(*(int *)((int)this + 0x164) + 0x14) != 0) {
    iVar4 = 1;
    while( true ) {
      piVar2 = *(int **)((int)this + 0x30);
      vector_constructor_iterator_nothrow(local_3c,0x10,3,&LAB_00402d20);
      (**(code **)(*piVar2 + 0x1c))(s_Engine_00622cec,iVar4,&fStack_7c,local_3c,1,0);
      if (((fStack_7c == _DAT_005d856c) && (fStack_78 == _DAT_005d856c)) &&
         (fStack_74 == _DAT_005d856c)) break;
      pvVar3 = (void *)OID__AllocObject(8,0x10,s_C__dev_ONSLAUGHT2_AirUnit_cpp_00622cf4,0x36);
      uStack_4 = 1;
      pvStack_80 = pvVar3;
      if (pvVar3 == (void *)0x0) {
        pvVar3 = (void *)0x0;
      }
      else {
        *(undefined4 *)((int)pvVar3 + 4) = 0;
        CWorldPhysicsManager__PushNodeGlobalList(unaff_EDI);
      }
      uStack_4 = 0xffffffff;
      CSPtrSet__AddToTail((void *)((int)this + 0x26c),pvVar3);
      iVar4 = iVar4 + 1;
    }
  }
  *(undefined4 *)((int)this + 600) = 0;
  CSPtrSet__AddToHead(&DAT_008550e0,this);
  ExceptionList = pvStack_c;
  return;
}
