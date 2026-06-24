/* address: 0x00480c90 */
/* name: CHLCollisionDetector__HandleCollisionEnter */
/* signature: void __thiscall CHLCollisionDetector__HandleCollisionEnter(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CHLCollisionDetector__HandleCollisionEnter(void *this,int param_1,void *param_2)

{
  int *piVar1;
  float fVar2;
  int iVar3;
  void *pvVar4;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  float fStack_14;
  float fStack_10;
  float fStack_c;

  DAT_0067a540 = DAT_0067a540 + 1;
  iVar3 = *(int *)(*(int *)((int)this + 8) + 8);
  if (*(int *)(iVar3 + 0x18) == -1) {
    iVar3 = 0;
  }
  else {
    iVar3 = iVar3 + 0xc;
  }
  pvVar4 = (void *)(iVar3 + 8);
  iVar3 = (**(code **)(*(int *)param_1 + 0x28))();
  if (1 < iVar3) goto LAB_00480ccb;
  CUnitAI__Helper_004f3ac0(*(void **)(param_1 + 8),(int)&fStack_24,pvVar4);
  CUnitAI__Helper_004f3ac0(*(void **)(*(int *)((int)this + 8) + 8),(int)&fStack_14,pvVar4);
  piVar1 = *(int **)((int)this + 8);
  fVar2 = (float)piVar1[7] + *(float *)(param_1 + 0x1c);
  if (((fStack_24 - fStack_14) * (fStack_24 - fStack_14) +
      (fStack_1c - fStack_c) * (fStack_1c - fStack_c) +
      (fStack_20 - fStack_10) * (fStack_20 - fStack_10)) - fVar2 * fVar2 < (float)_DAT_005d87b0) {
    if (((piVar1[3] & 0x100U) != 0) || ((*(uint *)(param_1 + 0xc) & 0x100) != 0)) {
      iVar3 = (**(code **)(*piVar1 + 0x20))(param_1);
      if (iVar3 == 0) {
LAB_00480ccb:
        *(undefined4 *)((int)this + 0x10) = 1;
        return;
      }
      iVar3 = (**(code **)(*(int *)param_1 + 0x20))(*(undefined4 *)((int)this + 8));
      if (iVar3 == 0) goto LAB_00480ccb;
    }
    (**(code **)(**(int **)((int)this + 8) + 0x18))(param_1);
  }
  *(undefined4 *)((int)this + 0x10) = 1;
  CUnitAI__Helper_00480ed0(this,(void *)param_1,pvVar4);
  return;
}
