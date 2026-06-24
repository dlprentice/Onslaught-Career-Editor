/* address: 0x004e5c90 */
/* name: CUnit__Unk_004e5c90 */
/* signature: int __thiscall CUnit__Unk_004e5c90(void * this, void * param_1, int param_2) */


int __thiscall CUnit__Unk_004e5c90(void *this,void *param_1,int param_2)

{
  int *piVar1;

  piVar1 = *(int **)this;
  for (; (piVar1 != (int *)0x0 && (0 < (int)param_1)); param_1 = (void *)((int)param_1 + -1)) {
    piVar1 = (int *)piVar1[1];
  }
  return *piVar1;
}
