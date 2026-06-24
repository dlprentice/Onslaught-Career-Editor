/* address: 0x004cb920 */
/* name: CParticleManager__UpdateParticleAndRecycleIfDead */
/* signature: void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CParticleManager__UpdateParticleAndRecycleIfDead(void *this,void *param_1,int param_2)

{
  uint uVar1;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;

  if (_DAT_005d8be0 < *(float *)((int)param_1 + 0x60)) {
    *(float *)((int)param_1 + 0x60) = *(float *)((int)param_1 + 0x60) - DAT_009c63f8;
  }
  Vec3__SetXYZ();
  *(float *)((int)param_1 + 0x38) = local_10 + *(float *)((int)param_1 + 0x38);
  *(float *)((int)param_1 + 0x3c) = local_c + *(float *)((int)param_1 + 0x3c);
  *(float *)((int)param_1 + 0x40) = local_8 + *(float *)((int)param_1 + 0x40);
  if (*(int *)((int)param_1 + 0x58) != 0) {
    *(undefined4 *)(*(int *)((int)param_1 + 0x58) + 0xa4) = 1;
    *(void **)(*(int *)((int)param_1 + 0x58) + 0xa8) = param_1;
  }
  if (((DAT_009c63fc == 0) || (*(float *)((int)param_1 + 0x60) <= _DAT_005d95c0)) ||
     (_DAT_005d856c <= *(float *)((int)param_1 + 0x60))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  *(uint *)((int)param_1 + 100) = *(uint *)((int)param_1 + 100) | uVar1;
  (**(code **)(**(int **)((int)param_1 + 0x5c) + 0x28))(param_1);
  if (*(int *)((int)param_1 + 100) != 0) {
    if (*(int *)((int)param_1 + 0x6c) == 0) {
      *(undefined4 *)this = *(undefined4 *)((int)param_1 + 0x68);
    }
    else {
      *(undefined4 *)(*(int *)((int)param_1 + 0x6c) + 0x68) = *(undefined4 *)((int)param_1 + 0x68);
    }
    if (*(int *)((int)param_1 + 0x68) != 0) {
      *(undefined4 *)(*(int *)((int)param_1 + 0x68) + 0x6c) = *(undefined4 *)((int)param_1 + 0x6c);
    }
    CParticle__Destroy();
    *(undefined4 *)((int)param_1 + 0x68) = *(undefined4 *)((int)this + 8);
    *(void **)((int)this + 8) = param_1;
  }
  return;
}
