/* address: 0x004725f0 */
/* name: CGame__Unk_004725f0 */
/* signature: int __thiscall CGame__Unk_004725f0(void * this, int param_1, int param_2) */


int __thiscall CGame__Unk_004725f0(void *this,int param_1,int param_2)

{
  if (param_1 == 1) {
    return *(int *)((int)this + 0x290);
  }
  if (param_1 == 2) {
    return *(int *)((int)this + 0x294);
  }
  return 0;
}
