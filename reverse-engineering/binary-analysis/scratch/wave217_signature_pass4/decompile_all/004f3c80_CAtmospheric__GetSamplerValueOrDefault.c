/* address: 0x004f3c80 */
/* name: CAtmospheric__GetSamplerValueOrDefault */
/* signature: double __thiscall CAtmospheric__GetSamplerValueOrDefault(void * this, int sampler_id, int default_index, int mode_flags) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
CAtmospheric__GetSamplerValueOrDefault(void *this,int sampler_id,int default_index,int mode_flags)

{
  float10 fVar1;

  if (*(int **)((int)this + 0x30) != (int *)0x0) {
    fVar1 = (float10)(**(code **)(**(int **)((int)this + 0x30) + 0x38))(sampler_id,default_index);
    return (double)fVar1;
  }
  return (double)_DAT_005d856c;
}
