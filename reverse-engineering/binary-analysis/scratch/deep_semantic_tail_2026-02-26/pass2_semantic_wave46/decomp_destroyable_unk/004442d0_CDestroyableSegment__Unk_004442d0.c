/* address: 0x004442d0 */
/* name: CDestroyableSegment__Unk_004442d0 */
/* signature: double __thiscall CDestroyableSegment__Unk_004442d0(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CDestroyableSegment__Unk_004442d0(void *this,int param_1,int param_2)

{
  int iVar1;

  if ((param_1 != -1) && (iVar1 = *(int *)(*(int *)((int)this + 4) + param_1 * 4), iVar1 != 0)) {
    return (double)*(float *)(iVar1 + 0x14);
  }
  return (double)_DAT_005d8be0;
}
