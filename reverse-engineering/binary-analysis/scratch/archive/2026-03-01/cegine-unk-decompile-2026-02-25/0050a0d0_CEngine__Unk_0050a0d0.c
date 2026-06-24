/* address: 0x0050a0d0 */
/* name: CEngine__Unk_0050a0d0 */
/* signature: uint __thiscall CEngine__Unk_0050a0d0(void * this, int param_1, uint param_2) */


uint __thiscall CEngine__Unk_0050a0d0(void *this,int param_1,uint param_2)

{
  return *(uint *)((int)this + 0xa8) & param_1;
}
