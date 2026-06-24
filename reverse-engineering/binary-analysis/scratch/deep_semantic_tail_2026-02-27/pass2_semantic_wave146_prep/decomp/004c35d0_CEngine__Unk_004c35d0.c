/* address: 0x004c35d0 */
/* name: CEngine__Unk_004c35d0 */
/* signature: void __thiscall CEngine__Unk_004c35d0(void * this, int param_1, int param_2) */


void __thiscall CEngine__Unk_004c35d0(void *this,int param_1,int param_2)

{
  float *pfVar1;
  undefined4 *puVar2;
  int iVar3;
  int local_8;

  if (*(int *)((int)this + 0x90) == 0) {
    *(undefined4 *)(param_1 + 0x80) = *(undefined4 *)((int)this + 0x68);
  }
  else {
    pfVar1 = *(float **)(param_1 + 0x58);
    if (pfVar1 == (float *)0x0) {
      return;
    }
    if (*(int *)((int)this + 0xa0) == 0) {
      *(undefined4 *)(param_1 + 0x80) = *(undefined4 *)((int)this + 0x68);
    }
    else {
      local_8 = (int)(longlong)
                     ROUND(SQRT((*pfVar1 - pfVar1[0x24]) * (*pfVar1 - pfVar1[0x24]) +
                                (pfVar1[1] - pfVar1[0x25]) * (pfVar1[1] - pfVar1[0x25]) +
                                (pfVar1[2] - pfVar1[0x26]) * (pfVar1[2] - pfVar1[0x26])) /
                           *(float *)((int)this + 0xa4));
      *(int *)(param_1 + 0x80) = local_8 + 3;
    }
  }
  CParticleManager__SetParticleResource(*(int *)(param_1 + 0x80) * 0x28);
  iVar3 = 0;
  if (0 < *(int *)(param_1 + 0x80)) {
    puVar2 = (undefined4 *)(*(int *)(param_1 + 0x88) + 0x20);
    do {
      puVar2[1] = 0;
      *puVar2 = 0x3e4ccccd;
      iVar3 = iVar3 + 1;
      puVar2 = puVar2 + 10;
    } while (iVar3 < *(int *)(param_1 + 0x80));
  }
  return;
}
