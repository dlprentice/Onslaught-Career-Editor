/* address: 0x004e6680 */
/* name: CUnit__Unk_004e6680 */
/* signature: int __thiscall CUnit__Unk_004e6680(void * this, int param_1, int param_2) */


int __thiscall CUnit__Unk_004e6680(void *this,int param_1,int param_2)

{
  int iVar1;

  if (param_1 == 0) {
    if ((*(int *)((int)this + 0x7c) != 1) && (*(int *)((int)this + 0x7c) != 6)) {
      return 0;
    }
  }
  else {
    if (param_1 == 1) {
      if (*(int *)((int)this + 0x7c) == 0) {
        return 1;
      }
      iVar1 = *(int *)((int)this + 0x7c) + -6;
    }
    else {
      if (param_1 != 6) {
        return 0;
      }
      iVar1 = *(int *)((int)this + 0x7c);
      if (iVar1 == 1) {
        return 1;
      }
    }
    if (iVar1 != 0) {
      return 0;
    }
  }
  return 1;
}
