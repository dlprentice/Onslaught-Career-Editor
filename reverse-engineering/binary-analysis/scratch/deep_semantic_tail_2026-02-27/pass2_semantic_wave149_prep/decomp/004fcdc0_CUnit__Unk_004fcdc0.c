/* address: 0x004fcdc0 */
/* name: CUnit__Unk_004fcdc0 */
/* signature: void __thiscall CUnit__Unk_004fcdc0(void * this, int param_1, uint param_2) */


void __thiscall CUnit__Unk_004fcdc0(void *this,int param_1,uint param_2)

{
  if ((*(int *)((int)this + 0x164) != 0) && (*(int *)(*(int *)((int)this + 0x164) + 0x104) != 0)) {
    *(uint *)((int)this + 0x34) = param_1 | 0x80200013;
    return;
  }
  *(uint *)((int)this + 0x34) = param_1 | 0x80000013;
  return;
}
