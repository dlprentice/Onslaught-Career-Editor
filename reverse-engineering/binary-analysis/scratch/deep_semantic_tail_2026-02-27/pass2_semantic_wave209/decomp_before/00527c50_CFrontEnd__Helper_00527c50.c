/* address: 0x00527c50 */
/* name: CFrontEnd__Helper_00527c50 */
/* signature: int __thiscall CFrontEnd__Helper_00527c50(void * this, int param_1, void * param_2) */


int __thiscall CFrontEnd__Helper_00527c50(void *this,int param_1,void *param_2)

{
  uint in_EAX;
  undefined4 extraout_EAX;

  if (*(int *)((int)this + 8) == 1) {
    *(undefined4 *)((int)this + 8) = 2;
  }
  else if (*(int *)((int)this + 8) == 3) {
    CController__RelinquishControl((void *)param_1);
    *(undefined4 *)((int)this + 8) = 0;
    return CONCAT31((int3)((uint)extraout_EAX >> 8),1);
  }
  return in_EAX & 0xffffff00;
}
