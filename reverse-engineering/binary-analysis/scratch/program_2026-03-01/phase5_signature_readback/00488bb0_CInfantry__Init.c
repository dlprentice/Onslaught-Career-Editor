/* address: 0x00488bb0 */
/* name: CInfantry__Init */
/* signature: void __thiscall CInfantry__Init(void * this, int param_1) */


void __thiscall CInfantry__Init(void *this,int param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  float10 fVar4;
  void *pvVar5;
  void *local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 *puStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d2e5a;
  puStack_c = ExceptionList;
  ExceptionList = &puStack_c;
  *(undefined4 *)(param_1 + 0x80) = 1;
  *(undefined4 *)(param_1 + 0x70) = 0x2000010;
  puVar2 = (undefined4 *)OID__AllocObject(0x38,0xb,s_C__dev_ONSLAUGHT2_Infantry_cpp_0062d4a8,0x1c);
  local_4 = 0;
  if (puVar2 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    CCollisionSeekingThing__ctor_like_00488ef0(puVar2);
    local_4 = CONCAT31(local_4._1_3_,1);
    CHLCollisionDetector__ctor_like_00488f00(puVar2 + 9);
    *puVar2 = &PTR_LAB_005dbf48;
  }
  *(undefined4 **)((int)this + 0x38) = puVar2;
  local_4 = 0xffffffff;
  if (*(int *)(param_1 + 0x60) == 1) {
    fVar4 = (float10)fpatan((float10)*(float *)(param_1 + 0x18),(float10)*(float *)(param_1 + 0x28))
    ;
    *(undefined4 *)(param_1 + 0x60) = 0;
    *(float *)(param_1 + 0x44) = (float)-fVar4;
  }
  *(undefined4 *)(param_1 + 0x4c) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0;
  *(undefined4 *)((int)this + 0x260) = 0x40800000;
  if ((*(int *)(param_1 + 0x3bc) != 0) && (*(int *)(*(int *)(param_1 + 0x3bc) + 0x100) == 1)) {
    *(undefined4 *)((int)this + 0x260) = 0x3f800000;
  }
  CGroundUnit__Init(param_1);
  local_1c = (void *)0x0;
  local_18 = 0;
  local_14 = 0;
  (**(code **)(*(int *)this + 0x70))(&local_1c);
  pvVar5 = (void *)0x3;
  (**(code **)(*(int *)this + 0xf0))(3,1,0);
  *(undefined4 *)((int)this + 300) = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 0xb8);
  *(undefined4 *)((int)this + 0x130) = 0;
  *(undefined4 *)((int)this + 0x134) = 0;
  uVar1 = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 200);
  *(undefined4 *)((int)this + 0x100) = uVar1;
  *(undefined4 *)((int)this + 0x104) = uVar1;
  *(undefined4 *)((int)this + 0x108) = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 0xd0);
  puStack_c = (undefined4 *)
              OID__AllocObject(0x48,0x17,s_C__dev_ONSLAUGHT2_Infantry_cpp_0062d4a8,0x46);
  local_14 = 2;
  if (puStack_c == (undefined4 *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = CInfantryGuide__ctor_like_0048a3c0(puStack_c,this,pvVar5);
  }
  local_14 = 0xffffffff;
  *(int *)((int)this + 0x208) = iVar3;
  puVar2 = (undefined4 *)OID__AllocObject(0x60,0x16,s_C__dev_ONSLAUGHT2_Infantry_cpp_0062d4a8,0x47);
  local_14 = 3;
  if (puVar2 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    puStack_c = puVar2;
    CWarspite__Init(this,param_1);
    *puVar2 = &PTR_LAB_005dbf14;
    puVar2[5] = 0;
  }
  *(undefined4 **)((int)this + 0x13c) = puVar2;
  *(undefined4 *)((int)this + 0x268) = 0;
  *(undefined4 *)((int)this + 0x26c) = 0;
  ExceptionList = local_1c;
  return;
}
