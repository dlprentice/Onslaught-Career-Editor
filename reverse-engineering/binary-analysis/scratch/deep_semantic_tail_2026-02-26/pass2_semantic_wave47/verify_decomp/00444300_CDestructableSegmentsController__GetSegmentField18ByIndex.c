/* address: 0x00444300 */
/* name: CDestructableSegmentsController__GetSegmentField18ByIndex */
/* signature: double __thiscall CDestructableSegmentsController__GetSegmentField18ByIndex(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
CDestructableSegmentsController__GetSegmentField18ByIndex(void *this,int param_1,int param_2)

{
  int iVar1;

  if ((param_1 != -1) && (iVar1 = *(int *)(*(int *)((int)this + 4) + param_1 * 4), iVar1 != 0)) {
    return (double)*(float *)(iVar1 + 0x18);
  }
  return (double)_DAT_005d856c;
}
