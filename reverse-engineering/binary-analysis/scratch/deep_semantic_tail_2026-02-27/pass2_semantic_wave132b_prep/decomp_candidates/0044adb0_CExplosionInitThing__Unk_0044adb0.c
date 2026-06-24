/* address: 0x0044adb0 */
/* name: CExplosionInitThing__Unk_0044adb0 */
/* signature: float * __thiscall CExplosionInitThing__Unk_0044adb0(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float * __thiscall CExplosionInitThing__Unk_0044adb0(void *this,void *param_1,int param_2)

{
  float10 extraout_ST0;
  float10 fVar1;

  OID__Helper_0055dcb0();
  fVar1 = (float10)_DAT_005d85e8;
  *(float *)((int)this + 4) = (float)extraout_ST0;
  if ((extraout_ST0 < fVar1) && ((float10)_DAT_005d85dc < extraout_ST0)) {
    fVar1 = (float10)fpatan(-(float10)*(float *)((int)param_1 + 4),
                            (float10)*(float *)((int)param_1 + 0x14));
    *(float *)this = (float)fVar1;
    fVar1 = (float10)fpatan(-(float10)*(float *)((int)param_1 + 0x20),
                            (float10)*(float *)((int)param_1 + 0x28));
    *(float *)((int)this + 8) = (float)fVar1;
    return this;
  }
  *(undefined4 *)this = 0;
  *(undefined4 *)((int)this + 8) = 0;
  return this;
}
