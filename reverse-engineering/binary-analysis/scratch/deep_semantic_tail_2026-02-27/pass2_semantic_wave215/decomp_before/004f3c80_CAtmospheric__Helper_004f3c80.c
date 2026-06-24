/* address: 0x004f3c80 */
/* name: CAtmospheric__Helper_004f3c80 */
/* signature: double __thiscall CAtmospheric__Helper_004f3c80(void * this, int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CAtmospheric__Helper_004f3c80(void *this,int param_1,int param_2,int param_3)

{
  float10 fVar1;

  if (*(int **)((int)this + 0x30) != (int *)0x0) {
    fVar1 = (float10)(**(code **)(**(int **)((int)this + 0x30) + 0x38))(param_1,param_2);
    return (double)fVar1;
  }
  return (double)_DAT_005d856c;
}
