/* address: 0x00528b00 */
/* name: CEngine__InvokeCallbackIfStateMinusOne */
/* signature: void __thiscall CEngine__InvokeCallbackIfStateMinusOne(void * this, void * param_1, int param_2) */


void __thiscall CEngine__InvokeCallbackIfStateMinusOne(void *this,void *param_1,int param_2)

{
  if (*(int *)((int)this + 0xc) == -1) {
    (*(code *)**(undefined4 **)this)((float)(int)param_1);
  }
  return;
}
