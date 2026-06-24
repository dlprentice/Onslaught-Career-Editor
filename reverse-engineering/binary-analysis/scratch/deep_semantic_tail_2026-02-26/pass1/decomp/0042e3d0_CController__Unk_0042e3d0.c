/* address: 0x0042e3d0 */
/* name: CController__Unk_0042e3d0 */
/* signature: double __thiscall CController__Unk_0042e3d0(void * this, void * param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CController__Unk_0042e3d0(void *this,void *param_1,int param_2,int param_3)

{
  int iVar1;
  float10 fVar2;

  switch(param_2) {
  case -6:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x38))(param_1);
    break;
  case -5:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x34))(param_1);
    break;
  case -4:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x30))(param_1);
    break;
  case -3:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x2c))(param_1);
    break;
  case -2:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x28))(param_1);
    break;
  case -1:
    fVar2 = (float10)(**(code **)(*(int *)this + 0x24))(param_1);
    break;
  default:
    iVar1 = (**(code **)(*(int *)this + 0x10))(param_1,param_2);
    if (iVar1 != 0) {
      return (double)_DAT_005d8568;
    }
    goto LAB_0042e473;
  }
  if (fVar2 < (float10)_DAT_005d97d0) {
    return (double)((fVar2 + (float10)_DAT_005d8568) * (float10)_DAT_005d97cc -
                   (float10)_DAT_005d8568);
  }
  if ((float10)_DAT_005d8588 < fVar2) {
    return (double)((float10)_DAT_005d8568 -
                   ((float10)_DAT_005d8568 - fVar2) * (float10)_DAT_005d97cc);
  }
LAB_0042e473:
  return (double)_DAT_005d856c;
}
