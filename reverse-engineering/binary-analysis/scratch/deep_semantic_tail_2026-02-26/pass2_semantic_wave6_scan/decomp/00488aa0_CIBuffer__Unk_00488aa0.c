/* address: 0x00488aa0 */
/* name: CIBuffer__Unk_00488aa0 */
/* signature: double __thiscall CIBuffer__Unk_00488aa0(void * this, int param_1, int param_2) */


double __thiscall CIBuffer__Unk_00488aa0(void *this,int param_1,int param_2)

{
  int iVar1;

  iVar1 = (**(code **)(*(int *)(param_1 + 8) + 0x6c))();
  return (double)*(float *)(*(int *)((int)this + 0x3c) + 0x10 + iVar1 * 0x18);
}
