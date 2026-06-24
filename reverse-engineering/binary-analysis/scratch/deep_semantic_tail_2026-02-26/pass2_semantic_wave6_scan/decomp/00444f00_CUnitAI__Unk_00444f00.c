/* address: 0x00444f00 */
/* name: CUnitAI__Unk_00444f00 */
/* signature: int __thiscall CUnitAI__Unk_00444f00(void * this, int param_1, int param_2) */


int __thiscall CUnitAI__Unk_00444f00(void *this,int param_1,int param_2)

{
  int *piVar1;
  int iVar2;

  piVar1 = *(int **)(*(int *)((int)this + 4) + param_1 * 4);
  if (piVar1 == (int *)0x0) {
    return 0;
  }
  iVar2 = (**(code **)(*piVar1 + 0x10))();
  return iVar2;
}
