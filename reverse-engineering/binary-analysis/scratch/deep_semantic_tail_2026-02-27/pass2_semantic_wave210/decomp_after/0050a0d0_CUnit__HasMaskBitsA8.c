/* address: 0x0050a0d0 */
/* name: CUnit__HasMaskBitsA8 */
/* signature: uint __thiscall CUnit__HasMaskBitsA8(void * this, int param_1, uint param_2) */


uint __thiscall CUnit__HasMaskBitsA8(void *this,int param_1,uint param_2)

{
  return *(uint *)((int)this + 0xa8) & param_1;
}
