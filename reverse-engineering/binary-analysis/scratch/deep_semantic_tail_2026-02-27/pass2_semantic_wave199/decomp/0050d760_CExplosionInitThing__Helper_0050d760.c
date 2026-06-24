/* address: 0x0050d760 */
/* name: CExplosionInitThing__Helper_0050d760 */
/* signature: double __thiscall CExplosionInitThing__Helper_0050d760(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CExplosionInitThing__Helper_0050d760(void *this,int param_1,int param_2)

{
  float fVar1;

  if (*(int *)((int)this + param_1 * 4 + 0x20c) == 3) {
    fVar1 = *(float *)((int)this + param_1 * 4 + 0x23c) - DAT_00672fd0;
    if (fVar1 < _DAT_005d856c) {
      return (double)_DAT_005d856c;
    }
  }
  else {
    fVar1 = *(float *)((int)this + param_1 * 4 + 0x23c);
  }
  return (double)fVar1;
}
