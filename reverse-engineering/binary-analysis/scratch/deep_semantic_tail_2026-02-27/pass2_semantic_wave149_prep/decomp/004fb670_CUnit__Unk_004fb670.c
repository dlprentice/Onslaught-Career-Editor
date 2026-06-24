/* address: 0x004fb670 */
/* name: CUnit__Unk_004fb670 */
/* signature: int __thiscall CUnit__Unk_004fb670(void * this, int param_1, int param_2) */


int __thiscall CUnit__Unk_004fb670(void *this,int param_1,int param_2)

{
  int iVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  double dVar5;

  if (param_1 == 0) {
    return 2;
  }
  fVar2 = *(float *)(param_1 + 0x1c) - *(float *)((int)this + 0x1c);
  fVar3 = *(float *)(param_1 + 0x20) - *(float *)((int)this + 0x20);
  fVar4 = *(float *)(param_1 + 0x24) - *(float *)((int)this + 0x24);
  fVar2 = SQRT(fVar2 * fVar2 + fVar4 * fVar4 + fVar3 * fVar3);
  if (*(void **)((int)this + 0x140) == (void *)0x0) {
    if (*(int *)((int)this + 0x144) == 0) {
      return 2;
    }
    iVar1 = *(int *)(*(int *)((int)this + 0x144) + 0x3d0);
    if (fVar2 < *(float *)(iVar1 + 0x2c)) {
      return 2;
    }
    if (*(float *)(iVar1 + 0x30) < fVar2) {
      return 1;
    }
  }
  else {
    dVar5 = CUnit__Helper_005096a0
                      (*(void **)((int)this + 0x140),*(void **)(param_1 + 0x1c),
                       *(float *)(param_1 + 0x20),*(float *)(param_1 + 0x24),
                       *(float *)(param_1 + 0x28));
    if ((double)fVar2 < dVar5) {
      return 2;
    }
    dVar5 = CUnit__Helper_005099a0
                      (*(void **)((int)this + 0x140),*(void **)(param_1 + 0x1c),
                       *(float *)(param_1 + 0x20),*(float *)(param_1 + 0x24),
                       *(float *)(param_1 + 0x28));
    if (dVar5 < (double)fVar2) {
      return 1;
    }
  }
  return 0;
}
