/* address: 0x0044cd20 */
/* name: CUnitAI__Unk_0044cd20 */
/* signature: void __thiscall CUnitAI__Unk_0044cd20(void * this, void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnitAI__Unk_0044cd20(void *this,void *param_1,float param_2)

{
  float fVar1;

  if (*(int *)(*(int *)((int)this + 0xe4) + 0x10) == 0) {
    fVar1 = *(float *)((int)this + 0xe0) - (float)param_1;
    *(float *)((int)this + 0xe0) = fVar1;
    if ((fVar1 < _DAT_005d856c) && ((*(byte *)((int)this + 0x2c) & 4) == 0)) {
      (**(code **)(*(int *)this + 200))();
    }
    if (*(float *)(*(int *)((int)this + 0xe4) + 0x18) < *(float *)((int)this + 0xe0)) {
      *(undefined4 *)((int)this + 0xe0) = *(undefined4 *)(*(int *)((int)this + 0xe4) + 0x18);
    }
  }
  return;
}
